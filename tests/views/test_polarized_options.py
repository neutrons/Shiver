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

    qtbot.wait(500)
    dialog.close()


def test_polarized_options_spin(qtbot):
    """Test for adding all valid inputs in polarized dialog - spin"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 3
    qtbot.keyClicks(dialog.ratio_input, "omega+8")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.log_input, "omega")
    assert len(dialog.invalid_fields) == 1
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

    dialog.close()


def test_polarized_options_no_spin(qtbot):
    """Test for adding all valid inputs in polarized dialog - no spin"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 3
    qtbot.keyClicks(dialog.log_input, "kapa")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.ratio_input, "sin(kapa)*1.2+4.54")
    assert len(dialog.invalid_fields) == 1
    qtbot.mouseClick(dialog.dir_py, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_px.height() / 2)))
    assert dialog.dir_py.isChecked()
    # assert no error
    assert len(dialog.invalid_fields) == 0
    dict_data = dialog.get_polarized_options_dict()
    # assert values are added in the dictionary

    assert dict_data["PolarizationState"] == "NSF_Py"
    assert dict_data["FlippingRatio"] == "sin(kapa)*1.2+4.54"
    assert dict_data["SampleLog"] == "kapa"

    dialog.close()


def test_polarized_options_ratio_num(qtbot):
    """Test for adding all valid inputs in polarized dialog - flipping ratio number"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 3
    qtbot.keyClicks(dialog.ratio_input, "8")
    assert len(dialog.invalid_fields) == 1
    qtbot.mouseClick(dialog.dir_pz, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_px.height() / 2)))
    assert dialog.dir_pz.isChecked()
    # assert no error
    assert len(dialog.invalid_fields) == 0

    qtbot.wait(500)

    dict_data = dialog.get_polarized_options_dict()
    # assert values are added in the dictionary

    assert dict_data["PolarizationState"] == "SF_Pz"
    assert dict_data["FlippingRatio"] == "8"
    assert dict_data["SampleLog"] == ""

    dialog.close()


def test_polarized_options_invalid_ratio_log(qtbot):
    """Test for adding invalid flipping ratio-sample log"""
    dialog = PolarizedDialog()
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    qtbot.mouseClick(dialog.dir_py, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_px.height() / 2)))
    assert dialog.dir_py.isChecked()
    assert len(dialog.invalid_fields) == 2

    # sample log- ratio
    qtbot.keyClicks(dialog.ratio_input, "sin(kapa)*1.2+4.54")
    assert len(dialog.invalid_fields) == 1
    qtbot.keyClicks(dialog.log_input, "pi")
    assert len(dialog.invalid_fields) == 1

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
    assert len(dialog.invalid_fields) == 3
    qtbot.keyClicks(dialog.ratio_input, "6.78+3.9*pi")
    assert len(dialog.invalid_fields) == 2
    qtbot.keyClicks(dialog.log_input, "pi")
    assert len(dialog.invalid_fields) == 1
    qtbot.mouseClick(dialog.dir_pz, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_px.height() / 2)))
    assert dialog.dir_pz.isChecked()

    # assert no error
    assert len(dialog.invalid_fields) == 0

    # click apply
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    dict_data = dialog.parent.dict_polarized

    # assert values are added in parent dictionary
    assert dict_data["PolarizationState"] == "NSF_Pz"
    assert dict_data["FlippingRatio"] == "6.78+3.9*pi"
    assert dict_data["SampleLog"] == "pi"

    dialog.close()


def test_apply_btn_valid(qtbot):
    """Test for clicking apply and storing data besides Sample log as a dictionary in parent"""
    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 3
    qtbot.keyClicks(dialog.ratio_input, "6.78")
    assert len(dialog.invalid_fields) == 1
    qtbot.mouseClick(dialog.dir_pz, QtCore.Qt.LeftButton, pos=QtCore.QPoint(2, int(dialog.dir_px.height() / 2)))
    assert dialog.dir_pz.isChecked()

    # assert no error
    assert len(dialog.invalid_fields) == 0

    # click apply
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    dict_data = dialog.parent.dict_polarized

    # assert values are added in parent dictionary
    assert dict_data["PolarizationState"] == "NSF_Pz"
    assert dict_data["FlippingRatio"] == "6.78"
    assert dict_data["SampleLog"] == ""

    dialog.close()


def test_apply_btn_invalid(qtbot):
    """Test for clicking apply with invalid fields"""
    red_parameters = ReductionParameters()
    dialog = PolarizedDialog(red_parameters)
    dialog.show()

    # spin x
    qtbot.mouseClick(dialog.state_no_spin, QtCore.Qt.LeftButton)

    # required fields
    assert len(dialog.invalid_fields) == 3
    # click apply

    completed = False

    # This is to handle modal dialogs
    def handle_dialog():
        nonlocal completed
        dialog.error.done(1)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_dialog))
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)
    dialog.close()