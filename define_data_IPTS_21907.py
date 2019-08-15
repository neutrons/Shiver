import os
import numpy as np

########################################################################################################
# Define list of dictionaries, each describing data (run) sets to be combined in a single mde workspace 
# Authors: A. Savici, I. Zaliznyak, March 2019. Last revision: August 2019.
########################################################################################################
def define_data_set(**kwargs):
    raw_data_folder='/SNS/HYS/IPTS-21907/nexus/'
    mde_folder='/SNS/HYS/IPTS-21907/shared/MDE/'

    data_set_list=[]
# T=36K Ei=27meV SF Px
    runs_SF_Px_36K=[]
    for n in range(221):
        runs_SF_Px_36K.append([220076+n,220541+n])
    data_set={'Runs':runs_SF_Px_36K,                #range(220076,220297)+range(220541,220762) List of runs, or list of lists of runs that are added together
              'BackgroundRuns':[220954,220955],   #[220954,220955][220076,220296,220541,220761]Options: None;list of runs that are added together
              'RawDataFolder':raw_data_folder,      #Options:raw_data_folder string
              'MdeFolder':mde_folder,               #Options:mde_folder string
              'MdeName':'merged_mde_LSCO_0.17_27meV_36K_SF_Px',   #Options:mde_name string
              'BackgroundMdeName':'BG_T0_failed_merged_mde_LSCO_0.17_27meV_36K_SF_Px',      #Options:None;bg_mde_name string
              'MaskingDataFile':'/SNS/HYS/shared/autoreduce/normalization/TiZr_15meV_45deg_july_2019.nxs',          #Options:None;data_file_name
              'NormalizationDataFile':'/SNS/HYS/shared/autoreduce/normalization/TiZr_15meV_45deg_july_2019.nxs',    #Options:None;data_file_name
              'SampleLogVariables':{'OmegaMotorName':None,'Temperature':36.0,'MagneticField':None},   #Options:None;LogVariableName;number
              'UBSetup':{'a':3.77,'b':3.77,'c':13.2,'alpha':90,'beta':90,'gamma':90,'u':'1,0,0','v':'0,1,0'},
               #Data reduction options
              'Ei':None,                            #Options: None;Ei_somehow_determined
              'T0':None,                            #Options: None;T0_determined_from_mantid
              'BadPulsesThreshold':None,            #Options: None;bg_pulses_threshold value
              'TimeIndepBackgroundWindow':None,     #Options: None;[Tib_min,Tib_max]
              'E_min':-4,                         #Options: None;Emin
              'E_max':26,                         #Options: None;Emax
              'AdditionalDimensions':None,          #Options: None;list of triplets ("name", min, max)
               #Polarized data options
              'PolarizationState':'SF_Px',             #Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
              'FlippingRatio':11.0,                 #Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
              'PolarizingSupermirrorDeflectionAdjustment':None, #Options:None;deflection_angle
              'EfCorrectionFunction':None,          #Options:None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
              }
    data_set_list.append(data_set)

# T=36K Ei=27meV NSF Px
    data_set={'Runs':range(220320,220541),          #List of runs, or list of lists of runs that are added together
              'BackgroundRuns':[220954,220955],     #[220954,220955][220320,220540]Options: None;list of runs that are added together
              'RawDataFolder':raw_data_folder,      #Options:raw_data_folder string
              'MdeFolder':mde_folder,               #Options:mde_folder string
              'MdeName':'merged_mde_LSCO_0.17_27meV_36K_NSF_Px',   #Options:mde_name string
              'BackgroundMdeName':'BG_T0_failed_merged_mde_LSCO_0.17_27meV_36K_NSF_Px',      #Options:None;bg_mde_name string
              'MaskingDataFile':'/SNS/HYS/shared/autoreduce/normalization/TiZr_15meV_45deg_july_2019.nxs',          #Options:None;data_file_name
              'NormalizationDataFile':'/SNS/HYS/shared/autoreduce/normalization/TiZr_15meV_45deg_july_2019.nxs',    #Options:None;data_file_name
              'SampleLogVariables':{'OmegaMotorName':None,'Temperature':36.0,'MagneticField':None},   #Options:None;LogVariableName;number
              'UBSetup':{'a':3.77,'b':3.77,'c':13.2,'alpha':90,'beta':90,'gamma':90,'u':'1,0,0','v':'0,1,0'},
               #Data reduction options
              'Ei':None,                            #Options: None;Ei_somehow_determined
              'T0':None,                            #Options: None;T0_determined_from_mantid
              'BadPulsesThreshold':None,            #Options: None;bg_pulses_threshold value
              'TimeIndepBackgroundWindow':None,     #Options: None;[Tib_min,Tib_max]
              'E_min':-4,                         #Options: None;Emin
              'E_max':26,                         #Options: None;Emax
              'AdditionalDimensions':None,          #Options: None;list of triplets ("name", min, max)
               #Polarized data options
              'PolarizationState':'NSF_Px',             #Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
              'FlippingRatio':11.0,                 #Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
              'PolarizingSupermirrorDeflectionAdjustment':None, #Options:None;deflection_angle
              'EfCorrectionFunction':None,          #Options:None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
              }
    data_set_list.append(data_set)

    return data_set_list

