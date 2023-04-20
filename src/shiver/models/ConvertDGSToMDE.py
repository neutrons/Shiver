from mantid.simpleapi import (LoadEventNexus, LoadNexusProcessed, LoadNexusMonitors,
                              CheckForSampleLogs, FilterByLogValue, FilterBadPulses,
                              CropWorkspace, RotateInstrumentComponent, SuggestTibHYSPEC,
                              SuggestTibCNCS, ConvertToMD,ConvertToMDMinMaxGlobal,
                              CropWorkspaceForMDNorm,
                              MaskDetectors, MaskBTP, SetGoniometer, GetEi, GetEiT0atSNS)
from mantid.api import (PythonAlgorithm, AlgorithmFactory, IMDWorkspaceProperty, MatrixWorkspaceProperty, MultipleFileProperty, PropertyMode, FileAction)
from mantid.kernel import (config, Direction, Property, StringListValidator)
import numpy


class ConvertDGSToMDE(PythonAlgorithm):
    def category(self):
        return "MDAlgorithms\\Creation"

    def seeAlso(self):
        return None

    def name(self):
        return "ConvertDGSToMDE"

    def summary(self):
        return "Converts an event workspace (or file) to MDEvent workspace, to be used by MDNorm algorithm"

    def PyInit(self):
        self.declareProperty(
            MatrixWorkspaceProperty(name="InputWorkspace",
                                    defaultValue="",
                                    direction=Direction.Input,
                                    optional=PropertyMode.Optional),
            doc = "Optional input workspace"
        )
        
        self.declareProperty(
            MatrixWorkspaceProperty(name="InputMonitorWorkspace",
                                    defaultValue="",
                                    direction=Direction.Input,
                                    optional=PropertyMode.Optional),
            doc = "Optional input monitor workspace"
        )
        
        self.declareProperty(MultipleFileProperty(name="Filenames", action=FileAction.OptionalLoad),
            doc="List of filenames to be loaded (optional), if the input workspace is not set")
            
        self.declareProperty(
            name="Loader",
            defaultValue="Raw Event",
            validator=StringListValidator(["Raw Event", "Processed Nexus"]),
            doc="Loader type for the files (will use LoadEventNexus or LoadNexusProcessed)",
        )
        
        self.declareProperty(
            MatrixWorkspaceProperty(name="MaskWorkspace",
                                    defaultValue="",
                                    direction=Direction.Input,
                                    optional=PropertyMode.Optional),
            doc = "Optional input mask workspace"
        )
        
        self.declareProperty(
            name="BadPulsesThreshold",
            defaultValue=Property.EMPTY_DBL,
            doc="The percentage of the average proton charge to use as the lower bound",
        )
        
        self.declareProperty(
            name="OmegaMotorName",
            defaultValue="",
            doc="Optional motor name for the vertical goniometer axis."
                "By default will use the universal gonimeter, if all"
                "chi, phi, and omega logs are in the workspace",
        )
        
        self.declareProperty(
            name="Ei",
            defaultValue=Property.EMPTY_DBL,
            doc="Incident energy (will override the value in logs)",
        )
        
        self.declareProperty(
            name="T0",
            defaultValue=Property.EMPTY_DBL,
            doc="Incident T0",
        )
        
        self.declareProperty(
            name="PolarizingSupermirrorDeflectionAdjustment",
            defaultValue=Property.EMPTY_DBL,
            doc="Override the polarizing supermirror deflection angle for HYSPEC",
        )
        
        self.declareProperty(
            IMDWorkspaceProperty("OutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output),
            doc="Output MD event workspace (in Q-space) to use with MDNorm",
        )


    def validateInputs(self):
        issues = {}
        input_ws_name = self.getProperty("InputWorkspace").valueAsStr
        filenames = self.getProperty("Filenames").valueAsStr
        if len(filenames)<5 and len(input_ws_name)<1:
            issues['Filenames'] = "Either Filenames of InputWorkspace must be set"
            issues['InputWorkspace'] = "Either Filenames of InputWorkspace must be set"
        return issues

    def PyExec(self):
        # TODO: this should be replaced by a with statement, so the config is restored to previous state
        config['default.facility'] = "SNS"
        # get properties
        data = self.getProperty("InputWorkspace").value
        data_m = self.getProperty("InputMonitorWorkspace").value
        filenames = self.getProperty("Filenames").value
        loader = self.getProperty("Loader").value
        mask_workspace = self.getPropertyValue("MaskWorkspace")
        bad_pulses_threshold = self.getProperty('BadPulsesThreshold').value
        if bad_pulses_threshold>100 or bad_pulses_threshold<0:
            bad_pulses_threshold = 0
        omega_motor_name = self.getPropertyValue("OmegaMotorName")
        Ei_supplied = self.getProperty('Ei').value
        T0_supplied = self.getProperty('T0').value
        if Ei_supplied == Property.EMPTY_DBL:
            Ei_supplied = None
        if T0_supplied == Property.EMPTY_DBL:
            T0_supplied = None
        psda = self.getProperty('PolarizingSupermirrorDeflectionAdjustment').value
        if psda == Property.EMPTY_DBL:
            psda = None
        output_name = self.getPropertyValue("OutputWorkspace")
        
        # Load the data if InputWorkspace is not provided
        if not data:
            if type(filenames) == str:
                filenames = [filenames]
            else: # list
                if type(filenames[0]) == list:
                    filenames = filenames[0]
            if loader == "Raw Event":
                data = LoadEventNexus(filenames[0])
                for i in range(1,len(filenames)):
                    temp = LoadEventNexus(filenames[i])
                    data += temp
            else:
                data = LoadNexusProcessed(filenames[0])
                for i in range(1,len(filenames)):
                    temp = LoadNexusProcessed(filenames[i])
                    data += temp

        # get instrument, units, and run object
        inst_name = data.getInstrument().getName()
        units = data.getAxis(0).getUnit().unitID() # TOF or DeltaE
        run_obj = data.getRun()

        # do filtering
        if units == 'TOF' and len(CheckForSampleLogs(Workspace = data, LogNames = 'pause')) == 0:
            data = FilterByLogValue(InputWorkspace = data, 
                                    LogName = 'pause', 
                                    MinimumValue = -1,
                                    MaximumValue = 0.5)
        if units == 'TOF' and bad_pulses_threshold > 0:
            data = FilterBadPulses(InputWorkspace = data, LowerCutoff = bad_pulses_threshold)
        
        # Masking, goniometer
        if(mask_workspace):
            MaskDetectors(Workspace=data, MaskedWorkspace=mask_workspace)
        else:
            MaskBTP(Workspace=data,Pixel="1-8,121-128")
        if omega_motor_name:
            SetGoniometer(Workspace=data,Axis0=omega_motor_name+',0,1,0,1')
        else:
            SetGoniometer(Workspace=data, Goniometers='Universal')

        # If units not DeltaE (from InputWorkspace) convert using DgsReduction    
        if units != 'DeltaE':   
            # check if monitor is necessary and get Ei,T0
            if inst_name in ['HYSPEC', 'CNCS']:
                Ei = Ei_supplied if Ei_supplied else run_obj['EnergyRequest'].getStatistics().mean
                T0 = T0_supplied if (T0_supplied is not None) else GetEi(data).Tzero
            else:
                if (Ei_supplied is not None) and (T0_supplied is not None):
                    Ei = Ei_supplied
                    T0 = T0_supplied    
                else:
                    if not data_m:
                        # load monitors
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
                    DeleteWorkspace(data_m)
            
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
                if psda:
                    psr = run_obj['psr'].getStatistics().mean
                    offset = psda*(1.-psr/4200.)
                    RotateInstrumentComponent(Workspace=data, ComponentName='Tank',
                                              X=0, Y=1, Z=0,
                                              Angle=offset, RelativeRotation=1)
            
            # get TIB
            tib = [None,None]
            perform_tib = False
            if tib_window is not None:
                perform_tib=True
                if tib_window == 'Default':
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
            
            # DgsReduction
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
        else:
            dgs_data = data

        # Crop workspace
        dgs_data=CropWorkspaceForMDNorm(InputWorkspace=dgs_data, XMin = Emin, XMax = Emax)

        # Convert to MD
        minValues, maxValues=ConvertToMDMinMaxGlobal(InputWorkspace=dgs_data,
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
                    Q3DFrames=Q_frame,
                    MinValues=minValues,
                    MaxValues=maxValues,
                    OtherDimensions=OtherDimensions,
                    PreprocDetectorsWS='-',
                    OutputWorkspace=output_name)
        self.setProperty("OutputWorkspace", mtd[output_name]) 

AlgorithmFactory.subscribe(ConvertDGSToMDE)
