import torch
from torch.utils.data import DataLoader
from implant_dataset import ImplantDataset
from pathlib import Path
from bin.networks.auto_unet import ImplantRegistrationNetwork
import torch.nn.functional as F

device = torch.device('cpu')
dataset = ImplantDataset('H:\\dentAL\\bin\\dataset\\list.txt', Path('H:\\data\\dentAL\\nifti'), device)
loader = DataLoader(dataset, batch_size=2, drop_last=True)

model = ImplantRegistrationNetwork(16).to(device)

optim = torch.optim.Adam(model.parameters(), lr=1e-5)

crit = torch.nn.MSELoss(reduction='sum')


def implant_registration(affine, input_implant):

    grid = F.affine_grid(affine, input_implant.shape, align_corners=False)

    return F.grid_sample(input=input_implant, grid=grid)


for epoch in range(1, 500):

    for idx, values in enumerate(loader):

        optim.zero_grad()

        input_implant, oral, label_implant, position, ori, pure_trans = values

        affine_matrix = model(oral, position)

        implant_registered = implant_registration(affine_matrix, input_implant)

        loss = crit(implant_registered, label_implant)

        print(loss)



