"""Test the histogram workspace saving"""

# pylint: disable=invalid-name
# pylint: disable=no-name-in-module
from unittest.mock import MagicMock, patch
from mantid.simpleapi import CreateMDWorkspace, FakeMDEventData
import pytest
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
    with pytest.raises(ValueError):
        model.apply_magnetic_form_factor_correction("ws", "wrongIon", "test")


def test_applied_magnetic_form_factor_error():
    """test magnetic form factor has wrongIon name"""
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)
    model = corrections.CorrectionsModel()
    with pytest.raises(ValueError):
        model.apply_magnetic_form_factor_correction("ws", "wrongIon", "test")


def test_applied_debye_waller_factor_error():
    """test debye-waller has negative <u^2>"""
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)
    model = corrections.CorrectionsModel()
    with pytest.raises(ValueError):
        model.apply_debye_waller_factor_correction("ws", "-3", "test")


def test_apply_debye_waller_factor_correction_finished_error():
    """mock algorithm observer for error message"""
    model = corrections.CorrectionsModel()
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)
    ws_name = "ws"
    fake_observer = MagicMock()
    model.algorithms_observers.add(fake_observer)

    error_messages = []

    def error_callback(msg):
        error_messages.append(msg)

    model.connect_error_message(error_callback)

    model.apply_debye_waller_factor_correction_finished(
        ws_name=ws_name, alg=fake_observer, error=True, msg="Debye-Waller failed"
    )

    assert not model.algorithm_running
    assert fake_observer not in model.algorithms_observers
    assert len(error_messages) == 1
    assert "Debye-Waller failed" in error_messages[0]


def test_apply_magnetic_form_factor_correction_finished_error():
    """mock algorithm observer for error message"""
    model = corrections.CorrectionsModel()
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)
    ws_name = "ws"
    fake_observer = MagicMock()
    model.algorithms_observers.add(fake_observer)

    error_messages = []

    def error_callback(msg):
        error_messages.append(msg)

    model.connect_error_message(error_callback)

    model.apply_magnetic_form_factor_correction_finished(
        ws_name=ws_name, alg=fake_observer, error=True, msg="magnetic form factor failed"
    )

    assert not model.algorithm_running
    assert fake_observer not in model.algorithms_observers
    assert len(error_messages) == 1
    assert "magnetic form factor failed" in error_messages[0]


@patch("time.sleep", return_value=None)
@patch.object(corrections.CorrectionsModel, "apply_debye_waller_factor_correction")
def test_apply_waits_for_previous_algorithm(mock_apply_dwf, mock_sleep):
    """test sleep(0.1)"""
    model = corrections.CorrectionsModel()

    model.algorithm_running = True

    def stop_running_once(*args, **kwargs):  # pylint: disable=unused-argument
        model.algorithm_running = False

    mock_sleep.side_effect = stop_running_once
    ws = CreateMDWorkspace(Dimensions="1", Extents="1,4", Names="|Q|", Units="A")
    FakeMDEventData(ws, UniformParams=-6000)

    model.apply(
        ws_name="ws",
        detailed_balance=True,
        hyspec_polarizer_transmission=False,
        debye_waller_factor=True,
        temperature="100",
        u2="2",
    )

    # Assert that sleep was called (indicating a wait loop happened)
    mock_sleep.assert_called_with(0.1)
    mock_apply_dwf.assert_called_once()
