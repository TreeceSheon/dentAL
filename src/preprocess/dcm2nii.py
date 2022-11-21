import SimpleITK as sitk
import os
import nibabel
import numpy as np


def read_img(in_path):

    file_name = os.listdir(in_path)[0]
    reader = sitk.ImageFileReader()
    reader.SetFileName(in_path + '/' + file_name)
    reader.ReadImageInformation()
    series_ID = reader.GetMetaData('0020|000e')
    sorted_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(in_path, series_ID)
    dcm_obj = sitk.ReadImage(sorted_file_names)
    voxel_size = dcm_obj.GetSpacing()
    return np.array(sitk.GetArrayFromImage(dcm_obj)).squeeze(), voxel_size


def write_img(vol, out_path, ref_path, new_spacing=None):
    img_ref = sitk.ReadImage(ref_path)
    img = sitk.GetImageFromArray(vol)
    img.SetDirection(img_ref.GetDirection())
    if new_spacing is None:
        img.SetSpacing(img_ref.GetSpacing())
    else:
        img.SetSpacing(tuple(new_spacing))
    img.SetOrigin(img_ref.GetOrigin())
    sitk.WriteImage(img, out_path)
    print('Save to:', out_path)


def search_CT_by_iter_path(path_itr, root_save_path, count):

    while True:

        try:
            path = path_itr.__next__()
            if path.is_dir():

                if path.name in ['ct', 'CT']:

                    print(path / '\n')
                    save_path = root_save_path / path.parts[-2]
                    save_path.mkdir(exist_ok=True)

                    while True:

                        try:

                            dcm2nii(path, save_path)
                            break
                        except Exception as e:

                            print(e)

                            command = input(
                                "please handle the issue before resuming the converting. Retry: 0, skip: 1, abort: 2")

                            if command == 1:
                                break

                            elif command == 2:
                                exit(-1)

                    count += 1

                    return count

                else:

                    count = search_CT_by_iter_path(path.iterdir(), root_save_path, count)

        except StopIteration:

            break

    return count


def dcm2nii(dcm_path, save_path):

    ct_volume, vox_size = read_img(str(dcm_path))

    volume_arr = np.array(ct_volume)

    nibabel.save(nibabel.Nifti1Image(volume_arr.transpose([1, 2, 0]), np.diag([*vox_size, 1])),
                 str(save_path) + '/CT.nii')


def batch_dcm_to_nii(search_path, save_path):

    itr = search_path.iterdir()

    count = search_CT_by_iter_path(itr, save_path, 0)

    print("successfully convert " + str(count) + " dicom volumes to nifti files.")
