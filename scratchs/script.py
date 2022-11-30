import numpy
import torch
from stl import mesh
from utils.handy import save_array_as_nii
from stl.main import to_ascii, to_binary
import matplotlib.pyplot as plt


your_mesh = mesh.Mesh.from_file("/Volumes/Samsung_T5/data/dentAL/rawdata/data/Single/upper/jingdegang/implant_26.stl")
plt.plot(your_mesh)

grid = numpy.array(your_mesh)

min_value = 100
aaa = []
aaa.extend(grid[:, 0].tolist())
aaa.extend(grid[:, 3].tolist())
aaa.extend(grid[:, 7].tolist())
aaa.sort()
img = numpy.zeros([547, 547, 651])

vox_size = 0.1
centroid = your_mesh.get_mass_properties()[1] // vox_size


for (x1, y1, z1, x2, y2, z2, x3, y3, z3) in grid:

    x1, y1, z1, x2, y2, z2, x3, y3, z3 = x1 / vox_size, y1 / vox_size, z1 / vox_size, x2 / vox_size, y2 / vox_size, z2 / vox_size, x3 / vox_size, y3 / vox_size, z3 / vox_size
    img[round(centroid[0] + x1), round(centroid[1] + y1), round(centroid[2] + z1)] = 1
    img[round(centroid[0] + x2), round(centroid[1] + y2), round(centroid[2] + z2)] = 1
    img[round(centroid[0] + x3), round(centroid[1] + y3), round(centroid[2] + z3)] = 1

save_array_as_nii(img, 'implant')
