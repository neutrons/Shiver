from __future__ import (absolute_import, division, print_function)
from mantid.simpleapi import *
from mantid.api import MatrixWorkspace
import glob
import numpy
import os
import json
from matplotlib.cbook import flatten

##################################################################################################################
# HYSPEC specfic modules for the data reduction by generate_mde and generate_BG_mde
# Authors: A. Savici, I. Zaliznyak Last revision: August 2019.
##################################################################################################################
def polarizer_transmission(ws,**kwargs):
    '''
    Hyspec polarizer transmission correction. If used it will
    undo the effect of the attenuation as a function of E_final
    '''
    EFixed=ws.run()['Ei'].value
    #DeltaE-Ei=-Ef
    ws=ScaleX(ws,Factor=-EFixed,Operation="Add")
    ws=ExponentialCorrection(ws,C0=1/0.585,C1=1/10.77,Operation="Multiply") #was 58.5% *exp(-Ef/12.07)
    ws=ScaleX(ws,Factor=EFixed,Operation="Add")
    return ws


def detector_geometry_correction(ws,psda=0.):
    '''
    Account for HYSPEC geometry change in polarized mode
    '''
    if (psda):
        run_obj = ws.getRun()
        psr=run_obj['psr'].getStatistics().mean
        offset=psda*(1.-psr/4200.)
        RotateInstrumentComponent(Workspace=ws,ComponentName='Tank',
                                  X=0, Y=1,Z=0,
                                  Angle=offset,RelativeRotation=1)
    return ws


##################################################################################################################
# Reduces raw data from sets of runs specified by list of dictionaries, data_set_list = define_data_set(),
# to corresponding combined mde workspaces, or loads the existing combined mde from a file
# Authors: A. Savici, I. Zaliznyak, March 2019. Last revision: Aug 2021.
##################################################################################################################
def reduce_data_to_MDE(data_set_list,compress_bg_events_tof=0):
    for data_set in data_set_list:
        data_mde_name=data_set['MdeName'].strip()
        fname=os.path.join(data_set['MdeFolder'],data_mde_name+'.nxs')           
        if not mtd.doesExist(data_mde_name):
            try:
                print('Try loading MDE from '+fname)
                LoadMD(fname,OutputWorkspace=data_mde_name, LoadHistory=False)
            except:
                print('Load MDE failed: generating combined MDE '+data_mde_name)
                generate_mde(data_set)
        bg_mde_name=data_set['BackgroundMdeName']
        if bg_mde_name:
            bg_mde_name=bg_mde_name.strip()
        if bg_mde_name or ('BackgroundRuns' in data_set and data_set['BackgroundRuns']):
            fname=os.path.join(data_set['MdeFolder'],bg_mde_name+'.nxs')           
            if not mtd.doesExist(bg_mde_name):
                try:
                    print('Try loading MDE from '+fname)
                    LoadMD(fname,OutputWorkspace=bg_mde_name, LoadHistory=False)
                except:
                    print('Load background MDE failed: generating background MDE '+bg_mde_name)
                    generate_BG_mde(data_set, compress_bg_events_tof)
                bkg_scale = data_set.get('BackgroundScaling', 1)
                if bkg_scale == None:
                    bkg_scale = 1
                if bkg_scale > 0 and bkg_scale != 1:
                    bkg_handle = mtd[bg_mde_name]
                    bkg_handle *= bkg_scale

def Log_removal(data_set,dgs_data):
    """
       function to remove Logs:
       data_set is the dictionary describing the data set
            for log removal to work data_set['Log_Removal]
            must be a one item dictionary with the key being either 'keep' or 'discard'
            Then the value is a list of log names.  In the keep case only logs in the list are kept.  All others are discarded.
            in the discard case each log in the list is discarded.
       dgs_data is the handle to the workspace to have the logs modified
    """
    if isinstance(data_set['Log_Removal'],dict):
        lr_keys = list(data_set['Log_Removal'].keys())
        if len(lr_keys)==1:
            if lr_keys[0] == 'keep':
                # here is where to add code to be sure to keep logs that are in the dictionary data_set['SampleLogVariables']
                lgs2keep = data_set['Log_Removal']['keep']
                RemoveLogs(dgs_data, KeepLogs=lgs2keep)
            
            if lr_keys[0] == 'discard':
                DeleteLogs(dgs_data,'Name')

        else:
            raise RuntimeError("The dictionary must have only 1 key that is either 'keep' or 'discard' ")
def tib_win(tib_window,inst_name,Ei):
    #Time independent BG subtraction
    tib = [None,None]
    perform_tib=False
    if tib_window is not None:
        perform_tib=True
        if tib_window is 'Default':
            #HYSPEC specific:
            if inst_name == 'HYSPEC':
                if Ei==15:
                    tib=[22000.,23000.]
                else:
                    tib = SuggestTibHYSPEC(Ei)
            #CNCS specific:
            elif inst_name == 'CNCS':
                tib = SuggestTibCNCS(Ei)
            #No tib defaults for other instruments:
            else:
                perform_tib=False
        else:
            tib=tib_window
    return tib, perform_tib
def set_parameters(data_set):

    UB_dict = data_set.get('UBSetup')
    Ei_supplied = data_set.get('Ei')
    T0_supplied = data_set.get('T0')
    bad_pulses_threshold = data_set.get('BadPulsesThreshold')
    tib_window = data_set.get('TimeIndepBackgroundWindow')
    
    emin = data_set.get('E_min')
    emax = data_set.get('E_max')
    additional_dimensions = data_set.get('AdditionalDimensions')

    #Polarized data options
    polarization_state = data_set.get('PolarizationState')  #Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
    flipping_ratio = data_set.get('FlippingRatio')          #Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
    psda = data_set.get('PolarizingSupermirrorDeflectionAdjustment') #Options:None;deflection_angle
    Ef_correction_function = data_set.get('EfCorrectionFunction') #Options: None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
    return (UB_dict, Ei_supplied, T0_supplied, bad_pulses_threshold, tib_window, emin, emax, additional_dimensions, 
            polarization_state, flipping_ratio, psda, Ef_correction_function )

def generate_mde(data_set):
    """
    reduce a set of runs described in data_set dictionary
    into an md event workspace
    """
    config['default.facility'] = "SNS"
    
    runs = data_set['Runs']
    if not runs:
        raise ValueError('data_set["Runs"] is an invalid runs list')
    if isinstance(runs,dict):
        try:
            with open(runs['file']) as fh:
                rndict = json.load(fh)
            runs = rndict[runs['ky']]
        except FileNotFoundError as FNF:
            print('The file {} was not found in {}.\n  Try specifying the full path'.format(runs['file'],os.getcwd()))
            raise FNF

    data_folder=data_set['RawDataFolder'].strip()
    if not data_folder:
        raise ValueError('data_set["RawDataFolder"] is empty')
    mde_folder= data_set['MdeFolder'].strip()
    if not mde_folder:
        raise ValueError('data_set["MdeFolder"] is empty')
    mde_name=data_set['MdeName'].strip()
    if not mde_name:
        raise ValueError('data_set["MdeName"] is empty')


    mask_workspace=None
    if data_set.get('MaskingDataFile') is not None:
        print('Masking file: {}'.format(data_set['MaskingDataFile']))
        mask_workspace=os.path.split(data_set['MaskingDataFile'])[-1]
        if not mtd.doesExist(mask_workspace):
            Load(data_set['MaskingDataFile'],OutputWorkspace=mask_workspace)

    sample_logs=data_set.get('SampleLogVariables')
    if sample_logs:
        omega_motor_name=sample_logs.get('OmegaMotorName')

    
    (UB_dict, Ei_supplied, T0_supplied, bad_pulses_threshold, tib_window, emin, emax, additional_dimensions,
     polarization_state, flipping_ratio, psda, Ef_correction_function) = set_parameters(data_set)

    for num,run in enumerate(runs):
        try:
            iter(run)
        except:
            run=[run]
        logger.warning("Processing runs {0}/{1}".format(num+1,len(runs)))
        filenames=[]
        patterns=[data_set['RawDataFolder']+'*{}.nxs.h5'.format(r)for r in run] #'*{}_event.nxs' for old files
        for p in patterns:
               print(p)
               filenames.extend(glob.glob(p))
        if len(filenames)<1:
           patterns=[data_set['RawDataFolder']+'*{}_event.nxs'.format(r)for r in run]
           for p in patterns:
               filenames.extend(glob.glob(p))
        if len(filenames)<1:
           raise RuntimeError("no files found")
        print (filenames)
        data  =LoadEventNexus(filenames[0])
        inst_name = data.getInstrument().getName()
        for i in range(1,len(filenames)):
            temp=LoadEventNexus(filenames[i])
            data+=temp
        if len(CheckForSampleLogs(Workspace = data, LogNames = 'pause')) == 0:
            data = FilterByLogValue(InputWorkspace = data, 
                                    LogName = 'pause', 
                                    MinimumValue = -1,
                                    MaximumValue = 0.5)

        if(bad_pulses_threshold):
            data = FilterBadPulses(InputWorkspace = data, LowerCutoff = bad_pulses_threshold)
        if(mask_workspace):
            MaskDetectors(Workspace=data, MaskedWorkspace=mask_workspace)
        else:
            MaskBTP(Workspace=data,Pixel="1-8,121-128")
        if omega_motor_name:
            SetGoniometer(Workspace=data,Axis0=omega_motor_name+',0,1,0,1')
        else:
            SetGoniometer(Workspace=data, Goniometers='Universal')

        run_obj = data.getRun()
        if inst_name in ['HYSPEC', 'CNCS']:
            Ei = Ei_supplied if Ei_supplied else run_obj['EnergyRequest'].getStatistics().mean
            T0=T0_supplied if (T0_supplied is not None) else GetEi(data).Tzero
        else:
            if (Ei_supplied is not None) and (T0_supplied is not None):
                Ei=Ei_supplied
                T0=T0_supplied    
            else:
                data_m = LoadNexusMonitors(filenames[0])
                for i in range(1,len(filenames)):
                    temp=LoadNexusMonitors(filenames[i])
                    data_m+=temp
                # handles if the monitors are histograms or event
                if data_m.id()=='EventWorkspace':
                    Ei, T0 = GetEiT0atSNS(data_m)   # event monitors
                elif data_m.id()=='Workspace2D':
                    Ei, tm1, mi, T0 = GetEi(data_m)   # histogram monitors
                else:
                    raise RuntimeError('Invalid monitor Data type')    

        Emin = emin if emin else -0.95*Ei
        Emax = emax if emax else 0.95*Ei
        Erange='{},{},{}'.format(Emin,(Emax-Emin)*0.2,Emax)

        #Instrument specific adjustments
        #HYSPEC specific:
        if inst_name == 'HYSPEC':
            #get tofmin and tofmax, and filter out anything else
            msd = run_obj['msd'].getStatistics().mean
            tel = (39000+msd+4500)*1000/numpy.sqrt(Ei/5.227e-6)
            tofmin = tel-1e6/120-470
            tofmax = tel+1e6/120+470
            data = CropWorkspace(InputWorkspace = data, XMin = tofmin, XMax = tofmax)    
            if psda is None:
                psda = run_obj['psda'].getStatistics().mean
            data=detector_geometry_correction(data,psda=psda)

        #Time independent BG subtraction
        tib, perform_tib = tib_win(tib_window,inst_name,Ei)
        
        #convert to energy transfer
        dgs_data,_=DgsReduction(SampleInputWorkspace=data,
                                SampleInputMonitorWorkspace=data,
                                TimeZeroGuess=T0,
                                IncidentEnergyGuess=Ei,
                                UseIncidentEnergyGuess=True,
                                IncidentBeamNormalisation='None',
                                EnergyTransferRange=Erange,
                                TimeIndepBackgroundSub=perform_tib,
                                TibTofRangeStart=tib[0],
                                TibTofRangeEnd=tib[1],
                                SofPhiEIsDistribution=False)
        dgs_data = CropWorkspaceForMDNorm(InputWorkspace=dgs_data, XMin = Emin, XMax = Emax)
        Log_removal(data_set,dgs_data)
        if Ef_correction_function == 'HYSPEC_default_correction':
            dgs_data=polarizer_transmission(dgs_data)
        elif Ef_correction_function is not None:
            func=locals()[Ef_correction_function] # Ef_correction_function must be loaded in memory
            dgs_data=func(dgs_data,data_set)

        minValues,maxValues=ConvertToMDMinMaxGlobal(InputWorkspace=dgs_data,
                                                    QDimensions='Q3D',
                                                    dEAnalysisMode='Direct',
                                                    Q3DFrames='Q')
        OtherDimensions=None
        if additional_dimensions:
            OtherDimensions=[]
            minValues=minValues.tolist()
            maxValues=maxValues.tolist()
            for triplet in additional_dimensions:
                OtherDimensions.append(triplet[0])
                minValues.append(triplet[1])
                maxValues.append(triplet[2])
                
        
        ConvertToMD(InputWorkspace=dgs_data,
                    QDimensions='Q3D',
                    dEAnalysisMode='Direct',
                    Q3DFrames="Q_sample",
                    MinValues=minValues,
                    MaxValues=maxValues,
                    OtherDimensions=OtherDimensions,
                    PreprocDetectorsWS='-',
                    OutputWorkspace="__{0}_{1}".format(mde_name,num))

    if len(runs) >1:
      MergeMD(','.join(["__{}_{}".format(mde_name,num) for num in range(len(runs))]),
            OutputWorkspace=mde_name)
      DeleteWorkspaces(','.join(["__{}_{}".format(mde_name,num) for num in range(len(runs))]))
    else:  
      CloneMDWorkspace("__{0}_0".format(mde_name),OutputWorkspace=mde_name)        
    DeleteWorkspaces('data,dgs_data')  

    SetUB(Workspace=mde_name, **UB_dict)
    mde_filename=os.path.join(mde_folder,mde_name+'.nxs')
    SaveMD(InputWorkspace=mde_name,Filename=mde_filename)


##################################################################################################################
# Reduces BG data from sets of runs specified by the dictionary BG_data_set = define_data_set()[0],
# to corresponding combined mde workspaces, or loads the existing combined mde from a file
# Authors: A. Savici, I. Zaliznyak. Last revision: Aug 2021.
##################################################################################################################
def generate_BG_mde(data_set,compress_events_tof):
    """
    reduce a set of runs described in data_set dictionary
    into an md event workspace
    """
    config['default.facility'] = "SNS"
    
    runs=data_set['BackgroundRuns']
    if not runs:
        raise ValueError('data_set["BackgroundRuns"] is an invalid runs list')
    data_folder=data_set['RawDataFolder'].strip()
    bkg_data_folder = data_set.get('BackgroundRawDataFolder', data_folder)
    if not bkg_data_folder:
        raise ValueError('data_set["BackgroundRawDataFolder"] is empty')
    mde_folder=data_set['MdeFolder'].strip()
    if not mde_folder:
        raise ValueError('data_set["MdeFolder"] is empty')
    mde_name=data_set['MdeName'].strip()
    if not mde_name:
        raise ValueError('data_set["MdeName"] is empty')
    bg_mde_name=data_set['BackgroundMdeName'].strip()

    mask_workspace=None
    if data_set.get('MaskingDataFile') is not None:
        print('Masking file: {}'.format(data_set['MaskingDataFile']))
        mask_workspace=os.path.split(data_set['MaskingDataFile'])[-1]
        if not mtd.doesExist(mask_workspace):
            Load(data_set['MaskingDataFile'],OutputWorkspace=mask_workspace)

    sample_logs=data_set.get('SampleLogVariables')
    if sample_logs:
        omega_motor_name=sample_logs.get('OmegaMotorName')
    
    (UB_dict, Ei_supplied, T0_supplied, bad_pulses_threshold, tib_window, emin, emax, additional_dimensions,
     polarization_state, flipping_ratio, psda, Ef_correction_function) = set_parameters(data_set)

    try:
        iter(runs)
    except:
        runs=[runs]
    runs=list(flatten(runs))
    filenames=[]
    patterns=[bkg_data_folder+'*{}.nxs.h5'.format(r)for r in runs] #'*{}_event.nxs' for old files
    for p in patterns:
        filenames.extend(glob.glob(p))
    data=LoadEventNexus(filenames[0])
    inst_name = data.getInstrument().getName()
    for i in range(1,len(filenames)):
        temp=LoadEventNexus(filenames[i])
        data+=temp
    if compress_events_tof:
        data = CompressEvents(data,Tolerance=compress_events_tof)
    if len(CheckForSampleLogs(Workspace = data, LogNames = 'pause')) == 0:
        data = FilterByLogValue(InputWorkspace = data, 
                                LogName = 'pause', 
                                MinimumValue = -1,
                                MaximumValue = 0.5)

    if(bad_pulses_threshold):
        data = FilterBadPulses(InputWorkspace = data, LowerCutoff = bad_pulses_threshold)
    if(mask_workspace):
        MaskDetectors(Workspace=data, MaskedWorkspace=mask_workspace)
    else:
        MaskBTP(Workspace=data,Pixel="1-8,121-128")
    if omega_motor_name:
        SetGoniometer(Workspace=data,Axis0=omega_motor_name+',0,1,0,1')

    run_obj = data.getRun()
    if inst_name in ['HYSPEC', 'CNCS']:
        Ei = Ei_supplied if Ei_supplied else run_obj['EnergyRequest'].getStatistics().mean
        T0=T0_supplied if (T0_supplied is not None) else GetEi(data).Tzero
    else:
        if (Ei_supplied is not None) and (T0_supplied is not None):
            Ei=Ei_supplied
            T0=T0_supplied    
        else:
            data_m = LoadNexusMonitors(filenames[0])
            for i in range(1,len(filenames)):
                temp=LoadNexusMonitors(filenames[i])
                data_m+=temp
            Ei,T0=GetEiT0atSNS(data_m)

    Emin = emin if emin else -0.95*Ei
    Emax = emax if emax else 0.95*Ei
    Erange='{},{},{}'.format(Emin,(Emax-Emin)*0.2,Emax)

    #HYSPEC specific adjustments
    if inst_name == 'HYSPEC':
        #get tofmin and tofmax, and filter out anything else
        msd = run_obj['msd'].getStatistics().mean
        tel = (39000+msd+4500)*1000/numpy.sqrt(Ei/5.227e-6)
        tofmin = tel-1e6/120-470
        tofmax = tel+1e6/120+470
        data = CropWorkspace(InputWorkspace = data, XMin = tofmin, XMax = tofmax)    
        if psda is None:
             psda = run_obj['psda'].getStatistics().mean
        data=detector_geometry_correction(data,psda=psda)

    #Time independent BG subtraction
    tib, perform_tib = tib_win(tib_window,inst_name,Ei)
   

    #convert to energy transfer
    dgs_data,_=DgsReduction(SampleInputWorkspace=data,
                            SampleInputMonitorWorkspace=data,
                            TimeZeroGuess=T0,
                            IncidentEnergyGuess=Ei,
                            UseIncidentEnergyGuess=True,
                            IncidentBeamNormalisation='None',
                            EnergyTransferRange=Erange,
                            TimeIndepBackgroundSub=perform_tib,
                            TibTofRangeStart=tib[0],
                            TibTofRangeEnd=tib[1],
                            SofPhiEIsDistribution=False)
    dgs_data=CropWorkspaceForMDNorm(InputWorkspace=dgs_data, XMin = Emin, XMax = Emax)
    Log_removal(data_set,dgs_data)
    if Ef_correction_function == 'HYSPEC_default_correction':
        dgs_data=polarizer_transmission(dgs_data)
    elif Ef_correction_function is not None:
        func=locals()[Ef_correction_function] # Ef_correction_function must be loaded in memory
        dgs_data=func(dgs_data,data_set)

    minValues,maxValues=ConvertToMDMinMaxGlobal(InputWorkspace=dgs_data,
                                                QDimensions='Q3D',
                                                dEAnalysisMode='Direct',
                                                Q3DFrames='Q')
    OtherDimensions=None
    if additional_dimensions:
        OtherDimensions=[]
        minValues=minValues.tolist()
        maxValues=maxValues.tolist()
        for triplet in additional_dimensions:
            OtherDimensions.append(triplet[0])
            minValues.append(triplet[1])
            maxValues.append(triplet[2])
                

    SetGoniometer(Workspace=dgs_data, Goniometers='Universal')

    ConvertToMD(InputWorkspace=dgs_data,
                QDimensions='Q3D',
                dEAnalysisMode='Direct',
                Q3DFrames="Q_lab",
                MinValues=minValues,
                MaxValues=maxValues,
                OtherDimensions=OtherDimensions,
                PreprocDetectorsWS='-',
                OutputWorkspace=bg_mde_name)
    
    DeleteWorkspaces('data,dgs_data')  

    SetUB(Workspace=bg_mde_name, **UB_dict)
    mde_filename=os.path.join(mde_folder,bg_mde_name+'.nxs')
    SaveMD(InputWorkspace=bg_mde_name,Filename=mde_filename)

