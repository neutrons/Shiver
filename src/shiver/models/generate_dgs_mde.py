"""The Shiver GenerateDGSMDE mantid algorithm"""
# pylint: disable=no-name-in-module
import json
import numpy
from mantid.simpleapi import (
    ConvertDGSToSingleMDE,
    LoadNexusProcessed,
    LoadEventNexus,
    MaskBTP,
    SetUB,
    MergeMD,
    _create_algorithm_function,
    RenameWorkspace,
    DeleteWorkspaces,
    mtd,
    Comment,
    DgsReduction,
    GenerateGoniometerIndependentBackground,
)
from mantid.api import (
    PythonAlgorithm,
    AlgorithmFactory,
    IMDWorkspaceProperty,
    MultipleFileProperty,
    PropertyMode,
    Progress,
    FileAction,
    FileProperty,
)
from mantid.kernel import (
    Direction,
    Property,
    StringArrayProperty,
    StringListValidator,
)
from shiver.models.utils import flatten_list
from shiver.version import __version__
from .convert_dgs_to_single_mde import get_Ei_T0


class GenerateDGSMDE(PythonAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """GenerateDGSMDE algorithm"""

    def category(self):
        return "MDAlgorithms\\Creation"

    def seeAlso(self):
        return None

    def name(self):
        return "GenerateDGSMDE"

    def summary(self):
        return "Converts DGS data files to a single MDEvent workspace, to be used by MDNorm algorithm"

    def PyInit(self):
        self.declareProperty(
            MultipleFileProperty(name="Filenames", action=FileAction.Load, extensions=[".nxs.h5", "*.*"]),
            doc="List of raw filenames",
        )

        self.declareProperty(
            FileProperty(name="MaskFile", defaultValue="", action=FileAction.OptionalLoad, extensions=[".nxs"]),
            doc="Optional input mask workspace",
        )

        self.declareProperty(
            FileProperty(
                name="DetectorGroupingFile",
                defaultValue="",
                action=FileAction.OptionalLoad,
                extensions=[".xml", ".map"],
            ),
            doc="Optional detector grouping",
        )

        self.declareProperty(
            name="MaskInputs",
            defaultValue="",
            doc="Additional masking (using MaskBTP algorithm)",
        )

        self.declareProperty(
            name="ApplyFilterBadPulses",
            defaultValue=False,
            doc="Flag whether to filter out pulses with low proton charge",
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
            StringArrayProperty(name="AdditionalDimensions", direction=Direction.Input),
            doc="Comma separated list containing sample log name, minimum, maximum values",
        )

        self.declareProperty(
            name="Type",
            defaultValue="Data",
            validator=StringListValidator(
                ["Data", "Background (angle integrated)", "Background (minimized by angle and energy)"]
            ),
            doc="Data preserves the goniometer angle dependence of the data."
            "Background (angle integrated) should be used for an angle independent background."
            "Background (minimized by angle and energy)",
        )

        self.declareProperty(
            name="UBParameters", defaultValue="", doc="UB matrix parameters that will be passed to SetUB algorithm"
        )

        self.declareProperty(
            IMDWorkspaceProperty(
                "OutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output
            ),
            doc="Output MD event workspace (in Q-space) to use with MDNorm",
        )

    def validateInputs(self):
        issues = {}
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

        if (
            self.getProperty("Type").value == "Background (minimized by angle and energy)"
            and self.getProperty("DetectorGroupingFile").value == ""
        ):
            issues[
                "DetectorGroupingFile"
            ] = "A grouping file is required when for 'Background (minimized by angle and energy)'"

        return issues

    def PyExec(self):  # pylint: disable=too-many-branches
        # get processing type and filenames
        process_type = self.getProperty("Type").value
        filenames = self.getProperty("Filenames").value
        if isinstance(filenames, str):
            filename_nested_list = [[filenames]]
        else:
            if process_type == "Data":
                filename_nested_list = [list(flatten_list(x)) for x in filenames]
            else:
                filename_nested_list = [list(flatten_list(filenames))]

        endrange = 100
        progress = Progress(self, start=0.0, end=1.0, nreports=endrange)

        # set up a dictionary of common parameters
        cdsm_dict = {"Loader": "Raw Event"}

        progress.report("Gathering mask information")
        mask_filename = self.getPropertyValue("MaskFile")
        __mask = None
        if mask_filename:
            __mask = LoadNexusProcessed(Filename=mask_filename)
        mask_btp_inputs = self.getPropertyValue("MaskInputs")
        if mask_btp_inputs:
            if not __mask:
                __mask = LoadEventNexus(Filename=filename_nested_list[0][0], MetadataOnly=True)
            btp_pars_list = json.loads(mask_btp_inputs.replace("'", '"'))
            for pars in btp_pars_list:
                MaskBTP(Workspace=__mask, **pars)
        cdsm_dict["MaskWorkspace"] = __mask

        filter_bad_pulses_flag = self.getPropertyValue("ApplyFilterBadPulses")
        filter_threshold = None
        if filter_bad_pulses_flag:
            filter_threshold = self.getPropertyValue("BadPulsesThreshold")
            if filter_threshold == Property.EMPTY_DBL:
                filter_threshold = 95.0
        cdsm_dict["BadPulsesThreshold"] = filter_threshold

        if process_type == "Data":
            cdsm_dict["QFrame"] = "Q_sample"
        else:
            cdsm_dict["QFrame"] = "Q_lab"

        cdsm_dict["OmegaMotorName"] = self.getPropertyValue("OmegaMotorName")
        cdsm_dict["Ei"] = self.getProperty("Ei").value
        cdsm_dict["T0"] = self.getProperty("T0").value
        cdsm_dict["EMin"] = self.getProperty("EMin").value
        cdsm_dict["EMax"] = self.getProperty("EMax").value
        cdsm_dict["TimeIndependentBackground"] = self.getProperty("TimeIndependentBackground").value
        cdsm_dict["PolarizingSupermirrorDeflectionAdjustment"] = self.getProperty(
            "PolarizingSupermirrorDeflectionAdjustment"
        ).value
        cdsm_dict["AdditionalDimensions"] = self.getProperty("AdditionalDimensions").value

        output_ws = self.getPropertyValue("OutputWorkspace")
        self.log().debug(f"Nested filename structure {filename_nested_list}")

        if process_type == "Background (minimized by angle and energy)":
            ws_list = []
            for n, filename in enumerate(filename_nested_list[0]):
                data = LoadEventNexus(filename, OutputWorkspace=f"__tmp_{n}")
                Ei, T0 = get_Ei_T0(data, data, cdsm_dict["Ei"], cdsm_dict["T0"], [filename])
                print(Ei, T0)
                e_min = cdsm_dict["EMin"]
                e_max = cdsm_dict["EMax"]
                if e_min == Property.EMPTY_DBL:
                    e_min = -0.95 * Ei
                if e_max == Property.EMPTY_DBL:
                    e_max = 0.95 * Ei
                Erange = f"{e_min}, {0.02*Ei}, {e_max}"

                DgsReduction(
                    SampleInputWorkspace=f"__tmp_{n}",
                    SampleInputMonitorWorkspace=f"__tmp_{n}",
                    IncidentEnergyGuess=Ei,
                    TimeZeroGuess=T0,
                    UseIncidentEnergyGuess=True,
                    IncidentBeamNormalisation="None",
                    EnergyTransferRange=Erange,
                    TimeIndepBackgroundSub=False,
                    SofPhiEIsDistribution=False,
                    OutputWorkspace=f"__tmp_{n}",
                )
                ws_list.append(f"__tmp_{n}")
            bkg = GenerateGoniometerIndependentBackground(
                ws_list, GroupingFile=self.getProperty("DetectorGroupingFile").value
            )
            DeleteWorkspaces(ws_list)
            filename_nested_list = [str(bkg)]
            ConvertDGSToSingleMDE(InputWorkspace=bkg, OutputWorkspace=f"__{output_ws}_part0", **cdsm_dict)
        else:
            for i, f_names in enumerate(filename_nested_list):
                progress.report(int(endrange * 0.9 * i / len(filename_nested_list)), f"Processing {'+'.join(f_names)}")
                ConvertDGSToSingleMDE(
                    Filenames="+".join(f_names), OutputWorkspace=f"__{output_ws}_part{i}", **cdsm_dict
                )

        if __mask:
            DeleteWorkspaces([__mask])
        progress.report("Merging data")
        if len(filename_nested_list) > 1:
            ws_list = [f"__{output_ws}_part{i}" for i in range(len(filename_nested_list))]
            MergeMD(ws_list, OutputWorkspace=output_ws)
            DeleteWorkspaces(ws_list)
        else:
            RenameWorkspace(InputWorkspace=f"__{output_ws}_part0", OutputWorkspace=output_ws)

        try:
            UB_parameters = json.loads(self.getProperty("UBParameters").value.replace("'", '"'))
            SetUB(Workspace=output_ws, **UB_parameters)
        except (ValueError, RuntimeError, json.decoder.JSONDecodeError) as e:
            self.log().error("Could not set the UB")
            self.log().error(str(e))

        Comment(output_ws, f"Shiver version {__version__}")
        self.setProperty("OutputWorkspace", mtd[output_ws])


AlgorithmFactory.subscribe(GenerateDGSMDE)
# Puts function in simpleapi globals
alg_cdsm = GenerateDGSMDE()
alg_cdsm.initialize()
_create_algorithm_function("GenerateDGSMDE", 1, alg_cdsm)
