import torch
from torch.utils.data import DataLoader
from implant_dataset import ImplantDataset
from pathlib import Path
from bin.networks.auto_unet import ImplantRegistrationNetwork
import torch.nn.functional as F
from utils.handy import *
from skimage.measure import regionprops


def implant_registration(affine, input_implant):
    grid = F.affine_grid(affine, input_implant.shape, align_corners=False)

    return F.grid_sample(input=input_implant, grid=grid)


implant = torch_from_nib_path("H:\\data\\dentAL\\nifti\\chenheping\\missing_teeth_patches96\\implant_21.nii").cpu()
oral = torch_from_nib_path("H:\\data\\dentAL\\nifti\\chenheping\\missing_teeth_patches96\\CT_implant_21.nii").cpu()

rot = get_rotation_mat([0, 0, 1], [0.5, 0.5, 0.7071]).cpu()

affine_implant = affine_transformation(implant, rot).cpu()

rp = regionprops(affine_implant.squeeze().numpy().astype(np.int8))[0]

pos = torch.tensor([*rp.centroid, *rp.bbox]).unsqueeze(0)

model = ImplantRegistrationNetwork(16)

with torch.no_grad():
    model(oral, pos.float())