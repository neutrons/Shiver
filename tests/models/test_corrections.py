"""Test the histogram workspace saving"""

# pylint: disable=invalid-name
from mantid.api import (  # pylint: disable=no-name-in-module
    PythonAlgorithm,
    AlgorithmFactory,
    MatrixWorkspaceProperty,
    WorkspaceFactory,
)
from mantid.kernel import Direction  # pylint: disable=no-name-in-module
from shiver.models import corrections


class DebyeWallerFactorCorrectionMD(PythonAlgorithm):
    """create a dummy function to test if the algorithms has been applied"""

    def PyInit(self):
        """init"""
        self.declareProperty("InputWorkspace", "")
        self.declareProperty("MeanSquaredDisplacement", "")
        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", "", direction=Direction.Output))

    def PyExec(self):
        """execute"""
        endrange = int(self.getProperty("MeanSquaredDisplacement").value)  # Convert to int
        wspace = WorkspaceFactory.create("Workspace2D", NVectors=1, XLength=endrange, YLength=endrange)
        self.setProperty("OutputWorkspace", wspace)  # Stores the workspace as the given name


class MagneticFormFactorCorrectionMD(PythonAlgorithm):
    """create a dummy function to test if the algorithms has been applied"""

    def PyInit(self):
        """init"""
        self.declareProperty("InputWorkspace", "")
        self.declareProperty("IonName", "")
        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", "", direction=Direction.Output))

    def PyExec(self):
        """execute"""
        wspace = WorkspaceFactory.create("Workspace2D", NVectors=1, XLength=3, YLength=3)
        self.setProperty("OutputWorkspace", wspace)  # Stores the workspace as the given name


def test_applied_debye_waller_factor():
    """test debye-waller is applied"""
    AlgorithmFactory.subscribe(DebyeWallerFactorCorrectionMD)
    model = corrections.CorrectionsModel()
    model.apply_debye_waller_factor_correction("doesnotmatter", "3", "test")
    assert model.has_debye_waller_factor_correction("test")[0]
    assert model.has_debye_waller_factor_correction("test")[1] == "3"
    AlgorithmFactory.unsubscribe("DebyeWallerFactorCorrectionMD",1)

def test_applied_magnetic_form_factor():
    """test magnetic form factor is applied"""
    AlgorithmFactory.subscribe(MagneticFormFactorCorrectionMD)
    model = corrections.CorrectionsModel()
    model.apply_magnetic_form_factor_correction("doesnotmatter", "Nd3+", "test")
    assert model.has_magnetic_form_factor_correction("test")[0]
    assert model.has_magnetic_form_factor_correction("test")[1] == "Nd3+"
    AlgorithmFactory.unsubscribe("MagneticFormFactorCorrectionMD",1)