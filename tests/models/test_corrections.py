"""Test the histogram workspace saving"""

# pylint: disable=too-many-lines
import os
import ast
import h5py
import pytest
import time

# Need to import the new algorithms so they are registered with mantid
import shiver.models.makeslice  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
from mantid.api import PythonAlgorithm, AlgorithmFactory, MatrixWorkspaceProperty, WorkspaceFactory
from mantid.kernel import Direction
import shiver.models.corrections as corrections


class DebyeWallerFactorCorrectionMD(PythonAlgorithm):
    """create a dummy function to test if the algorithms has been applied"""

    def PyInit(self):
        self.declareProperty("InputWorkspace", "")
        self.declareProperty("MeanSquaredDisplacement", "")
        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", "", direction=Direction.Output))

    def PyExec(self):
        endrange = int(self.getProperty("MeanSquaredDisplacement").value)  # Convert to int
        wspace = WorkspaceFactory.create("Workspace2D", NVectors=1, XLength=endrange, YLength=endrange)
        self.setProperty("OutputWorkspace", wspace)  # Stores the workspace as the given name


class MagneticFormFactorCorrectionMD(PythonAlgorithm):
    """create a dummy function to test if the algorithms has been applied"""

    def PyInit(self):
        self.declareProperty("InputWorkspace", "")
        self.declareProperty("IonName", "")
        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", "", direction=Direction.Output))

    def PyExec(self):
        wspace = WorkspaceFactory.create("Workspace2D", NVectors=1, XLength=3, YLength=3)
        self.setProperty("OutputWorkspace", wspace)  # Stores the workspace as the given name


def test_applied_debye_waller_factor():
    AlgorithmFactory.subscribe(DebyeWallerFactorCorrectionMD)
    model = corrections.CorrectionsModel()
    model.apply_debye_waller_factor_correction("doesnotmatter", "3", "test")
    assert model.has_debye_waller_factor_correction("test")[0]
    assert model.has_debye_waller_factor_correction("test")[1] == "3"


def test_applied_magnetic_form_factor():
    AlgorithmFactory.subscribe(MagneticFormFactorCorrectionMD)
    model = corrections.CorrectionsModel()
    model.apply_magnetic_form_factor_correction("doesnotmatter", "Nd3+", "test")
    assert model.has_magnetic_form_factor_correction("test")[0]
    assert model.has_magnetic_form_factor_correction("test")[1] == "Nd3+"
