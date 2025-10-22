
########################################################################################################
# Define list of dictionaries, each describing data (run) sets to be combined in a single mde workspace
# Authors: A. Savici, I. Zaliznyak, March 2019. Last revision: August 2019.
########################################################################################################
def define_data_set(**kwargs):
    raw_data_folder='/SNS/HYS/IPTS-21819/nexus/'
    mde_folder='/SNS/HYS/IPTS-21819/shared/merged_mde_Px/'
    shared_folder='/SNS/HYS/shared/autoreduce/normalization/'

    data_set_list=[]
    #  T = 1p6 K Ei = 3p8meV, Px SF
    data_set={'Runs':range(209998,210059),
              'RawDataFolder':raw_data_folder,      #Options:raw_data_folder string
              'BackgroundRuns':None,
              'BackgroundMdeName':None,      #Options:None;bg_mde_name string
              'MdeFolder':mde_folder,               #Options:mde_folder string
              'MdeName':'merged_mde_Ruby_3p8meV_1p6K_Px_SF',
              'MaskingDataFile':shared_folder+'V_13p1g_Pol_SF_8p5meV_240hz_35deg_feb_2018.nxs',
              'NormalizationDataFile':shared_folder+'V_13p1g_Pol_SF_8p5meV_240hz_35deg_feb_2018.nxs',
              'SampleLogVariables':{'OmegaMotorName':None,'Temperature':1.6,'MagneticField':None},   #Options:None;LogVariableName;number
              'UBSetup':{'a':13.49,'b':9.935,'c':6.891,'alpha':90,'beta':90,'gamma':90,'u':'0,1,0','v':'0,0,1'},
               #Data reduction options
              'Ei':3.8,                            #Options: None;Ei_somehow_determined
              'T0':112.0,                          #Options: None;T0_determined_from_mantid
              'BadPulsesThreshold':None,           #Options: None;bg_pulses_threshold value
              'TimeIndepBackgroundWindow':'Default',    #Options: None;'Default';[Tib_min,Tib_max]
              'E_min':None,                        #Options: None;Emin
              'E_max':None,                        #Options: None;Emax
              'AdditionalDimensions':None,         #Options: None;list of triplets ("name", min, max)
               #Polarized data options
              'PolarizationState':'SF_Px',         #Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
              'FlippingRatio':12.0,                #Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
              'PolarizingSupermirrorDeflectionAdjustment':None, #Options:None;deflection_angle
              'EfCorrectionFunction':None,          #Options:None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
              }
    data_set_list.append(data_set)
    # T=1.6K Ei=3p8meV Px NSF
    data_set={'Runs':range(210059,210109),
              'RawDataFolder':raw_data_folder,      #Options:raw_data_folder string
              'BackgroundRuns':None,
              'BackgroundMdeName':None,      #Options:None;bg_mde_name string
              'MdeFolder':mde_folder,               #Options:mde_folder string
              'MdeName':'merged_mde_Ruby_3p8meV_1p6K_Px_NSF',
              'MaskingDataFile':shared_folder+'V_13p1g_Pol_SF_8p5meV_240hz_35deg_feb_2018.nxs',
              'NormalizationDataFile':shared_folder+'V_13p1g_Pol_SF_8p5meV_240hz_35deg_feb_2018.nxs',
              'SampleLogVariables':{'OmegaMotorName':None,'Temperature':1.6,'MagneticField':None},   #Options:None;LogVariableName;number
              'UBSetup':{'a':13.49,'b':9.935,'c':6.891,'alpha':90,'beta':90,'gamma':90,'u':'0,1,0','v':'0,0,1'},
               #Data reduction options
              'Ei':3.8,                            #Options: None;Ei_somehow_determined
              'T0':112.0,                          #Options: None;T0_determined_from_mantid
              'BadPulsesThreshold':None,           #Options: None;bg_pulses_threshold value
              'TimeIndepBackgroundWindow':'Default',    #Options: None;'Default';[Tib_min,Tib_max]
              'E_min':None,                        #Options: None;Emin
              'E_max':None,                        #Options: None;Emax
              'AdditionalDimensions':None,         #Options: None;list of triplets ("name", min, max)
               #Polarized data options
              'PolarizationState':'NSF_Px',         #Options:None;'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'
              'FlippingRatio':12.0,                #Options:None;'14';'6.5+2.8*cos((omega+3.7)*pi/180),omega'
              'PolarizingSupermirrorDeflectionAdjustment':None, #Options:None;deflection_angle
              'EfCorrectionFunction':None,          #Options:None;'HYSPEC_default_correction';Custom_Ef_Correction_Function_Name
              }
    data_set_list.append(data_set)

    return data_set_list

