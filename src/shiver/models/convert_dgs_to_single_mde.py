"""The Shiver ConvertDGSToSingleMDE mantid algorithm"""
# pylint: disable=no-name-in-module
import numpy
from mantid.simpleapi import (
    LoadEventNexus,
    LoadNexusProcessed,
    LoadNexusMonitors,
    CheckForSampleLogs,
    FilterByLogValue,
    FilterBadPulses,
    CropWorkspace,
    RotateInstrumentComponent,
    HYSPECSuggestTIB,
    CNCSSuggestTIB,
    ConvertToMD,
    ConvertToMDMinMaxGlobal,
    mtd,
    CropWorkspaceForMDNorm,
    DgsReduction,
    MaskDetectors,
    MaskBTP,
    SetGoniometer,
    GetEi,
    GetEiT0atSNS,
    DeleteWorkspace,
    _create_algorithm_function,
)
from mantid.api import (
    PythonAlgorithm,
    AlgorithmFactory,
    IMDWorkspaceProperty,
    MatrixWorkspaceProperty,
    MultipleFileProperty,
    PropertyMode,
    Progress,
    FileAction,
)
from mantid.kernel import (
    Direction,
    Property,
    StringArrayProperty,
    StringListValidator,
    amend_config,
)
from shiver.models.utils import flatten_list


def get_Ei_T0(data, data_m, Ei_supplied, T0_supplied, filenames, progress=None):
    # pylint: disable=invalid-name,too-many-branches
    """Determines the Ei and T0 values from the data supplied"""
    if Ei_supplied == Property.EMPTY_DBL:
        Ei_supplied = None
    if T0_supplied == Property.EMPTY_DBL:
        T0_supplied = None

    inst_name = data.getInstrument().getName()
    run_obj = data.getRun()

    # check if monitor is necessary and get Ei,T0
    if inst_name in ["HYSPEC", "CNCS"]:
        Ei = None
        if Ei_supplied:
            Ei = Ei_supplied
        elif "EnergyRequest" in run_obj:
            Ei = run_obj["EnergyRequest"].getStatistics().mean
        else:
            raise ValueError("EnergyRequest is not defined")
        T0 = T0_supplied if (T0_supplied is not None) else GetEi(data).Tzero
    else:
        if (Ei_supplied is not None) and (T0_supplied is not None):
            Ei = Ei_supplied
            T0 = T0_supplied
        else:
            delete_monitors = False
            if not data_m:
                # load monitors
                if progress:
                    progress.report("Loading monitors")
                delete_monitors = True
                data_m = LoadNexusMonitors(filenames[0])
                for i in range(1, len(filenames)):
                    __temp = LoadNexusMonitors(filenames[i])
                    data_m += __temp
            # handles if the monitors are histograms or event
            if data_m.id() == "EventWorkspace":
                Ei, T0 = GetEiT0atSNS(data_m)  # event monitors
            elif data_m.id() == "Workspace2D":
                Ei, _, _, T0 = GetEi(data_m)  # histogram monitors
            else:
                raise RuntimeError("Invalid monitor Data type")
            if delete_monitors:
                DeleteWorkspace(data_m)

    return Ei, T0


class ConvertDGSToSingleMDE(PythonAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """ConvertDGSToSingleMDE algorithm"""

    def category(self):
        return "MDAlgorithms\\Creation;Shiver"

    def seeAlso(self):
        return None

    def name(self):
        return "ConvertDGSToSingleMDE"

    def summary(self):
        return "Converts an event workspace (or file) to MDEvent workspace, to be used by MDNorm algorithm"

    def PyInit(self):
        self.declareProperty(
            MatrixWorkspaceProperty(
                name="InputWorkspace", defaultValue="", direction=Direction.Input, optional=PropertyMode.Optional
            ),
            doc="Optional input workspace",
        )

        self.declareProperty(
            MatrixWorkspaceProperty(
                name="InputMonitorWorkspace", defaultValue="", direction=Direction.Input, optional=PropertyMode.Optional
            ),
            doc="Optional input monitor workspace",
        )

        self.declareProperty(
            MultipleFileProperty(name="Filenames", action=FileAction.OptionalLoad),
            doc="List of filenames to be loaded (optional), if the input workspace is not set",
        )

        self.declareProperty(
            name="Loader",
            defaultValue="Raw Event",
            validator=StringListValidator(["Raw Event", "Processed Nexus"]),
            doc="Loader type for the files (will use LoadEventNexus or LoadNexusProcessed)",
        )

        self.declareProperty(
            MatrixWorkspaceProperty(
                name="MaskWorkspace", defaultValue="", direction=Direction.Input, optional=PropertyMode.Optional
            ),
            doc="Optional input mask workspace",
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
            name="EMin",
            defaultValue=Property.EMPTY_DBL,
            doc="Minimum energy transfer. If empty, -0.95*Ei",
        )

        self.declareProperty(
            name="EMax",
            defaultValue=Property.EMPTY_DBL,
            doc="Maximum energy transfer. If empty, 0.95*Ei",
        )

        self.declareProperty(
            name="TimeIndependentBackground",
            defaultValue="",
            doc="Time independent background subtation. If 'Default', will try to calculate"
            " the range for CNCS and HYSPEC. Otherwise, it expect a minimum and maximum time of flight",
        )

        self.declareProperty(
            name="PolarizingSupermirrorDeflectionAdjustment",
            defaultValue=Property.EMPTY_DBL,
            doc="Override the polarizing supermirror deflection angle for HYSPEC",
        )

        self.declareProperty(
            name="QFrame",
            defaultValue="Q_sample",
            validator=StringListValidator(["Q_sample", "Q_lab"]),
            doc="Q_sample preserves the goniometer angle dependence of the data."
            "Q_lab should be used for an angle independent background.",
        )

        self.declareProperty(
            StringArrayProperty(name="AdditionalDimensions", direction=Direction.Input),
            doc="Comma separated list containing sample log name, minimum, maximum values",
        )

        self.declareProperty(
            IMDWorkspaceProperty(
                "OutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output
            ),
            doc="Output MD event workspace (in Q-space) to use with MDNorm",
        )

    def validateInputs(self):
        issues = {}
        input_ws_name = self.getProperty("InputWorkspace").valueAsStr
        filenames = self.getProperty("Filenames").valueAsStr
        if len(filenames) < 5 and len(input_ws_name) < 1:
            issues["Filenames"] = "Either Filenames of InputWorkspace must be set"
            issues["InputWorkspace"] = "Either Filenames of InputWorkspace must be set"
        tib_window = self.getPropertyValue("TimeIndependentBackground").strip()
        if tib_window and tib_window != "Default":
            try:
                tib = numpy.array(tib_window.split(","), dtype=float)
                if len(tib) != 2:
                    raise ValueError("length is not 2")
            except ValueError:
                issues[
                    "TimeIndependentBackground"
                ] = "This must be either 'Default' or two numbers separated by a comma"
        ad_dims = self.getPropertyValue("AdditionalDimensions")
        if ad_dims:
            ad_dims = ad_dims.split(",")
            if len(ad_dims) % 3:
                issues["AdditionalDimensions"] = "Must enter triplets of name, minimum, maximum"
            for i in range(len(ad_dims) // 3):
                try:
                    if float(ad_dims[3 * i + 1]) >= float(ad_dims[3 * i + 2]):
                        raise ValueError("wrong order")
                except (ValueError, IndexError):
                    issues["AdditionalDimensions"] = f"The triplet #{i} has some issues"
        return issues

    def PyExec(self):  # pylint: disable=too-many-branches
        # get properties
        data = self.getProperty("InputWorkspace").value
        data_m = self.getProperty("InputMonitorWorkspace").value
        filenames = self.getProperty("Filenames").value
        loader = self.getProperty("Loader").value
        mask_workspace = self.getPropertyValue("MaskWorkspace")
        bad_pulses_threshold = self.getProperty("BadPulsesThreshold").value
        if bad_pulses_threshold > 100 or bad_pulses_threshold < 0:
            bad_pulses_threshold = 0
        omega_motor_name = self.getPropertyValue("OmegaMotorName")
        Ei_supplied = self.getProperty("Ei").value
        T0_supplied = self.getProperty("T0").value
        tib_window = self.getPropertyValue("TimeIndependentBackground")
        e_min = self.getProperty("EMin").value
        e_max = self.getProperty("EMax").value
        psda = self.getProperty("PolarizingSupermirrorDeflectionAdjustment").value
        if psda == Property.EMPTY_DBL:
            psda = None
        Q_frame = self.getPropertyValue("QFrame")
        additional_dimensions = self.getPropertyValue("AdditionalDimensions")
        output_name = self.getPropertyValue("OutputWorkspace")

        endrange = 100
        progress = Progress(self, start=0.0, end=1.0, nreports=endrange)

        # Load the data if InputWorkspace is not provided
        if not data:
            filenames = list(flatten_list([filenames]))
            if loader == "Raw Event":
                progress.report("Loading")
                data = LoadEventNexus(filenames[0])
                for i in range(1, len(filenames)):
                    progress.report("Loading")
                    __temp = LoadEventNexus(filenames[i])
                    data += __temp
            else:
                progress.report("Loading")
                data = LoadNexusProcessed(filenames[0])
                for i in range(1, len(filenames)):
                    progress.report("Loading")
                    __temp = LoadNexusProcessed(filenames[i])
                    data += __temp

        # get instrument, units
        inst_name = data.getInstrument().getName()
        units = data.getAxis(0).getUnit().unitID()  # TOF or DeltaE

        # do filtering
        if units == "TOF" and len(CheckForSampleLogs(Workspace=data, LogNames="pause")) == 0:
            data = FilterByLogValue(InputWorkspace=data, LogName="pause", MinimumValue=-1, MaximumValue=0.5)
        if units == "TOF" and bad_pulses_threshold > 0:
            data = FilterBadPulses(InputWorkspace=data, LowerCutoff=bad_pulses_threshold)

        # Masking, goniometer
        if mask_workspace:
            MaskDetectors(Workspace=data, MaskedWorkspace=mask_workspace)
        else:
            MaskBTP(Workspace=data, Pixel="1-8,121-128")
        if omega_motor_name:
            SetGoniometer(Workspace=data, Axis0=omega_motor_name + ",0,1,0,1")
        else:
            SetGoniometer(Workspace=data, Goniometers="Universal")

        # If units not DeltaE (from InputWorkspace) convert using DgsReduction
        if units != "DeltaE":
            Ei, T0 = get_Ei_T0(data, data_m, Ei_supplied, T0_supplied, filenames, progress)

            # Instrument specific adjustments
            # HYSPEC specific:
            if inst_name == "HYSPEC":
                run_obj = data.getRun()
                # get tofmin and tofmax, and filter out anything else
                msd = run_obj["msd"].getStatistics().mean
                tel = (39000 + msd + 4500) * 1000 / numpy.sqrt(Ei / 5.227e-6)
                tofmin = tel - 1e6 / 120 - 470
                tofmax = tel + 1e6 / 120 + 470
                data = CropWorkspace(InputWorkspace=data, XMin=tofmin, XMax=tofmax)
                if psda is None:
                    psda = run_obj["psda"].getStatistics().mean
                if psda:
                    psr = run_obj["psr"].getStatistics().mean
                    offset = psda * (1.0 - psr / 4200.0)
                    RotateInstrumentComponent(
                        Workspace=data, ComponentName="Tank", X=0, Y=1, Z=0, Angle=offset, RelativeRotation=1
                    )

            # get TIB
            tib = [None, None]
            perform_tib = False
            if tib_window:
                perform_tib = True
                if tib_window == "Default":
                    # HYSPEC specific:
                    if inst_name == "HYSPEC":
                        if Ei == 15:
                            tib = [22000.0, 23000.0]
                        else:
                            tib = HYSPECSuggestTIB(Ei)
                    # CNCS specific:
                    elif inst_name == "CNCS":
                        tib = CNCSSuggestTIB(Ei)
                    # No tib defaults for other instruments:
                    else:
                        perform_tib = False
                else:
                    tib = tib_window.split(",")

            progress.report(int(endrange * 0.5), "DgsReduction")

            # DgsReduction
            if e_min == Property.EMPTY_DBL:
                e_min = -0.95 * Ei
            if e_max == Property.EMPTY_DBL:
                e_max = 0.95 * Ei
            Erange = f"{e_min}, {e_max-e_min}, {e_max}"

            with amend_config(facility="SNS"):
                dgs_data, _ = DgsReduction(
                    SampleInputWorkspace=data,
                    SampleInputMonitorWorkspace=data,
                    TimeZeroGuess=T0,
                    IncidentEnergyGuess=Ei,
                    UseIncidentEnergyGuess=True,
                    IncidentBeamNormalisation="None",
                    EnergyTransferRange=Erange,
                    TimeIndepBackgroundSub=perform_tib,
                    TibTofRangeStart=tib[0],
                    TibTofRangeEnd=tib[1],
                    SofPhiEIsDistribution=False,
                )
        else:
            dgs_data = data
            if e_min == Property.EMPTY_DBL:
                e_min = dgs_data.readX(0)[0]
            if e_max == Property.EMPTY_DBL:
                e_max = dgs_data.readX(0)[-1]

        # Crop workspace
        dgs_data = CropWorkspaceForMDNorm(InputWorkspace=dgs_data, XMin=e_min, XMax=e_max)

        # Convert to MD
        minValues, maxValues = ConvertToMDMinMaxGlobal(
            InputWorkspace=dgs_data, QDimensions="Q3D", dEAnalysisMode="Direct", Q3DFrames="Q"
        )
        OtherDimensions = None
        if additional_dimensions:
            OtherDimensions = []
            minValues = minValues.tolist()
            maxValues = maxValues.tolist()
            for i, value in enumerate(additional_dimensions.split(",")):
                if i % 3 == 0:
                    OtherDimensions.append(value)
                if i % 3 == 1:
                    minValues.append(float(value))
                if i % 3 == 2:
                    maxValues.append(float(value))

        progress.report(int(endrange * 0.8), "ConvertToMD")
        convert_params = {"MaxRecursionDepth": 2}
        ConvertToMD(
            InputWorkspace=dgs_data,
            QDimensions="Q3D",
            dEAnalysisMode="Direct",
            Q3DFrames=Q_frame,
            MinValues=minValues,
            MaxValues=maxValues,
            OtherDimensions=OtherDimensions,
            PreprocDetectorsWS="-",
            OutputWorkspace=output_name,
            **convert_params,
        )
        self.setProperty("OutputWorkspace", mtd[output_name])
        DeleteWorkspace(data)
        DeleteWorkspace(dgs_data)
        try:
            DeleteWorkspace(__temp)
        except NameError:
            pass
        progress.report(endrange, "Done")


AlgorithmFactory.subscribe(ConvertDGSToSingleMDE)

# Puts function in simpleapi globals
alg = ConvertDGSToSingleMDE()
alg.initialize()
_create_algorithm_function("ConvertDGSToSingleMDE", 1, alg)
