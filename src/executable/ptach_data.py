from src.preprocess import batch_dcm_to_nii, get_region_centroid
from pathlib import Path
import nibabel as nib
from utils import save_array_as_nii
from scipy.ndimage import zoom

PATCH_SIZE = 96
PS = PATCH_SIZE

# convert dicom to nifti

# data_path = Path('H:\\data\\dentAL\\nifti\\mengxiaojun')
save_path = Path('H:\\data\\dentAL\\nifti')

# batch_dcm_to_nii(data_path, save_path)


# patch generating

def patching_with_centroid(centroid, patch_size, volume, scale=1):

    patch_border = list(range(3))

    volume = zoom(volume, (1/scale, 1/scale, 1/scale))

    for dim in range(3):

        start = centroid[dim] - patch_size // 2 if patch_size // 2 < centroid[dim] else 0

        end = start + patch_size

        end = min(end, volume.shape[dim])

        start = end - patch_size

        patch_border[dim] = (start, end)

    return volume[patch_border[0][0]: patch_border[0][1],
           patch_border[1][0]: patch_border[1][1], patch_border[2][0]: patch_border[2][1]]


itr = save_path.iterdir()
patient_count = 0

for patient in itr:

    implants = {}
    volume = None

    for nii in patient.iterdir():

        if nii.name.upper().startswith('IMPLANT'):

            implants[str(nii.name.split('.')[0])] = nib.load(str(nii)).get_fdata()

        elif nii.name.upper().startswith('CT'):

            volume = nib.load(str(nii)).get_fdata()

            volume = (volume - volume.min()) / (volume.max() - volume.min())

    if volume is None:

        raise AttributeError('CT for ' + str(patient) + 'not found')

    print(patient)
    patient_count += 1

    with open('list.txt', 'a') as f:

        for (name, implant) in implants.items():

            print(name)

            centroid = get_region_centroid(implant)

            volume_patch = patching_with_centroid(centroid, PS, volume, scale=2)
            implant_patch = patching_with_centroid(centroid, PS, implant)

            if volume_patch.shape != [96, 96, 96]:
                pass
            if implant_patch.shape != [96, 96, 96]:
                pass
            save_folder = patient / ('missing_teeth_patches' + str(PS))

            save_folder.mkdir(exist_ok=True)

            save_array_as_nii(volume_patch, str(save_folder / ('CT_' + name.lower())))
            save_array_as_nii(implant_patch, str(save_folder / name.lower()))

            f.write(patient.name + ' ' + name.lower() + '\n')

        print(str(patient_count) + '\n')


# patch CT




