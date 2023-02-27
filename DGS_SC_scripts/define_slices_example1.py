import numpy as np
from matplotlib.colors import LogNorm

def define_data_slices(extra=''):
    dsl=[]
    for E in np.arange(0,2,0.5):
        dE=0.05
        description={'QDimension0':'1,0,0',
                     'QDimension1':'0,1,0',
                     'QDimension2':'0,0,1',
                     'Dimension0Name':'QDimension1',
                     'Dimension0Binning':'-2.,0.025,2.',
                     'Dimension1Name':'QDimension2',
                     'Dimension1Binning':'-2.5,0.025,2.5',
                     'Dimension2Name':'QDimension0',
                     'Dimension2Binning':'-0.2,0.2',
                     'Dimension3Name':'DeltaE',
                     'Dimension3Binning':'{},{}'.format(E-dE,E+dE),
                     #'SymmetryOperations':'P 4/nmm',
                     #'SymmetryOperations':'x,y,z;-x,y,z;x,y,-z;-x,y,-z',
                     'ConvertToChi':False,
                     'Plot_parameters':{'norm':LogNorm()},#vmin=1e-4,vmax=1e-1
                     'Axes_parameters':{'xrange':None,'yrange':None, 'xtitle':None, 'ytitle':None, 'title':'CNCS E=[{},{}]meV'.format(E-dE,E+dE), 'aspect_ratio':None, 'tight_axes':True, 'grid':True},
                     'Name':'KL_slice_{0:.1f}meV_noBG_subtraction'.format(E)+extra}
        dsl.append(description)
    K=[-2.,2.]
    description={'QDimension0':'1,0,0',
                 'QDimension1':'0,1,0',
                 'QDimension2':'0,0,1',
                 'Dimension0Name':'QDimension2',
                 'Dimension0Binning':'-2.5,0.025,2.5',
                 'Dimension1Name':'DeltaE',
                 'Dimension1Binning':'-0.5,0.025,3.25',
                 'Dimension2Name':'QDimension0',
                 'Dimension2Binning':'-0.2,0.2',
                 'Dimension3Name':'QDimension1',
                 'Dimension3Binning':'{},{}'.format(K[0],K[1]),
                  #'SymmetryOperations':'P 4/nmm',
                  #'SymmetryOperations':'x,y,z;-x,y,z;x,y,-z;-x,y,-z',
                 'ConvertToChi':False,
                 'Plot_parameters':{'norm':LogNorm()},#vmin=1e-4,vmax=1e-1
                 'Axes_parameters':{'xrange':None,'yrange':None, 'xtitle':None, 'ytitle':None, 'title':'CNCS E=[{},{}]meV'.format(E-dE,E+dE), 'aspect_ratio':None, 'tight_axes':True, 'grid':True},
                 'Name':'LE_slice_noBG_subtraction K=[{},{}]'.format(K[0],K[1])+extra}
    dsl.append(description)

    return dsl


