import os
from mantid.simpleapi import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy.optimize import curve_fit
from mantid.plots.datafunctions import *
from mantid import plots
import mantid

########################################################################################################
# Utilities to make and plot a slice (histogram) from the reduced data described by data_set dictionary  
# using slice descriptions defined in the list of dictionaries provided by define_data_slices(extra='')
# Authors: A. Savici, I. Zaliznyak, March 2019.
# Revised June 2020, by Ovi to work with python 3.x (has_key('') --> in)
########################################################################################################
def make_slice(data_set,slice_description, solid_angle_ws=None, ASCII_slice_folder='', MD_slice_folder=''):
    slice_name=slice_description['Name'].strip()
    mde_name=data_set['MdeName'].strip()
    UB_dict=data_set.get('UBSetup')
    mdnorm_parameters={'InputWorkspace': mde_name,
                       'OutputWorkspace': slice_name,
                       'OutputDataWorkspace':'_data',
                       'OutputNormalizationWorkspace':'_norm'}
    # Load normalization file from dataset description, if needed
    try:
        norm_file=data_set['NormalizationDataFile'].strip()
    except:
        norm_file=None
    if norm_file:
        norm_ws_name=os.path.split(norm_file)[-1]
        if not mtd.doesExist(norm_ws_name):
            print('Loading normalization and masking file '+norm_file)
            Load(norm_file,OutputWorkspace=norm_ws_name)
        mdnorm_parameters['SolidAngleWorkspace']=norm_ws_name
    if solid_angle_ws:
        mdnorm_parameters['SolidAngleWorkspace']=solid_angle_ws
    for par_name in ['QDimension0','QDimension1','QDimension2','Dimension0Name','Dimension0Binning',
                     'Dimension1Name','Dimension1Binning','Dimension2Name','Dimension2Binning',
                     'Dimension3Name','Dimension3Binning','SymmetryOperations']:
        if par_name in slice_description:
            mdnorm_parameters[par_name]=slice_description[par_name]

    # transform to chi''
    is_chi = slice_description.get('ConvertToChi',False)

    temperature=0.
    if is_chi:
        try:
            temperature=data_set['SampleLogVariables']['Temperature']
        except:
            raise ValueError("For calculating chi'' one needs to set the temperature in the dataset definition. See example.")
        if not mtd.doesExist(mde_name+'_chi'):
            ApplyDetailedBalanceMD(InputWorkspace=mde_name, Temperature=str(data_set['SampleLogVariables']['Temperature']), OutputWorkspace=mde_name+'_chi')
        mdnorm_parameters['InputWorkspace']=mde_name+'_chi'

    bg_type=None
    bg_mde_name=data_set.get("BackgroundMdeName")
    if bg_mde_name is not None:
        bg_mde_name=bg_mde_name.strip()
    if bg_mde_name:
        if not mtd.doesExist(bg_mde_name):
            bg_mde_filename=os.path.join(data_set['MdeFolder'],bg_mde_name+'.nxs')
            try:
                print(bg_mde_name+'background MDE specified in data set is not loaded: try loading from '+bg_mde_filename)
                LoadMD(bg_mde_filename,OutputWorkspace=data_mde_name, LoadHistory=False)
            except:
                raise ValueError('BG MDE not found: please run the reduction on BG runs to make the BG MDE '+bg_mde_name)
        if is_chi:
            if not mtd.doesExist(bg_mde_name+'_chi'):
                ApplyDetailedBalanceMD(InputWorkspace=bg_mde_name, Temperature=str(data_set['SampleLogVariables']['Temperature']), OutputWorkspace=bg_mde_name+'_chi')
            bg_mde_name+='_chi'

        if mtd[bg_mde_name].getSpecialCoordinateSystem()==mantid.kernel.SpecialCoordinateSystem.QLab:
            mdnorm_parameters['BackgroundWorkspace'] = bg_mde_name
            mdnorm_parameters['OutputBackgroundDataWorkspace'] = '_bkg_data'
            mdnorm_parameters['OutputBackgroundNormalizationWorkspace'] = '_bkg_norm'
        elif mtd[bg_mde_name].getSpecialCoordinateSystem()==mantid.kernel.SpecialCoordinateSystem.QSample:
            mdnorm_bkg_parameters=mdnorm_parameters.copy()
            mdnorm_bkg_parameters['InputWorkspace']= bg_mde_name
            mdnorm_bkg_parameters['OutputWorkspace']= '_bkg'
            mdnorm_bkg_parameters['OutputDataWorkspace']='_bkg_data'
            mdnorm_bkg_parameters['OutputNormalizationWorkspace']='_bkg_norm'
            bg_type='sample'
            MDNorm(**mdnorm_bkg_parameters)
            
    MDNorm(**mdnorm_parameters)

    SmoothingFWHM=slice_description.get("Smoothing")
    if SmoothingFWHM:
        SmoothMD(InputWorkspace='_data', 
                 WidthVector=SmoothingFWHM,
                 Function='Gaussian',
                 InputNormalizationWorkspace='_norm',
                 OutputWorkspace='_data')
        SmoothMD(InputWorkspace='_norm', 
                 WidthVector=SmoothingFWHM,
                 Function='Gaussian',
                 InputNormalizationWorkspace='_norm',
                 OutputWorkspace='_norm')
        DivideMD(LHSWorkspace='_data', RHSWorkspace='_norm', OutputWorkspace=slice_name)
        if bg_mde_name:
            SmoothMD(InputWorkspace='_bkg_data',
                     WidthVector=SmoothingFWHM,
                     Function='Gaussian',
                     InputNormalizationWorkspace='_bkg_norm',
                     OutputWorkspace='_bkg_data')
            SmoothMD(InputWorkspace='_bkg_norm',
                     WidthVector=SmoothingFWHM,
                     Function='Gaussian',
                     InputNormalizationWorkspace='_bkg_norm',
                     OutputWorkspace='_bkg_norm')
            DivideMD(LHSWorkspace='_bkg_data', RHSWorkspace='_bkg_norm', OutputWorkspace='_bkg')

            MinusMD(LHSWorkspace=slice_name,RHSWorkspace='_bkg', OutputWorkspace=slice_name)
    elif bg_type=='sample': # there is background from multi-angle
        MinusMD(LHSWorkspace=slice_name,RHSWorkspace='_bkg', OutputWorkspace=slice_name)

    if ASCII_slice_folder:
        filename=os.path.join(ASCII_slice_folder,slice_name+'.txt')
        IgnoreIntegrated=False
        SaveMDToAscii(mtd[slice_name],filename,IgnoreIntegrated,NumEvNorm=False,Format='%.6e')
    if MD_slice_folder:
        filename=os.path.join(MD_slice_folder,slice_name+'.nxs')
        SaveMD(InputWorkspace=slice_name, Filename=filename)
    return slice_name


def make_slices_FR_corrected(slice_description,data_set_SF,data_set_NSF, solid_angle_ws=None, ASCII_slice_folder='', MD_slice_folder=''):
    # Obtain flipping ratio from SF dataset description
    FR_ds=data_set_SF['FlippingRatio']
    if FR_ds is None:
        raise ValueError('Flipping ratio is not defined')
    try:
        FR=float(FR_ds)
        FR=str(FR)
        var_names=''
    except:
        FR,var_names=FR_ds.split(',',1)

    mde_SF=mtd[data_set_SF['MdeName'].strip()]
    mde_NSF=mtd[data_set_NSF['MdeName'].strip()]
    SF_F,SF_1=FlippingRatioCorrectionMD(InputWorkspace=mde_SF, FlippingRatio=FR, SampleLogs=var_names)
    NSF_F,NSF_1=FlippingRatioCorrectionMD(InputWorkspace=mde_NSF, FlippingRatio=FR, SampleLogs=var_names)

    slice_name=slice_description['Name']
    slice_description['Name']=slice_name+'_SF_F'
    data_set_SF['MdeName']=SF_F.name()
    make_slice(data_set_SF,slice_description, solid_angle_ws=solid_angle_ws)
    slice_description['Name']=slice_name+'_SF_1'
    data_set_SF['MdeName']=SF_1.name()
    make_slice(data_set_SF,slice_description, solid_angle_ws=solid_angle_ws)
    slice_description['Name']=slice_name+'_NSF_F'
    data_set_NSF['MdeName']=NSF_F.name()
    make_slice(data_set_NSF,slice_description, solid_angle_ws=solid_angle_ws)
    slice_description['Name']=slice_name+'_NSF_1'
    data_set_NSF['MdeName']=NSF_1.name()
    make_slice(data_set_NSF,slice_description, solid_angle_ws=solid_angle_ws)
    slice_description['Name']=slice_name
    data_set_SF['MdeName']=mde_SF.name()
    data_set_NSF['MdeName']=mde_NSF.name()

    MinusMD(LHSWorkspace=slice_name+'_SF_F',RHSWorkspace=slice_name+'_NSF_1', OutputWorkspace=slice_name+'_SF_FRcorr')
    MinusMD(LHSWorkspace=slice_name+'_NSF_F',RHSWorkspace=slice_name+'_SF_1', OutputWorkspace=slice_name+'_NSF_FRcorr')

    if ASCII_slice_folder:
        IgnoreIntegrated=False
        filename=os.path.join(ASCII_slice_folder,slice_name+'_SF_FRcorr.txt')
        SaveMDToAscii(mtd[slice_name+'_SF_FRcorr'],filename,IgnoreIntegrated,NumEvNorm=False,Format='%.6e') 
        filename=os.path.join(ASCII_slice_folder,slice_name+'_NSF_FRcorr.txt')
        SaveMDToAscii(mtd[slice_name+'_NSF_FRcorr'],filename,IgnoreIntegrated,NumEvNorm=False,Format='%.6e') 
    if MD_slice_folder:
        filename=os.path.join(MD_slice_folder,slice_name+'_SF_FRcorr.nxs')
        SaveMD(InputWorkspace=slice_name+'_SF_FRcorr', Filename=filename)
        filename=os.path.join(MD_slice_folder,slice_name+'_NSF_FRcorr.nxs')
        SaveMD(InputWorkspace=slice_name+'_NSF_FRcorr', Filename=filename)


def plot_slice(slice_description, ax=None, cbar_label=None):
    slice_name=slice_description['Name']
    if ax:
        plot_parameters=slice_description.get('Plot_parameters')
        if not plot_parameters:
            plot_parameters={}
        num_dims=len(mtd[slice_name].getNonIntegratedDimensions())
        if num_dims==1:
            slice_plot=ax.errorbar(mtd[slice_name],**plot_parameters)
            return slice_plot
        elif num_dims==2:
            slice_plot=ax.pcolormesh(mtd[slice_name],**plot_parameters)
            if cbar_label is not None:
                cbar=ax.get_figure().colorbar(slice_plot)
                cbar.set_label(cbar_label) #add text to colorbar            
            return slice_plot


def set_axes_parameters(ax,**axes_args):
    try:
        if 'tight_axes' in axes_args and axes_args['tight_axes']!=None:
             ax.autoscale(tight=axes_args['tight_axes'])
    except Error as err:
        print(err)

    try:
        if 'xrange' in axes_args and axes_args['xrange']!=None:
            ax.set_xlim(axes_args['xrange'])
    except Error as err:
        print(err)

    try:
        if 'yrange' in axes_args and axes_args['yrange']!=None:
            ax.set_ylim(axes_args['yrange'])
    except Error as err:
        print(err)

    try:
        if 'xtitle' in axes_args and axes_args['xtitle']!=None:
            ax.set_xlabel(axes_args['xtitle'])
    except Error as err:
        print(err)

    try:
        if 'ytitle' in axes_args and axes_args['ytitle']!=None:
            ax.set_ylabel(axes_args['ytitle'])
    except Error as err:
        print(err)

    try:
        if 'title' in axes_args and axes_args['title']!=None:
            ax.set_title(axes_args['title'])
    except Error as err:
        print(err)

    try:
        if 'aspect_ratio' in axes_args and axes_args['aspect_ratio']!=None:
            ax.set_aspect(axes_args['aspect_ratio'])
    except Error as err:
        print(err)

    try:
        if 'grid' in axes_args and axes_args['grid']!=None:
             ax.grid(axes_args['grid'])
    except Error as err:
        print(err)


def filter_large_error(ws,threshold):
    signal=ws.getSignalArray()*1.0
    error2=ws.getErrorSquaredArray()*1.0
    discard=np.where(np.sqrt(error2)>threshold*signal)
    signal[discard]=np.nan
    error2[discard]=np.nan
    ws.setSignalArray(signal)
    ws.setErrorSquaredArray(error2)


def gauss(x,b,a,c,w):
    s=w/2.355
    y=a*np.exp(-(x-c)**2/(2*s**2))+b
    return(y)


def subtract_incoherent(ws,q_range=None):
    (q,E),data_array,error_array=get_md_data(ws, get_normalization(ws),withError=True)
    q = points_from_boundaries(q)
    E = points_from_boundaries(E)
    if not q_range:
        q_range=[np.min(q),np.max(q)]
    q_to_use=np.where(np.logical_and(q>q_range[0],q<q_range[1]))[0]
    data_to_use=np.mean(data_array[:,q_to_use],axis=1).data
    error2_to_use=np.mean(error_array[:,q_to_use]**2,axis=1).data
    w=0.3
    c=-0.1
    a=np.max(data_to_use)
    b=0.0
    tofit=np.where(E<5)[0]
    params,_=curve_fit(gauss,E[tofit],data_to_use[tofit],[b,a,c,w],np.sqrt(error2_to_use[tofit]))
    fitted=gauss(E,0.0,params[1],params[2],params[3])
    fig,ax=plt.subplots()
    ax.errorbar(E,data_to_use,yerr=np.sqrt(error2_to_use),fmt='ko')
    ax.plot(E,gauss(E,params[0],params[1],params[2],params[3]))
    fig.show()
    ws.setSignalArray(ws.getSignalArray()-np.tile(fitted,q.shape).reshape(ws.getSignalArray().shape))


def dim2array(d,center=True):
    """
    Create a numpy array containing bin centers along the dimension d
    input: d - IMDDimension
    return: numpy array, from min+st/2 to max-st/2 with step st  
    """
    dmin=d.getMinimum()
    dmax=d.getMaximum()
    dstep=d.getX(1)-d.getX(0)
    if center:
        return np.arange(dmin+dstep/2,dmax,dstep)
    else:
        return np.linspace(dmin,dmax,d.getNBins()+1)

def SaveMDToAscii(ws,filename,IgnoreIntegrated=True,NumEvNorm=False,Format='%.6e'):
    """
    Save an MDHistoToWorkspace to an ascii file (column format)
    input: ws - handle to the workspace
    input: filename - path to the output filename
    input: IgnoreIntegrated - if True, the integrated dimensions are ignored (smaller files), but that information is lost
    input: NumEvNorm - must be set to true if data was converted to MD from a histo workspace (like NXSPE) and no MDNorm... algorithms were used
    input: Format - value to pass to numpy.savetxt
    return: nothing
    """
    if ws.id()!='MDHistoWorkspace':
        raise ValueError("The workspace is not an MDHistoToWorkspace")
    #get dimensions
    if IgnoreIntegrated:
        dims=ws.getNonIntegratedDimensions()
    else:
        dims=[ws.getDimension(i) for i in range(ws.getNumDims())]
    dimarrays=[dim2array(d) for d in dims]
    try:    
        newdimarrays=np.meshgrid(*dimarrays,indexing='ij')
    except:
        newdimarrays=dimarrays #1D arrays
    #get data
    data=ws.getSignalArray()*1.
    err2=ws.getErrorSquaredArray()*1.
    if NumEvNorm:
        nev=ws.getNumEventsArray()
        data/=nev
        err2/=(nev*nev)
    err=np.sqrt(err2)
    #write file
    header="Intensity Error "+" ".join([d.getName() for d in dims])
    header+="\n shape: "+"x".join([str(d.getNBins()) for d in dims])
    toPrint=np.c_[data.flatten(),err.flatten()]
    for d in newdimarrays:
        toPrint=np.c_[toPrint,d.flatten()]
    np.savetxt(filename,toPrint,fmt=Format,header=header)


def slice_des2str(sd,instr=None):
    """
    make a string containing the dictionary parameters that can be put on a plot with the text.
    sd is the slice description dictionary
    instr is an initial string to put before the automatically formatted string.
    """
    outstr=""
    if instr is not None:
        outstr = instr+'\n'
    for ky in sd.keys():
        if (ky !='Axes_parameters') &(ky!='Plot_parameters')& (ky.find('Dimension')<0):
            if sd[ky] is not None:
                outstr+="{}:{}\n".format(ky,sd[ky])
    for idx in range(4):
        Dimnum = 'Dimension{}'.format(idx)
        Dimname = sd[Dimnum+'Name']
        if Dimname.find('QDim')>=0:
            outstr+="{} : {}\n".format(sd[Dimname],sd[Dimnum+'Binning'])
        else:
             outstr+="{} : {}\n".format(Dimname,sd[Dimnum+'Binning'])
    return outstr

def plot_w_parameters(slice_description,ds,
                      sp_kw={'figsize':(10,6),'gridspec_kw':{'width_ratios': [1, 2]}}):
    """
    make a plot with the slice parameters to one side
    slice_description  (required) is a dictionary describing the slice
    ds (required) is the data set
    sp_kw  (optional) is the keywords to pass through to the subplots command that makes the figure window    
    """
    fig,ax=plt.subplots(ncols=2, subplot_kw={'projection':'mantid'}, **sp_kw)
    c=plot_slice(slice_description, ax=ax[1], cbar_label='Intensity')
    set_axes_parameters(ax[1],**slice_description['Axes_parameters'])
    ax[0].text(0.01,0.99,slice_des2str(slice_description,instr=ds['MdeName']),ha='left', va='top')
    ax[0].axis('off')
    return fig,ax

