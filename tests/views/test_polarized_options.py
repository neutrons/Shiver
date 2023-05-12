"""UI tests for Reduction Parameters widget: input values"""
from functools import partial
from qtpy import QtCore


from shiver.views.polarized_options import PolarizedDialog
from shiver.views.reduction_parameters import ReductionParameters


def test_polarized_options_unpolarized(qtbot):
    """Test for adding all valid inputs in polarized dialog - unpolarized"""
    dialog = PolarizedDialog()
    dialog.show()

    # unpolarized
    qtbot.mouseClick(dialog.state_unpolarized, QtCore.Qt.LeftButton)

    # assert no error
    assert len(dialog.invalid_fields) == 0

    dict_data = dialog.get_polarized_options_dict()
    # assert values are added in the dictionary

    assert dict_data["PolarizationState"] is None
    assert dict_data["FlippingRatio"] is None
    assert dict_data["SampleLog"] == ""
    assert dict_data["PSDA"] is None
    qtbot.wait(500)
    dialog.close()


def test_polarized_options_spin(qtbot):
    """Test for adding all valid inputs in polarized dialog - spin"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.psda_input, "2")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.ratio_input, "omega+8")
    assert len(dialog.invalid_fields) == 1
    qtbot.keyClicks(dialog.log_input, "omega")
    assert len(dialog.invalid_fields) == 0
    qtbot.mouseClick(dialog.dir_px, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_px.height() / 2)))
    assert dialog.dir_px.isChecked()
    # assert no error
    assert len(dialog.invalid_fields) == 0

    qtbot.wait(500)

    dict_data = dialog.get_polarized_options_dict()
    # assert values are added in the dictionary

    assert dict_data["PolarizationState"] == "SF_Px"
    assert dict_data["FlippingRatio"] == "omega+8"
    assert dict_data["SampleLog"] == "omega"
    assert dict_data["PSDA"] == "2"
    dialog.close()


def test_polarized_options_no_spin(qtbot):
    """Test for adding all valid inputs in polarized dialog - no spin"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.psda_input, "5")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.log_input, "kapa")
    assert len(dialog.invalid_fields) == 1
    qtbot.keyClicks(dialog.ratio_input, "sin(kapa)*1.2+4.54")
    assert len(dialog.invalid_fields) == 0
    qtbot.mouseClick(dialog.dir_py, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_py.height() / 2)))
    assert dialog.dir_py.isChecked()
    # assert no error
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True
    dict_data = dialog.get_polarized_options_dict()
    # assert values are added in the dictionary

    assert dict_data["PolarizationState"] == "NSF_Py"
    assert dict_data["FlippingRatio"] == "sin(kapa)*1.2+4.54"
    assert dict_data["SampleLog"] == "kapa"
    assert dict_data["PSDA"] == "5"

    dialog.close()


def test_polarized_options_ratio_num(qtbot):
    """Test for adding all valid inputs in polarized dialog - flipping ratio number"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_spin, QtCore.Qt.LeftButton)

    # required fields
    qtbot.keyClicks(dialog.psda_input, "2")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.ratio_input, "8")
    assert len(dialog.invalid_fields) == 0
    assert dialog.dir_pz.isChecked()
    # assert no error
    assert len(dialog.invalid_fields) == 0

    qtbot.wait(500)

    dict_data = dialog.get_polarized_options_dict()
    # assert values are added in the dictionary

    assert dict_data["PolarizationState"] == "SF_Pz"
    assert dict_data["FlippingRatio"] == "8"
    assert dict_data["SampleLog"] == ""
    assert dict_data["PSDA"] == "2"
    dialog.close()


def test_polarized_options_invalid_ratio_log(qtbot):
    """Test for adding invalid flipping ratio-sample log"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    qtbot.mouseClick(dialog.dir_py, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_py.height() / 2)))
    assert dialog.dir_py.isChecked()
    assert len(dialog.invalid_fields) == 2

    # sample log- ratio
    qtbot.keyClicks(dialog.ratio_input, "sin(kapa)*1.2+4.54")
    assert len(dialog.invalid_fields) == 1
    qtbot.keyClicks(dialog.log_input, "pi")
    assert len(dialog.invalid_fields) == 1
    assert dialog.btn_apply.isEnabled() is False
    dialog.close()


def test_polarized_options_invalid_psda(qtbot):
    """Test for adding invalid psda"""
    dialog = PolarizedDialog()
    dialog.show()

    qtbot.keyClicks(dialog.psda_input, "3.8")
    assert len(dialog.invalid_fields) == 0
    dialog.close()


def test_help_button(qtbot):
    """Test for pushing the help button"""

    dialog = PolarizedDialog()
    dialog.show()

    # push the Help button
    qtbot.mouseClick(dialog.btn_help, QtCore.Qt.LeftButton)

    dialog.close()


def test_apply_btn_valid_all(qtbot):
    """Test for clicking apply and storing all data as a dictionary in parent"""
    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.ratio_input, "6.78+3.9*pi")
    assert len(dialog.invalid_fields) == 1
    qtbot.keyClicks(dialog.log_input, "pi")
    assert len(dialog.invalid_fields) == 0
    assert dialog.dir_pz.isChecked()

    # assert no error
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True
    # click apply
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    dict_data = dialog.parent.dict_polarized

    # assert values are added in parent dictionary
    assert dict_data["PolarizationState"] == "NSF_Pz"
    assert dict_data["FlippingRatio"] == "6.78+3.9*pi"
    assert dict_data["SampleLog"] == "pi"
    assert dict_data["PSDA"] is None
    dialog.close()


def test_apply_btn_valid(qtbot):
    """Test for clicking apply and storing data besides Sample log as a dictionary in parent"""
    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)
    assert dialog.btn_apply.isEnabled() is False
    # required fields
    qtbot.keyClicks(dialog.psda_input, "3.45")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.ratio_input, "6.78")
    assert len(dialog.invalid_fields) == 0
    assert dialog.dir_pz.isChecked()

    # assert no error
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True
    # click apply
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    dict_data = dialog.parent.dict_polarized

    # assert values are added in parent dictionary
    assert dict_data["PolarizationState"] == "NSF_Pz"
    assert dict_data["FlippingRatio"] == "6.78"
    assert dict_data["SampleLog"] == ""
    assert dict_data["PSDA"] == "3.45"
    dialog.close()


def test_apply_btn_invalid(qtbot):
    """Test for clicking apply with invalid fields"""
    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 2

    assert dialog.btn_apply.isEnabled() is False
    dialog.close()


def test_polarized_options_initialization_from_dict_nsf():
    """Test for initializing all parameters from dict - NSF"""

    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    params = {"PolarizationState": "NSF_Pz", "FlippingRatio": "6.78+3.9*pi", "SampleLog": "pi", "PSDA": None}
    dialog.populate_pol_options_from_dict(params)

    # assert fields are populated properly
    # NSF-->state_no_spin checked
    assert dialog.state_unpolarized.isChecked() is False
    assert dialog.state_spin.isChecked() is False
    assert dialog.state_no_spin.isChecked() is True

    # Pz-->direction Pz checked
    assert dialog.dir_pz.isChecked() is True
    assert dialog.dir_px.isChecked() is False
    assert dialog.dir_py.isChecked() is False

    assert dialog.ratio_input.text() == params["FlippingRatio"]
    assert dialog.ratio_input.isVisible() is True
    assert dialog.log_input.text() == params["SampleLog"]
    assert dialog.ratio_input.isVisible() is True
    assert dialog.psda_input.text() == ""
    assert len(dialog.invalid_fields) == 0
    dialog.close()


def test_polarized_options_initialization_from_dict_unpolarized():
    """Test for initializing all parameters from dict - unpolarized"""

    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    params = {"PolarizationState": "Unpolarized Data", "FlippingRatio": None, "SampleLog": "", "PSDA": 2.2}
    dialog.populate_pol_options_from_dict(params)

    # assert fields are populated properly
    # Unpolarized checked
    assert dialog.state_unpolarized.isChecked() is True
    assert dialog.state_spin.isChecked() is False
    assert dialog.state_no_spin.isChecked() is False

    # direction pz default checked
    assert dialog.dir_pz.isChecked() is True
    assert dialog.dir_px.isChecked() is False
    assert dialog.dir_py.isChecked() is False

    assert dialog.ratio_input.text() == ""
    assert dialog.ratio_input.isVisible() is False
    assert dialog.log_input.text() == ""
    assert dialog.ratio_input.isVisible() is False
    assert dialog.psda_input.text() == "2.2"
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True
    dialog.close()


def test_polarized_options_initialization_from_dict_invalid():
    """Test for initializing parameters from invalid dict"""

    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    params = {"p": "Unpolarized Data", "FlippingRatio": None, "SampleLog": "", "PSDA": 9.4}

    # This is to handle modal dialog expected error
    def handle_dialog():
        dialog.error.done(1)

    QtCore.QTimer.singleShot(500, partial(handle_dialog))
    dialog.populate_pol_options_from_dict(params)
