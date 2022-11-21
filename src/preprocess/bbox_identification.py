import numpy as np
from scipy.ndimage import zoom
from skimage.measure import regionprops


class RegionProposal:

    def __init__(self, arr, scaling_factor=2):

        arr = arr.astype(np.int16)
        arr_downsample = zoom(arr, [1/scaling_factor, 1/scaling_factor, 1/scaling_factor])
        region = regionprops(arr_downsample)[0]

        self.bbx = tuple((ele * scaling_factor for ele in region.bbox))
        self.centroid = tuple((int(ele * scaling_factor) for ele in region.centroid))
        self.area = region.area * scaling_factor
        self.label = region.label


def get_region_bbx(arr):

    return RegionProposal(arr).bbx


def get_region_centroid(arr):

    return RegionProposal(arr).centroid
