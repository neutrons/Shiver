import matplotlib.pyplot as plt
from mantid import plots
from reduce_data_to_MDE import *
from slice_utils import *
import define_data_example
import define_slices_example


#############################################
# MAIN PROGRAM
#############################################
datasets=define_data_example.define_data_set()
ds=datasets[0]
reduce_data_to_MDE([ds])

slice_descriptions=define_slices_example.define_data_slices()

slice_description=slice_descriptions[0] #take only one slice
make_slice(ds,slice_description, solid_angle_ws=None, ASCII_slice_folder='')
fig,ax=plt.subplots(subplot_kw={'projection':'mantid'})
c=plot_slice(slice_description, ax=ax, cbar_label='Intensity')
set_axes_parameters(ax,**slice_description['Axes_parameters'])
fig.show()
