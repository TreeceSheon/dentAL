# -*- coding: utf-8 -*-
"""01_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OWXPL8K-jKC4KgGmYXXkeBWOL2V1biuf

# Setup
"""
import math

import torch
import torch.nn.functional as F
import torch.nn as nn

H = 160
W = 192
D = 128


def conv_block(c_in, c_out, ks, num_groups=None, actv=nn.ReLU, **conv_kwargs):
    "A sequence of modules composed of Group Norm, ReLU and Conv3d in order"
    if not num_groups: num_groups = int(c_in / 2) if c_in % 2 == 0 else None
    return nn.Sequential(nn.BatchNorm3d(c_in),
                         actv(),
                         nn.Conv3d(c_in, c_out, ks, **conv_kwargs))


def reslike_block(nf, num_groups=None, bottle_neck: bool = False, actv=nn.ReLU, **conv_kwargs):
    "A ResNet-like block with the GroupNorm normalization providing optional bottle-neck functionality"
    nf_inner = nf / 2 if bottle_neck else nf
    return nn.Sequential(
        conv_block(num_groups=num_groups, c_in=nf, c_out=nf_inner, ks=3, stride=1, padding=1, actv=actv, **conv_kwargs))
    # conv_block(num_groups=num_groups, c_in=nf_inner, c_out=nf, ks=3, stride=1, padding=1, actv=actv, **conv_kwargs))


def upsize(c_in, c_out, ks=1, scale=2):
    "Reduce the number of features by 2 using Conv with kernel size 1x1x1 and double the spatial dimension using 3D trilinear upsampling"
    return nn.Sequential(nn.Conv3d(c_in, c_out, ks),
                         nn.Upsample(scale_factor=scale, mode='trilinear', align_corners=True))


def skew(vector):
    """
    skew-symmetric operator for rotation matrix generation
    """
    b = vector.shape[0]

    skew_mat = torch.zeros([b, 3, 3])

    skew_mat[:, 0, 1] = -vector[:, 2]
    skew_mat[:, 0, 2] = -vector[:, 1]
    skew_mat[:, 1, 0] = vector[:, 2]
    skew_mat[:, 1, 2] = -vector[:, 0]
    skew_mat[:, 2, 0] = -vector[:, 1]
    skew_mat[:, 2, 1] = vector[:, 0]

    return skew_mat


def get_rotation_mat(ori2):
    """
    generating pythonic style rotation matrix
    :param ori1: your current orientation
    :param ori2: orientation to be rotated
    :return: pythonic rotation matrix.
    """
    ori1 = torch.tensor([0, 0, 1]).float().to(ori2.device).unsqueeze(0).repeat(ori2.shape[0], 1)
    v = torch.cross(ori1, ori2, dim=1)
    c = torch.sum(ori1 * ori2, dim=1).unsqueeze(1).unsqueeze(1)
    mat = torch.eye(3).unsqueeze(0).repeat(ori2.shape[0], 1, 1) + skew(v) + torch.matmul(skew(v), skew(v)) / (1 + c)

    return mat


class ImplantRegistrationNetwork(nn.Module):
    "Encoder part"

    def __init__(self, base):
        super().__init__()

        self.element_wise_mlp = nn.Sequential(
            nn.Linear(12 * 12 * 12, 3),
            nn.LeakyReLU(negative_slope=0.2)
        )
        self.channel_wise_mlp = nn.Sequential(
            nn.Linear(128 + 32, 2),
            nn.LeakyReLU(negative_slope=0.2)
        )
        self.encoder = Encoder(base)
        self.implant_embedding = ImplantEmbedding()

    def forward(self, x, position):
        """
        :param x:
        :param position: (shift, c1, c2, c3, b1, b2, b3, b4, b5, b6)
        :return:
        """
        x = self.encoder(x)

        b, c = x.shape[:2]

        pos_embedding = self.implant_embedding(position)

        embedding = self.element_wise_mlp(x.view([b, c, -1]))

        embedding = torch.cat([embedding.permute([0, 2, 1]), pos_embedding], dim=2)

        embedding = self.channel_wise_mlp(embedding).permute([0, 2, 1])

        orientation = F.normalize(embedding[:, 0, :], p=2, dim=1)

        rot_mat = get_rotation_mat(orientation)

        translation = embedding[:, 1, :]
        # translation = torch.tensor([0, 0, 1]).unsqueeze(0).repeat([b, 1])

        return torch.cat([rot_mat, translation.unsqueeze(-1)], dim=2)


class ImplantEmbedding(nn.Module):

    def __init__(self, length=32):
        super(ImplantEmbedding, self).__init__()
        self.alpha = nn.Parameter(torch.rand([9]))
        self.beta = nn.Parameter(torch.rand([9]))

        self.position_embedding = nn.Linear(9, length * 3)
        self.actv = nn.Tanh()
        self.output = nn.Linear(length * 3, 6)

    def forward(self, position):
        position = torch.sin(self.beta * 2 * math.pi * position) + torch.cos(self.beta * 2 * math.pi * position)

        pos_embedding = self.position_embedding(position)

        embedding = self.actv(pos_embedding)

        return self.output(embedding).reshape(-1, 2, 3)


class Encoder(nn.Module):

    def __init__(self, base):
        super(Encoder, self).__init__()

        self.conv1 = nn.Conv3d(1, base, 3, stride=1, padding=1)

        self.res_block1 = reslike_block(base, num_groups=8)
        self.conv_block1 = conv_block(base, base * 2, 3, num_groups=8, stride=2, padding=1)

        self.res_block2 = reslike_block(base * 2, num_groups=8)
        self.conv_block3 = conv_block(base * 2, base * 4, 3, num_groups=8, stride=2, padding=1)

        self.res_block4 = reslike_block(base * 4, num_groups=8)
        self.conv_block5 = conv_block(base * 4, base * 8, 3, num_groups=8, stride=2, padding=1)

        self.res_block6 = reslike_block(base * 8, num_groups=8)
        self.conv_block7 = conv_block(base * 8, base * 8, 3, num_groups=8, stride=1, padding=1)

        self.res_block8 = reslike_block(base * 8, num_groups=8)

    def forward(self, x):
        x = self.conv1(x)  # Output size: (1, 32, 160, 192, 128)
        skip = self.res_block1(x)  # Output size: (1, 32, 160, 192, 128)

        x = self.conv_block1(x + skip)  # Output size: (1, 64, 80, 96, 64)
        skip = self.res_block2(x)  # Output size: (1, 64, 80, 96, 64)

        x = self.conv_block3(x + skip)  # Output size: (1, 128, 40, 48, 32)
        skip = self.res_block4(x)  # Output size: (1, 128, 40, 48, 32)

        x = self.conv_block5(x + skip)  # Output size: (1, 256, 20, 24, 16)
        skip = self.res_block6(x)  # Output size: (1, 256, 20, 24, 16)

        x = self.conv_block7(x + skip)  # Output size: (1, 256, 20, 24, 16)
        skip = self.res_block8(x)  # Output size: (1, 256, 20, 24, 16)

        return x + skip


if __name__ == '__main__':
    model = ImplantRegistrationNetwork(16)
    implant_embedding_model = ImplantEmbedding()
    img = torch.rand([4, 1, 96, 96, 96])
    implant = torch.rand([4, 1, 96, 96, 96])
    label = torch.rand([4, 1, 96, 96, 96])
    position = torch.rand([4, 9])

    affine_matrix = model(img, position)

    grid = F.affine_grid(affine_matrix, img.shape, align_corners=False)

    pred = F.grid_sample(input=implant, grid=grid)

    loss = torch.sum(label - pred)

    loss.backward()




