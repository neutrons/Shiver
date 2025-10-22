
########################################################################################################
# Define list of dictionaries, each describing data (run) sets to be combined in a single mde workspace
# Authors: A. Savici, I. Zaliznyak, March 2019.
########################################################################################################
def define_data_set(**kwargs):
    shared_folder='/SNS/CNCS/IPTS-21407/shared/autoreduce/'
    raw_data_folder='/SNS/CNCS/IPTS-21407/nexus/'
    mde_folder='/SNS/CNCS/IPTS-21407/shared/MDE/'

    data_set_list=[]
# T=2.8K H=0T Ei=3.32meV
    data_set={'Runs':range(297517,297697),          #List of runs, or list of lists of runs that are added together
              'BackgroundRuns':None,   #range(297325,297337)Options: None;list of runs that are added together
              'RawDataFolder':raw_data_folder,      #Options:raw_data_folder string
              'RawDataFolderBackground':None,       #Options:None (same as the raw data); bknd_raw_data_folder string
              'BackgroundScaling':1,             #Options: None (same as 1); scaling factor
              'MdeFolder':mde_folder,               #Options:mde_folder string
              'MdeName':'merged_mde_YbAlO3_3.7meV_0T_3K',   #Options:mde_name string
              'BackgroundMdeName':'BG_8T_100K_merged_mde_YbAlO3_3.7meV_0T_3K',      #Options:None;bg_mde_name string
              'MaskingDataFile':shared_folder+'van_277537.nxs',         #Options:None;data_file_name
              'NormalizationDataFile':shared_folder+'van_277537.nxs',   #Options:None;data_file_name
              'SampleLogVariables':{'OmegaMotorName':None,'Temperature':3.0,'MagneticField':0.0},   #Options:None;LogVariableName;number
              'UBSetup':{'a':5.12484,'b':5.33161,'c':7.31103,'alpha':90,'beta':90,'gamma':90,'u':'-0.0493617,4.27279,-4.37293','v':'-0.0706905,-3.18894,-5.85775'},
               #Data reduction options
              'Ei':None,                            #Options: None;Ei_somehow_determined
              'T0':None,                            #Options: None;T0_determined_from_mantid
              'BadPulsesThreshold':None,            #Options: None;bg_pulses_threshold value
              'TimeIndepBackgroundWindow':'Default',    #Options: None;'Default';[Tib_min,Tib_max]
              'E_min':None,                         #Options: None;Emin if None the value is -0.95*Ei
              'E_max':None,                         #Options: None;Emax if None the value is 0.95*Ei
              'AdditionalDimensions':None,          #Options: None;list of triplets ("name", min, max)
               #Polarized data options
              'PolarizationState':None,             #Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
              'FlippingRatio':None,                 #Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
              'PolarizingSupermirrorDeflectionAdjustment':None, #Options:None;deflection_angle
              'EfCorrectionFunction':None,          #Options:None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
              }
    data_set_list.append(data_set)

    return data_set_list

