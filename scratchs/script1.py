import numpy as np

from utils.handy import *
import trimesh
from trimesh import voxel

mesh = trimesh.load_mesh('H:\\data\\dentAL\\rawdata\\data\\Single\\upper\\xurongnan\\implant_23.stl')
voxel_size = np.array([0.25, 0.25, 0.25])
mesh_shift = mesh.centroid / voxel_size
shift_y, shift_x, shift_z = mesh_shift[0], mesh_shift[1], mesh_shift[2]
ct_size = np.zeros([639, 639, 419])


def make_coord(shape, flatten=True):
    """
    Make coordinates at grid centers.
    """
    coord_seqs = []
    for i, n in enumerate(shape):
        r = 1 / n
        seq = -1 + r + (2 * r) * torch.arange(n).float()
        coord_seqs.append(seq)
    ret = torch.stack(torch.meshgrid(*coord_seqs), dim=-1)
    if flatten:
        ret = ret.view(-1, ret.shape[-1])
    return ret


coords = make_coord([639, 639, 419])

grid_x = np.linspace(0, ct_size[0], int(ct_size[0] / voxel_size[0]))
grid_y = np.linspace(0, ct_size[1], int(ct_size[1] / voxel_size[1]))
grid_z = np.linspace(0, ct_size[2], int(ct_size[2] / voxel_size[2]))
ct_centroid = ct_size // 2
mesh_centroid_in_voxel = ct_centroid + np.array([shift_x, shift_y, shift_z])
print(mesh_centroid_in_voxel)
# validation

from skimage.measure import regionprops

implant = torch_from_nib_path('/Volumes/Samsung_T5/data/dentAL/rawdata/data/Single/upper/xurongnan/DemoPrjectFolder/implant_23.nii').squeeze().numpy().astype(np.int8)
ctriod = regionprops(implant)[0].centroid
print(ctriod)
