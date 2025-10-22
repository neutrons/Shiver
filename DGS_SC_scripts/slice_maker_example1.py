import sys

import matplotlib.pyplot as plt

sys.path.append('/SNS/groups/dgs/DGS_SC_Scripts')
from imp import reload

import define_data_example
import define_slices_example
from reduce_data_to_MDE import *
from slice_utils import *

#############################################
# MAIN PROGRAM
#############################################
reload(define_data_example)
reload(define_slices_example)
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
