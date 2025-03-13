"""Test the histogram workspace saving"""

# pylint: disable=invalid-name
from mantid.simpleapi import CreateMDWorkspace, FakeMDEventData
from shiver.models import corrections


def test_applied_debye_waller_factor():
    """test debye-waller is applied"""
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)
    model = corrections.CorrectionsModel()
    model.apply_debye_waller_factor_correction("ws", "3", "test")
    assert model.has_debye_waller_factor_correction("test")[0]
    assert model.has_debye_waller_factor_correction("test")[1] == "3"


def test_applied_magnetic_form_factor():
    """test magnetic form factor is applied"""
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)
    model = corrections.CorrectionsModel()
    model.apply_magnetic_form_factor_correction("ws", "Nd3", "test")
    assert model.has_magnetic_form_factor_correction("test")[0]
    assert model.has_magnetic_form_factor_correction("test")[1] == "Nd3"
