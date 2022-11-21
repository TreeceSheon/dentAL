import nibabel as nib
import numpy as np

def save_array_as_nii(arr, name):

    return nib.save(nib.Nifti1Image(arr, np.eye(4)), name + '.nii')

