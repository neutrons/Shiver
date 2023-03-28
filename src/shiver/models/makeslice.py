"""The Shiver MakeSlice mantid algorithm"""
# pylint: disable=no-name-in-module

from mantid.api import (
    DataProcessorAlgorithm,
    AlgorithmFactory,
    PropertyMode,
    mtd,
    IMDEventWorkspaceProperty,
    MatrixWorkspaceProperty,
    IMDHistoWorkspaceProperty,
    CommonBinsValidator,
    InstrumentValidator,
)


from mantid.kernel import (
    Direction,
    FloatArrayProperty,
    FloatArrayLengthValidator,
    Property,
    SpecialCoordinateSystem,
    CompositeValidator,
)

from mantid.simpleapi import (
    MDNorm,
    DivideMD,
    MinusMD,
    SmoothMD,
    DeleteWorkspaces,
    _create_algorithm_function,
)


class MakeSlice(DataProcessorAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """MakeSlice algorithm"""

    def name(self):
        return "MakeSlice"

    def category(self):
        return "Shiver"

    def PyInit(self):
        self.copyProperties("MDNorm", "InputWorkspace")

        self.declareProperty(
            IMDEventWorkspaceProperty(
                "BackgroundWorkspace", defaultValue="", optional=PropertyMode.Optional, direction=Direction.Input
            ),
            doc="Background Workspace MDEvent workspace",
        )

        validator = CompositeValidator()
        validator.add(InstrumentValidator())
        validator.add(CommonBinsValidator())

        self.declareProperty(
            MatrixWorkspaceProperty(
                "NormalizationWorkspace",
                defaultValue="",
                optional=PropertyMode.Optional,
                direction=Direction.Input,
                validator=validator,
            ),
            doc="A Matrix workspace.",
        )

        self.declareProperty(
            FloatArrayProperty("QDimension0", [1, 0, 0], FloatArrayLengthValidator(3), direction=Direction.Input),
            "The first Q projection axis",
        )
        self.declareProperty(
            FloatArrayProperty("QDimension1", [0, 1, 0], FloatArrayLengthValidator(3), direction=Direction.Input),
            "The second Q projection axis",
        )
        self.declareProperty(
            FloatArrayProperty("QDimension2", [0, 0, 1], FloatArrayLengthValidator(3), direction=Direction.Input),
            "The third Q projection axis",
        )

        self.copyProperties(
            "MDNorm",
            [
                "Dimension0Name",
                "Dimension0Binning",
                "Dimension1Name",
                "Dimension1Binning",
                "Dimension2Name",
                "Dimension2Binning",
                "Dimension3Name",
                "Dimension3Binning",
                "SymmetryOperations",
            ],
        )

        self.declareProperty(
            name="Smoothing", defaultValue=Property.EMPTY_DBL, direction=Direction.Input, doc="Smoothing"
        )

        self.declareProperty(
            IMDHistoWorkspaceProperty(
                "OutputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Output
            ),
            doc="OutputWorkspace IMDHisto workspace",
        )

    def PyExec(self):
        # Name
        slice_name = self.getPropertyValue("OutputWorkspace")
        # MdeName
        mde_name = str(self.getProperty("InputWorkspace").value).strip()

        mdnorm_parameters = {
            "InputWorkspace": mde_name,
            "OutputWorkspace": slice_name,
            "OutputDataWorkspace": "_data",
            "OutputNormalizationWorkspace": "_norm",
        }

        mdnorm_parameters["SolidAngleWorkspace"] = self.getProperty("NormalizationWorkspace").value

        for par_name in [
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
        ]:
            mdnorm_parameters[par_name] = self.getProperty(par_name).value

        bg_type = None
        # get the background workspace
        bg_mde_name = self.getProperty("BackgroundWorkspace").valueAsStr

        # if background workspace is given
        if bg_mde_name:
            if mtd[bg_mde_name].getSpecialCoordinateSystem() == SpecialCoordinateSystem.QLab:
                mdnorm_parameters["BackgroundWorkspace"] = bg_mde_name
                mdnorm_parameters["OutputBackgroundDataWorkspace"] = "_bkg_data"
                mdnorm_parameters["OutputBackgroundNormalizationWorkspace"] = "_bkg_norm"
            elif mtd[bg_mde_name].getSpecialCoordinateSystem() == SpecialCoordinateSystem.QSample:
                mdnorm_bkg_parameters = mdnorm_parameters.copy()
                mdnorm_bkg_parameters["InputWorkspace"] = bg_mde_name
                mdnorm_bkg_parameters["OutputWorkspace"] = "_bkg"
                mdnorm_bkg_parameters["OutputDataWorkspace"] = "_bkg_data"
                mdnorm_bkg_parameters["OutputNormalizationWorkspace"] = "_bkg_norm"
                bg_type = "sample"
                MDNorm(**mdnorm_bkg_parameters)

        MDNorm(**mdnorm_parameters)
        SmoothingFWHM = self.getProperty("Smoothing").value
        if SmoothingFWHM == Property.EMPTY_DBL:
            SmoothingFWHM = None

        if SmoothingFWHM:
            SmoothMD(
                InputWorkspace="_data",
                WidthVector=SmoothingFWHM,
                Function="Gaussian",
                InputNormalizationWorkspace="_norm",
                OutputWorkspace="_data",
            )
            SmoothMD(
                InputWorkspace="_norm",
                WidthVector=SmoothingFWHM,
                Function="Gaussian",
                InputNormalizationWorkspace="_norm",
                OutputWorkspace="_norm",
            )
            DivideMD(LHSWorkspace="_data", RHSWorkspace="_norm", OutputWorkspace=slice_name)
            if bg_mde_name:
                SmoothMD(
                    InputWorkspace="_bkg_data",
                    WidthVector=SmoothingFWHM,
                    Function="Gaussian",
                    InputNormalizationWorkspace="_bkg_norm",
                    OutputWorkspace="_bkg_data",
                )
                SmoothMD(
                    InputWorkspace="_bkg_norm",
                    WidthVector=SmoothingFWHM,
                    Function="Gaussian",
                    InputNormalizationWorkspace="_bkg_norm",
                    OutputWorkspace="_bkg_norm",
                )
                DivideMD(LHSWorkspace="_bkg_data", RHSWorkspace="_bkg_norm", OutputWorkspace="_bkg")

                MinusMD(LHSWorkspace=slice_name, RHSWorkspace="_bkg", OutputWorkspace=slice_name)
        elif bg_type == "sample":  # there is background from multi-angle
            MinusMD(LHSWorkspace=slice_name, RHSWorkspace="_bkg", OutputWorkspace=slice_name)

        self.setProperty("OutputWorkspace", mtd[slice_name])
        DeleteWorkspaces([ws for ws in ["_bkg", "_bkg_data", "_bkg_norm", "_data", "_norm"] if mtd.doesExist(ws)])


AlgorithmFactory.subscribe(MakeSlice)

# Puts function in simpleapi globals
makeslice = MakeSlice()
makeslice.initialize()
_create_algorithm_function("MakeSlice", 1, makeslice)
