from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot

filename = '/Volumes/Samsung_T5/data/dentAL/rawdata/data/Single/upper/xurongnan/implant_23.stl'

# Create a new plot
figure = pyplot.figure()
axes = figure.gca(projection='3d')

# Load the STL files and add the vectors to the plot
mesh = mesh.Mesh.from_file(filename)

axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.vectors, color='lightgrey'))
#axes.plot_surface(mesh.x,mesh.y,mesh.z)
# Auto scale to the mesh size
scale = mesh.points.flatten()
axes.auto_scale_xyz(scale, scale, scale)

#turn off grid and axis from display
pyplot.axis('on')

#set viewing angle
axes.view_init(azim=120)

# Show the plot to the screen
pyplot.show()