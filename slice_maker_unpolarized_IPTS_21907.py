import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from mantid.simpleapi import *
from mantid import plots
from reduce_data_to_MDE import *
from slice_utils import *
import define_data_IPTS_21907
import define_slices_IPTS_21907


#############################################
# MAIN PROGRAM
#############################################
# Define the list of data set descriptions and load the combined mde workspaces (make if needed)
reload(define_data_IPTS_21907)
datasets=define_data_IPTS_21907.define_data_set()

for ds in datasets:
    reduce_data_to_MDE([ds])
    slice_folder=os.path.join(ds['MdeFolder'],'Slices')
    ASCII_slice_folder=os.path.join(slice_folder,'ASCII')
    try:
        os.makedirs(slice_folder)
    except:
        pass
    try:
        os.makedirs(ASCII_slice_folder)
    except:
        pass

    # Plot slices into a pdf file
    pdf_filename = os.path.join(slice_folder,ds['MdeName']+'.pdf')

    with PdfPages(pdf_filename) as pdf_handle:
        reload(define_slices_IPTS_21907)
        extra='_'+ds['MdeName']
        slice_descriptions=define_slices_IPTS_21907.define_data_slices(extra=extra)

        for slice_description in slice_descriptions:
            make_slice(ds,slice_description, solid_angle_ws=None, ASCII_slice_folder='')
            fig,ax=plt.subplots(subplot_kw={'projection':'mantid'})
            c=plot_slice(slice_description, ax=ax, cbar_label='Intensity')
            set_axes_parameters(ax,**slice_description['Axes_parameters'])
            pdf_handle.savefig(fig)
            
plt.close('all')

