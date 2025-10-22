import os
import sys

sys.path.append('/opt/Mantid/bin')
sys.path.append('/opt/Mantid/lib')
from imp import reload

import define_data_IPTS_21819
import define_slices_IPTS_21819
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reduce_data_to_MDE import *
from slice_utils import *

#############################################################################################################################
# MAIN PROGRAM
# Makes set of slices described by define_slices dictionaries from the set of data mde described by define_data dictionaries
# Authors: A. Savici, I. Zaliznyak, March 2019. Last revision: August 2019.
#############################################################################################################################

# Define the list of data set descriptions and load the combined mde workspaces (make if needed)
reload(define_data_IPTS_21819)
datasets=define_data_IPTS_21819.define_data_set()
reduce_data_to_MDE(datasets)

ds_SFPx=[ds for ds in datasets if ds['PolarizationState']=='SF_Px'][0]        #Choose SF dataset to slice
ds_NSFPx=[ds for ds in datasets if ds['PolarizationState']=='NSF_Px'][0]      #Choose NSF dataset to slice

# Create output folders
slice_folder=os.path.join(ds_SFPx['MdeFolder'],'Slices')
try:
    os.makedirs(slice_folder)
except:
    pass
ASCII_slice_folder=os.path.join(slice_folder,'ASCII')
try:
    os.makedirs(ASCII_slice_folder)
except:
    pass

pdf_filename = os.path.join(slice_folder,'Ruby_3p8meV_1p6K_Px.pdf')
with PdfPages(pdf_filename) as pdf_handle:
    #get slice definitions
    reload(define_slices_IPTS_21819)
    slice_descriptions=define_slices_IPTS_21819.define_data_slices(extra='_Ruby_3p8meV_180Hz_1p6K_Px')

    #on each page plot the flipping ratio corrected SF and NSF data
    for slice_description in slice_descriptions:
        slice_name=slice_description['Name']
        make_slices_FR_corrected(slice_description,ds_SFPx,ds_NSFPx, solid_angle_ws=None, ASCII_slice_folder=ASCII_slice_folder, MD_slice_folder='')
        SF_workspace_name=slice_name+'_SF_FRcorr'
        NSF_workspace_name=slice_name+'_NSF_FRcorr'

        fig,ax=plt.subplots(nrows=2, ncols=1, sharex=True, subplot_kw={'projection':'mantid'})

        c=ax[0].pcolormesh(mtd[SF_workspace_name],**slice_description['Plot_parameters'])
        set_axes_parameters(ax[0],**slice_description['Axes_parameters'])
        ax[0].set_title(slice_description['Axes_parameters']['title']+' SF FR {0} corr'.format(ds_SFPx['FlippingRatio']))
        if c:
            cbar=fig.colorbar(c, ax=ax[0])
            cbar.set_label('Intensity (arb. units)') #add text to colorbar
        ax[0].set(adjustable='box-forced',anchor='C')

        c=ax[1].pcolormesh(mtd[NSF_workspace_name],**slice_description['Plot_parameters'])
        set_axes_parameters(ax[1],**slice_description['Axes_parameters'])
        ax[1].set_title(slice_description['Axes_parameters']['title']+' NSF FR {0} corr'.format(ds_NSFPx['FlippingRatio']))
        if c:
            cbar=fig.colorbar(c, ax=ax[1])
            cbar.set_label('Intensity (arb. units)') #add text to colorbar
        ax[1].set(adjustable='box-forced',anchor='C')

        pdf_handle.savefig(fig)
plt.close('all')

