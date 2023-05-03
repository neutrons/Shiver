"""UI tests for Reduction Parameters widget: input values"""
import os
from functools import partial
from qtpy import QtCore, QtWidgets
from shiver.views.generate import Generate


def test_reduction_parameters_mask_valid_input(qtbot):
    """Test for adding valid inputs in reduction parameters mask"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    nexus_path = str(os.path.abspath(processed_sample_file))

    completed = False

    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.mask_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_dialog, str(nexus_path)))
    # push the browse button
    qtbot.mouseClick(red_params.mask_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    assert red_params.mask_path.text().endswith(nexus_path) is True


def test_reduction_parameters_norm_valid_input(qtbot):
    """Test for adding valid inputs in reduction parameters norm"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    nexus_path = str(os.path.abspath(processed_sample_file))

    completed = False

    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.norm_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_dialog, str(nexus_path)))
    # push the browse button
    qtbot.mouseClick(red_params.norm_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    assert red_params.norm_path.text().endswith(nexus_path) is True


def test_reduction_parameters_text_valid_input(qtbot):
    """Test for adding valid inputs in reduction parameters ei and t0"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    qtbot.keyClicks(red_params.ei_input, "72.94")
    qtbot.keyClicks(red_params.t0_input, "18.09")

    assert red_params.ei_input.text() == "72.94"
    assert red_params.t0_input.text() == "18.09"


def test_reduction_parameters_text_invalid_input(qtbot):
    """Test for adding invalid inputs in reduction parameters ei and t0"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    qtbot.keyClicks(red_params.ei_input, "-a")
    qtbot.keyClicks(red_params.t0_input, "a")

    assert red_params.ei_input.text() == ""
    assert red_params.t0_input.text() == ""


def test_reduction_parameters_get_data_first_level(qtbot):
    """Test for retrieving all reduction parameters from initial widget"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)
    red_params = generate.reduction_parameters

    # mask input
    processed_mask_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    mask_path = str(os.path.abspath(processed_mask_file))

    completed = False

    # This is to handle modal dialogs
    def handle_mask_dialog(mask_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.mask_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, mask_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_mask_dialog, str(mask_path)))
    # push the browse button
    qtbot.mouseClick(red_params.mask_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    # norm input
    processed_norm_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/HYS_371495.nxs.h5")
    norm_path = str(os.path.abspath(processed_norm_file))

    completed = False

    # This is to handle modal dialogs
    def handle_norm_dialog(norm_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.norm_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, norm_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    QtCore.QTimer.singleShot(500, partial(handle_norm_dialog, str(norm_path)))
    # push the browse button
    qtbot.mouseClick(red_params.norm_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    qtbot.keyClicks(red_params.ei_input, "85.49")
    qtbot.keyClicks(red_params.t0_input, "10")

    # get data
    reduction_data = red_params.get_reduction_params_dict()

    # check first layer reduction parameters
    assert reduction_data["mask_path"].endswith(mask_path) is True
    assert reduction_data["norm_path"].endswith(norm_path) is True
    assert reduction_data["ei_input"] == red_params.ei_input.text()
    assert reduction_data["t0_input"] == red_params.t0_input.text()
