import numpy as np
from matplotlib.colors import LogNorm

########################################################################################################
# Define list of dictionaries, describing slices to be histogrammed and plotted from an mde workspace 
# Authors: A. Savici, I. Zaliznyak, March 2019. Last revision: August 2019.
########################################################################################################
def define_data_slices(extra=''):
    T=''
    if extra:
        #assumes temperature is after the last _
        T=extra.split('_')[-1].replace('p','.')

    dsl=[]

    dl=0.05
    for l in np.arange(0.77,1.25,0.46):
        description={'QDimension0':'0,1,0',
                     'QDimension1':'0,0,1',
                     'QDimension2':'1,0,0',
                     'Dimension0Name':'QDimension0',
                     'Dimension0Binning':'-0.5,0.035,0.5',
                     'Dimension1Name':'DeltaE',
                     'Dimension1Binning':'-0.2,0.035,2.4',
                     'Dimension2Name':'QDimension2',
                     'Dimension2Binning':'-0.15,0.15',
                     'Dimension3Name':'QDimension1',
                     'Dimension3Binning':'{},{}'.format(l-dl,l+dl),                   
                     #'SymmetryOperations':'P21/c monoclinic 14',
                     'SymmetryOperations':'x,y,z;-x,-y,-z',
                     'Smoothing':1,
                     #'Plot_parameters':{'norm':LogNorm(vmin=1e-4,vmax=1e-1)},
                     'Plot_parameters':{'vmin':1e-5,'vmax':1e-3},
                     'Axes_parameters':{'xrange':None,
                                        'yrange':None, 
                                        'xtitle':None, 
                                        'ytitle':None, 
                                        'title':'HYSPEC L=[{},{}] T={}'.format(l-dl,l+dl,T), 
                                        'aspect_ratio':None, 
                                        'tight_axes':True},
                     'Name':'KE_slice_L{0:.2f}to{1:0.2f}'.format(l-dl,l+dl)+extra}
        dsl.append(description)

    return dsl


