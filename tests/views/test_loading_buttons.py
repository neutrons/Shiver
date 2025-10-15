"""UI tests for LoadingButtons widget"""

import functools

from qtpy import QtCore, QtWidgets

from shiver.views.loading_buttons import LoadingButtons


def test_file_loading(qtbot, tmp_path):
    """Test for pressing the load buttons and checking that the callback function is called"""
    # create test data
    filename = tmp_path / "test.nxs"
    filename.write_text("data")

    # start widget
    buttons = LoadingButtons()
    qtbot.addWidget(buttons)
    buttons.show()

    # load file callback
    file_load_calls = []

    def load_file_callback(ws_type, filename):
        file_load_calls.append((ws_type, filename))

    buttons.connect_load_file(load_file_callback)

    # This is to handle modal dialogs
    def handle_dialog(filename):
        # get a reference to the dialog and handle it here
        dialog = buttons.findChild(QtWidgets.QFileDialog)
        # get a File Name field
        line_edit = dialog.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, filename)
        qtbot.wait(100)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)

    assert len(file_load_calls) == 0

    # click on load normalization
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(filename)))
    qtbot.mouseClick(buttons.load_norm, QtCore.Qt.LeftButton)

    qtbot.wait(100)

    assert len(file_load_calls) == 1
    assert file_load_calls[-1] == ("norm", str(filename))

    # click on load MDE
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(filename)))
    qtbot.mouseClick(buttons.load_mde, QtCore.Qt.LeftButton)

    qtbot.wait(100)

    assert len(file_load_calls) == 2
    assert file_load_calls[-1] == ("mde", str(filename))


def test_load_dataset_button(qtbot, tmp_path):
    """Test for pressing the load dataset button and checking that the callback function is called"""
    # create test data
    filename = tmp_path / "test.py"
    filename.write_text("def define_data_set(): return [{}]")

    # start widget
    buttons = LoadingButtons()
    qtbot.addWidget(buttons)
    buttons.show()

    # load dataset callback
    dataset_load_calls = []

    def load_dataset_callback(filename):
        dataset_load_calls.append(filename)

    buttons.connect_load_dataset(load_dataset_callback)

    # This is to handle modal dialogs
    def handle_dialog(filename):
        # get a reference to the dialog and handle it here
        dialog = buttons.findChild(QtWidgets.QFileDialog)
        # get a File Name field
        line_edit = dialog.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, filename)
        qtbot.wait(100)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)

    assert len(dataset_load_calls) == 0

    # click on load dataset
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(filename)))
    qtbot.mouseClick(buttons.load_dataset, QtCore.Qt.LeftButton)

    qtbot.wait(100)

    assert len(dataset_load_calls) == 1
