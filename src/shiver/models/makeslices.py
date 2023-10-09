"""The Shiver MakeSlice mantid algorithm"""
# pylint: disable=no-name-in-module

from mantid.api import (
    DataProcessorAlgorithm,
    AlgorithmFactory,
    PropertyMode,
    mtd,
    IMDEventWorkspaceProperty,
    IMDHistoWorkspaceProperty,
)


from mantid.kernel import (
    Direction,
)

from mantid.simpleapi import (
    MinusMD,
    DeleteWorkspaces,
    Comment,
    MakeSlice,
    FlippingRatioCorrectionMD,
    _create_algorithm_function,
)


from shiver.version import __version__


class MakeMultipleSlices(DataProcessorAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """MakeMultipleSlices algorithm"""

    def name(self):
        return "MakeMultipleSlices"

    def category(self):
        return "Shiver"

    def PyInit(self):
        self.declareProperty(
            IMDEventWorkspaceProperty("SFInputWorkspace", defaultValue="", direction=Direction.Input),
            doc="InputWorkspace Spin-Flip MDEvent workspace. Must be in Q_sample frame.",
        )

        self.declareProperty(
            IMDEventWorkspaceProperty("NSFInputWorkspace", defaultValue="", direction=Direction.Input),
            doc="InputWorkspace Non Spin-Flip MDEvent workspace. Must be in Q_sample frame.",
        )

        self.declareProperty(
            name="FlippingRatio",
            defaultValue="",
            direction=Direction.Input,
            doc="""Formula to define the flipping ratio. It can depend on the variables in the list of sample logs
          defined below""",
        )

        self.declareProperty(
            name="SampleLogs",
            defaultValue="",
            direction=Direction.Input,
            doc="""
            Comma separated list of sample logs that can appear in the formula for flipping ratio""",
        )

        self.copyProperties(
            "MakeSlice",
            [
                "BackgroundWorkspace",
                "NormalizationWorkspace",
                "QDimension0",
                "QDimension1",
                "QDimension2",
                "Dimension0Name",
                "Dimension0Binning",
                "Dimension1Name",
                "Dimension1Binning",
                "Dimension2Name",
                "Dimension2Binning",
                "Dimension3Name",
                "Dimension3Binning",
                "SymmetryOperations",
                "Smoothing",
            ],
        )

        self.declareProperty(
            IMDHistoWorkspaceProperty(
                "SFOutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output
            ),
            doc="Spin-Flip OutputWorkspace IMDHisto workspace",
        )
        self.declareProperty(
            IMDHistoWorkspaceProperty(
                "NSFOutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output
            ),
            doc="Non Spin-Flip OutputWorkspace IMDHisto workspace",
        )

    def PyExec(self):
        flipping_ratio_data = self.getPropertyValue("FlippingRatio")
        if flipping_ratio_data is None:
            raise ValueError("Flipping ratio is not defined")

        try:
            flipping_ratio = float(flipping_ratio_data)
            flipping_ratio = str(flipping_ratio)
            var_names = ""
        except ValueError:
            flipping_ratio, var_names = flipping_ratio_data.split(",", 1)

        # Name
        slice_name = self.getPropertyValue("OutputWorkspace")

        # MdeNames
        sf_mde_name = str(self.getProperty("SFInputWorkspace").value).strip()
        nsf_mde_name = str(self.getProperty("NSFInputWorkspace").value).strip()

        # polarized workspaces
        sf_mde = mtd[sf_mde_name]
        nsf_mde = mtd[nsf_mde_name]

        # corrections
        sf_f, sf_1 = FlippingRatioCorrectionMD(
            InputWorkspace=sf_mde, FlippingRatio=flipping_ratio, SampleLogs=var_names
        )
        nsf_f, nsf_1 = FlippingRatioCorrectionMD(
            InputWorkspace=nsf_mde, FlippingRatio=flipping_ratio, SampleLogs=var_names
        )

        # define makeslice_parameters
        makeslice_parameters = {
            # "InputWorkspace": mde_name,
            # "OutputWorkspace": slice_name,
        }

        for par_name in [
            "BackgroundWorkspace",
            "NormalizationWorkspace",
            "QDimension0",
            "QDimension1",
            "QDimension2",
            "Dimension0Name",
            "Dimension0Binning",
            "Dimension1Name",
            "Dimension1Binning",
            "Dimension2Name",
            "Dimension2Binning",
            "Dimension3Name",
            "Dimension3Binning",
            "SymmetryOperations",
            "Smoothing",
        ]:
            makeslice_parameters[par_name] = self.getProperty(par_name).value

        # make slices for each polarized workspace
        # sf_f
        slice_output = slice_name + "_SF_F"
        slice_input = sf_f.name()
        MakeSlice(InputWorkspace=slice_input, OutputWorkspace=slice_output, *makeslice_parameters)

        # sf_1
        slice_output = slice_name + "_SF_1"
        slice_input = sf_1.name()
        MakeSlice(InputWorkspace=slice_input, OutputWorkspace=slice_output, *makeslice_parameters)

        # nsf_f
        slice_output = slice_name + "_NSF_F"
        slice_input = nsf_f.name()
        MakeSlice(InputWorkspace=slice_input, OutputWorkspace=slice_output, *makeslice_parameters)

        # nsf_1
        slice_output = slice_name + "_NSF_1"
        slice_input = nsf_1.name()
        MakeSlice(InputWorkspace=slice_input, OutputWorkspace=slice_output, *makeslice_parameters)

        # workspace calculations
        MinusMD(
            LHSWorkspace=slice_name + "_SF_F",
            RHSWorkspace=slice_name + "_NSF_1",
            OutputWorkspace=slice_name + "_SF_FRcorr",
        )
        MinusMD(
            LHSWorkspace=slice_name + "_NSF_F",
            RHSWorkspace=slice_name + "_SF_1",
            OutputWorkspace=slice_name + "_NSF_FRcorr",
        )

        Comment(slice_name, f"Shiver version {__version__}")

        self.setProperty("SFOutputWorkspace", mtd[slice_name + "_SF_FRcorr"])
        self.setProperty("NSFOutputWorkspace", mtd[slice_name + "_NSF_FRcorr"])

        # delete intermediate workspaces
        DeleteWorkspaces(
            [
                ws
                for ws in [slice_name + "_SF_F", slice_name + "_NSF_1", slice_name + "_NSF_F", slice_name + "_SF_1"]
                if mtd.doesExist(ws)
            ]
        )


AlgorithmFactory.subscribe(MakeMultipleSlices)

# Puts function in simpleapi globals
makeslices = MakeMultipleSlices()
makeslices.initialize()
_create_algorithm_function("MakeMultipleSlices", 1, makeslices)
