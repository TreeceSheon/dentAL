import torch
import torch.nn as nn


class AbstractImplantRegistrationNet(nn.Module):

    def __init__(self):

        super(AbstractImplantRegistrationNet, self).__init__()

        self.encoder = None
        self.decoder = None

    def save(self, name):

        torch.save(self.encoder.state_dict(), name)

    def forward(self, *args):

        raise NotImplementedError


class ImplantRegstSequentialNet(AbstractImplantRegistrationNet):

    """
    take sequential representation of an implant to predict the orientation of corresponding implant.
    """

    def __init__(self):

        super(ImplantRegstSequentialNet, self).__init__()

    def forward(self, seq):

        """
        :param seq: [[bbox*6], [centroid*3], [length, radius]]
        """

