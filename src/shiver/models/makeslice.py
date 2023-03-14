"""The Shiver MakeSlice mantid algorithm"""

from mantid.api import (
    DataProcessorAlgorithm,
    AlgorithmFactory,
    PropertyMode,
    mtd,
    IMDEventWorkspaceProperty,
    MatrixWorkspaceProperty,
    IMDHistoWorkspaceProperty,
)  # pylint: disable=no-name-in-module


from mantid.kernel import (
    Direction,
    FloatArrayProperty,
    FloatArrayLengthValidator,
    Property,
    SpecialCoordinateSystem,
)  # pylint: disable=no-name-in-module


class MakeSlice(DataProcessorAlgorithm):
    # pylint: disable=invalid-name,missing-function-docstring
    """MakeSlice algorithm"""

    def name(self):
        return "MakeSlice"

    def category(self):
        return "Shiver"

    def PyInit(self):
        # Workspaces
        self.declareProperty(
            IMDEventWorkspaceProperty(
                "InputWorkspace", defaultValue="", optional=PropertyMode.Mandatory, direction=Direction.Input
            ),
            doc="Input MDEvent workspace",
        )

        self.declareProperty(
            IMDEventWorkspaceProperty(
                "BackgroundWorkspace", defaultValue="", optional=PropertyMode.Optional, direction=Direction.Input
            ),
            doc="Background Workspace MDEvent workspace",
        )

        self.declareProperty(
            MatrixWorkspaceProperty(
                "NormalizationWorkspace", defaultValue="", optional=PropertyMode.Optional, direction=Direction.Input
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

        self.declareProperty(name="ConvertToChi", defaultValue=False, direction=Direction.Input, doc="Convert To Chi")

        self.declareProperty(name="Temperature", defaultValue="", direction=Direction.Input, doc="Temperature")

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
        from mantid.simpleapi import (
            MDNorm,
            DivideMD,
            MinusMD,
            SmoothMD,
            ApplyDetailedBalanceMD,
        )  # pylint: disable=no-name-in-module

        # Name
        slice_name = str(self.getProperty("OutputWorkspace").value).strip()
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

        is_chi = self.getProperty("ConvertToChi").value

        temperature = 0
        if is_chi:
            temperature = self.getProperty("Temperature").value
            if temperature is None:
                raise ValueError(
                    "For calculating chi'' one needs to set the temperature in the dataset definition. See example."
                )

            ApplyDetailedBalanceMD(
                InputWorkspace=mde_name, Temperature=str(temperature), OutputWorkspace=mde_name + "_chi"
            )
            mdnorm_parameters["InputWorkspace"] = mde_name + "_chi"

        bg_type = None
        # get the background workspace
        bg_mde_name = self.getProperty("BackgroundWorkspace").valueAsStr

        # if background workspace is given
        if bg_mde_name:
            if is_chi:
                ApplyDetailedBalanceMD(
                    InputWorkspace=bg_mde_name, Temperature=str(temperature), OutputWorkspace=bg_mde_name + "_chi"
                )
                bg_mde_name += "_chi"

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


AlgorithmFactory.subscribe(MakeSlice)
