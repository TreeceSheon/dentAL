from torch.utils.data import Dataset
import torch
import nibabel as nib
import numpy as np
import torch.nn.functional as F
from skimage.measure import regionprops


def get_ids(file_path):
    f = open(file_path, 'r')
    ids = []
    for line in f:
        ids.append(line.strip("\n"))
    return ids


def skew(vector):
    """
    skew-symmetric operator for rotation matrix generation
    """

    return np.array([[0, -vector[2], vector[1]],
                     [vector[2], 0, -vector[0]],
                     [-vector[1], vector[0], 0]])


def get_rotation_mat(ori1, ori2):
    """
    generating pythonic style rotation matrix
    :param ori1: your current orientation
    :param ori2: orientation to be rotated
    :return: pythonic rotation matrix.
    """
    ori1 = ori1.numpy()
    ori2 = ori2.squeeze().numpy()
    v = np.cross(ori1, ori2)
    c = np.dot(ori1, ori2)
    mat = np.identity(3) + skew(v) + np.matmul(skew(v), skew(v)) / (1 + c)
    return torch.from_numpy(np.flip(mat).copy()).float()


class ImplantDataset(Dataset):

    def __init__(self, file_path, root_path, device=torch.device('cuda')):

        super(ImplantDataset, self).__init__()

        self.ids = get_ids(file_path)
        self.entries = []
        self.device = device

        for idx, name in enumerate(self.ids):

            fields = name.split(' ')

            self.entries.append({
                'oral': root_path / fields[0] / 'missing_teeth_patches96' / ('CT_' + fields[1] + '.nii'),
                'implant': root_path / fields[0] / 'missing_teeth_patches96' / (fields[1] + '.nii')
            })

    def implant_augmentation(self, implant):

        implant = implant.unsqueeze(0)
        orientation = F.normalize(torch.rand([1, 3]))
        rot_mat = get_rotation_mat(torch.tensor([0, 0, 1]), orientation)
        pure_translate = torch.rand([3, 1])
        affine_matrix = torch.cat([rot_mat.to(self.device), pure_translate], dim=1).unsqueeze(0)
        grid = F.affine_grid(affine_matrix, implant.shape, align_corners=False)
        return F.grid_sample(input=implant, grid=grid, mode='bilinear'), orientation, pure_translate

    def __getitem__(self, index):
        pair = self.entries[index]
        print(str(pair['implant']))

        label_implant = torch.from_numpy(nib.load(str(pair['implant'])).get_fdata()[np.newaxis]).to(self.device, torch.float)
        while True:
            try:
                input_implant, ori, pure_trans = self.implant_augmentation(label_implant)
                rp = regionprops(input_implant.squeeze().cpu().numpy().astype(np.int8))[0]
                break
            except IndexError:
                continue

        centroid = rp.centroid
        bbox = rp.bbox
        position = torch.tensor([*centroid, *bbox]).to(self.device, torch.float)
        oral = torch.from_numpy(nib.load(str(pair['oral'])).get_fdata()[np.newaxis]).to(self.device, torch.float)
        return input_implant.squeeze(0), oral, label_implant, position, ori, pure_trans

    def __len__(self):
        return len(self.entries)
