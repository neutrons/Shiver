"""The Shiver MakeSFCorrectedSlices mantid algorithm"""

# pylint: disable=no-name-in-module

from mantid.api import (
    AlgorithmFactory,
    DataProcessorAlgorithm,
    IMDEventWorkspaceProperty,
    IMDHistoWorkspaceProperty,
    PropertyMode,
    mtd,
)
from mantid.kernel import Direction, StringMandatoryValidator
from mantid.simpleapi import (
    Comment,
    DeleteWorkspaces,
    FlippingRatioCorrectionMD,
    MakeSlice,
    MinusMD,
    _create_algorithm_function,
)

from shiver.version import __version__


class MakeSFCorrectedSlices(DataProcessorAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """MakeSFCorrectedSlices algorithm"""

    def name(self):
        return "MakeSFCorrectedSlices"

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
            validator=StringMandatoryValidator(),
            direction=Direction.Input,
            doc="""Formula to define the flipping ratio. It can depend on the variables in the list of sample logs
          defined below""",
        )

        self.declareProperty(
            name="FlippingRatioSampleLog",
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
        flipping_ratio = self.getPropertyValue("FlippingRatio")

        var_names = ""
        flipping_log = self.getPropertyValue("FlippingRatioSampleLog")

        if flipping_log != "":
            var_names = flipping_log

        # output workspace names
        sf_slice_name = self.getPropertyValue("SFOutputWorkspace")
        nsf_slice_name = self.getPropertyValue("NSFOutputWorkspace")

        # MdeNames
        sf_mde_name = str(self.getProperty("SFInputWorkspace").value).strip()
        nsf_mde_name = str(self.getProperty("NSFInputWorkspace").value).strip()

        # polarized workspaces
        sf_mde = mtd[sf_mde_name]
        nsf_mde = mtd[nsf_mde_name]

        # define makeslice_parameters
        makeslice_parameters = {}

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

        # corrections
        sf_f, sf_1 = FlippingRatioCorrectionMD(
            InputWorkspace=sf_mde,
            FlippingRatio=flipping_ratio,
            SampleLogs=var_names,
            startProgress=0.0,
            endProgress=0.05,
        )

        nsf_f, nsf_1 = FlippingRatioCorrectionMD(
            InputWorkspace=nsf_mde,
            FlippingRatio=flipping_ratio,
            SampleLogs=var_names,
            startProgress=0.05,
            endProgress=0.1,
        )

        # make slices for each polarized workspace
        # sf_f
        sf_slice_output_f = sf_slice_name + "_F"
        slice_input = sf_f.name()
        MakeSlice(
            InputWorkspace=slice_input,
            OutputWorkspace=sf_slice_output_f,
            **makeslice_parameters,
            startProgress=0.1,
            endProgress=0.3,
        )

        # sf_1
        sf_slice_output_1 = sf_slice_name + "_1"
        slice_input = sf_1.name()
        MakeSlice(
            InputWorkspace=slice_input,
            OutputWorkspace=sf_slice_output_1,
            **makeslice_parameters,
            startProgress=0.3,
            endProgress=0.5,
        )

        # nsf_f
        nsf_slice_output_f = nsf_slice_name + "_F"
        slice_input = nsf_f.name()
        MakeSlice(
            InputWorkspace=slice_input,
            OutputWorkspace=nsf_slice_output_f,
            **makeslice_parameters,
            startProgress=0.5,
            endProgress=0.7,
        )

        # nsf_1
        nsf_slice_output_1 = nsf_slice_name + "_1"
        slice_input = nsf_1.name()
        MakeSlice(
            InputWorkspace=slice_input,
            OutputWorkspace=nsf_slice_output_1,
            **makeslice_parameters,
            startProgress=0.7,
            endProgress=0.9,
        )

        # workspace calculations
        sf_output = sf_slice_name
        nsf_output = nsf_slice_name

        try:
            MinusMD(
                LHSWorkspace=sf_slice_output_f,
                RHSWorkspace=nsf_slice_output_1,
                OutputWorkspace=sf_output,
            )
            MinusMD(
                LHSWorkspace=nsf_slice_output_f,
                RHSWorkspace=sf_slice_output_1,
                OutputWorkspace=nsf_output,
            )
        except ValueError as err:
            # delete intermediate workspaces before exit
            DeleteWorkspaces(
                [
                    ws
                    for ws in [
                        sf_slice_output_f,
                        sf_slice_output_1,
                        nsf_slice_output_f,
                        nsf_slice_output_1,
                        sf_f.name(),
                        sf_1.name(),
                        nsf_f.name(),
                        nsf_1.name(),
                    ]
                    if mtd.doesExist(ws)
                ]
            )
            raise err
        Comment(sf_output, f"Shiver version {__version__}")
        Comment(nsf_output, f"Shiver version {__version__}")

        self.setProperty("SFOutputWorkspace", mtd[sf_output])
        self.setProperty("NSFOutputWorkspace", mtd[nsf_output])

        DeleteWorkspaces(
            [
                ws
                for ws in [
                    sf_slice_output_f,
                    sf_slice_output_1,
                    nsf_slice_output_f,
                    nsf_slice_output_1,
                    sf_f.name(),
                    sf_1.name(),
                    nsf_f.name(),
                    nsf_1.name(),
                ]
                if mtd.doesExist(ws)
            ]
        )


AlgorithmFactory.subscribe(MakeSFCorrectedSlices)

# Puts function in simpleapi globals
makeslices = MakeSFCorrectedSlices()
makeslices.initialize()
_create_algorithm_function("MakeSFCorrectedSlices", 1, makeslices)
