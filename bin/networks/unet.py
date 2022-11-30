import torch
import torch.nn as nn
import torch.nn.functional as F


class Unet(nn.Module):

    class Encoder(nn.Module):

        def __init__(self, in_channel, out_channel):
            super(Unet.Encoder, self).__init__()
            self._input = nn.Sequential(
                nn.Conv3d(in_channel, out_channel, 3, 1, 1),
                nn.BatchNorm3d(out_channel),
                nn.ReLU()
            )
            self._output = nn.Sequential(
                nn.Conv3d(out_channel, out_channel, 3, 1, 1),
                nn.BatchNorm3d(out_channel),
                nn.ReLU()
            )

        def forward(self, feature_map):
            mid = self._input(feature_map)
            res = self._output(mid)
            return res

    class Decoder(nn.Module):

        def __init__(self, in_channel, out_channel):
            super(Unet.Decoder, self).__init__()
            self._input = nn.Sequential(
                nn.ConvTranspose3d(in_channel, out_channel, 2, stride=2),
                nn.BatchNorm3d(out_channel),
                nn.ReLU()
            )
            self._mid = nn.Sequential(
                nn.Conv3d(out_channel, out_channel, 3, 1, 1),
                nn.BatchNorm3d(out_channel),
                nn.ReLU()
            )
            self._output = nn.Sequential(
                nn.Conv3d(out_channel, out_channel, 3, 1, 1),
                nn.BatchNorm3d(out_channel),
                nn.ReLU()
            )

        def forward(self, feature_map):
            x = self._input(feature_map)
            mid = self._mid(x)
            res = self._output(mid)
            return res

    def __init__(self, depth, base, init=1):
        super(Unet, self).__init__()
        self.depth = depth
        self._input = Unet.Encoder(init, base)
        self._encoders = nn.ModuleList([nn.Sequential(nn.MaxPool3d(2),
                                        Unet.Encoder(base * 2 ** i, base * 2 ** (i + 1)))
                                        for i in range(depth)])
        self._decoders = nn.ModuleList([Unet.Decoder(base * 2 ** i, base * 2 ** (i - 1))
                                        for i in range(depth, 0, -1)])

        self._output = nn.Sequential(
            nn.Linear(12 * 12 * 12, 1024),
            nn.Linear(1024, 16)
        )

    def forward(self, x):

        inEncoder = self._input(x)

        for encoder in self._encoders:
            inEncoder = encoder(inEncoder)

        #
        # for decoder in self._decoders:
        #     inDecoder = decoder(inDecoder)

        return self._output(inEncoder)


class RegistrationModel(nn.Module):

    def __init__(self, depth, base):

        super(RegistrationModel, self).__init__()

        self.encoder = Encoder(depth, base)

        self.decoder = RegistrationDecoder(channel=base * 8, length=16)

    def forward(self, shift, fixed):

        embed1 = self.encoder(shift)
        embed2 = self.encoder(fixed)

        return self.decoder(embed1, embed2)


class RegistrationDecoder(nn.Module):

    def __init__(self, channel=16, length=32, embeding_size=32):

        super(RegistrationDecoder, self).__init__()

        self.q = nn.Linear(length, embeding_size)

        self.k = nn.Linear(length, embeding_size)

        self.v = nn.Linear(length, embeding_size)

        self.dropout = nn.Dropout(0.2)

        self.proj = nn.Sequential(
            nn.Linear(channel * embeding_size, channel * 3),
            nn.ReLU(),
            nn.Linear(channel * 3, 3)
        )

    def forward(self, embed1, embed2):

        query = self.q(embed1) * self.q(embed2)
        key = self.k(embed1) * self.k(embed2)
        value = self.v(embed1) * self.v(embed2)

        attn = (F.normalize(query, dim=-1) @ F.normalize(key, dim=-1).transpose(-2, -1))
        attn = F.softmax(attn)
        attn = self.dropout(attn)
        attn = torch.matmul(attn.transpose(1, 2), value)

        embed = self.proj(attn.view(attn.shape[0], -1))

        return F.normalize(embed)

    @staticmethod
    def get_rotation_mat(ori2):
        """
        generating pythonic style rotation matrix
        :param ori1: your current orientation
        :param ori2: orientation to be rotated
        :return: pythonic rotation matrix.
        """
        device = ori2.device
        ori1 = torch.tensor([0, 0, 1]).float().to(device).unsqueeze(0).repeat(ori2.shape[0], 1)
        v = torch.cross(ori1, ori2, dim=1)
        c = torch.sum(ori1 * ori2, dim=1).unsqueeze(1).unsqueeze(1)
        mat = torch.eye(3).unsqueeze(0).repeat(ori2.shape[0], 1, 1).to(device) + RegistrationDecoder.skew(v) + torch.matmul(RegistrationDecoder.skew(v),
                                                                                                        RegistrationDecoder.skew(v)) / (
                          1 + c)
        return mat

    @staticmethod
    def skew(vector):
        """
        skew-symmetric operator for rotation matrix generation
        """
        b = vector.shape[0]
        device = vector.device
        skew_mat = torch.zeros([b, 3, 3]).to(device)

        skew_mat[:, 0, 1] = -vector[:, 2]
        skew_mat[:, 0, 2] = -vector[:, 1]
        skew_mat[:, 1, 0] = vector[:, 2]
        skew_mat[:, 1, 2] = -vector[:, 0]
        skew_mat[:, 2, 0] = -vector[:, 1]
        skew_mat[:, 2, 1] = vector[:, 0]

        return skew_mat


class Encoder(nn.Module):

    def __init__(self, depth, base):
        super(Encoder, self).__init__()
        self.depth = depth
        self._input = Unet.Encoder(1, base)
        self._encoders = nn.ModuleList([nn.Sequential(nn.MaxPool3d(2),
                                        Unet.Encoder(base * 2 ** i, base * 2 ** (i + 1)))
                                        for i in range(depth)])
        self._output = nn.Sequential(
            nn.Linear(depth * depth * depth * 4 ** 3, 1024),
            nn.Linear(1024, 16)
        )

    def forward(self, x):

        inEncoder = self._input(x)

        for encoder in self._encoders:
            inEncoder = encoder(inEncoder)

        b, c, _, _, _ = inEncoder.shape
        return self._output(inEncoder.view(b, c, -1))


