"""Test for the RawData widget"""

import os
from qtpy import QtCore, QtWidgets
from shiver.views.data import RawData


def test_raw_data_get_selection(qtbot):
    """Test the browsing to path and selection of files"""

    raw_data = RawData()
    qtbot.addWidget(raw_data)
    raw_data.show()

    assert raw_data.files.count() == 0

    directory = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw"))

    # This is to handle modal dialogs
    def handle_dialog():
        # get a reference to the dialog and handle it here
        dialog = raw_data.findChild(QtWidgets.QFileDialog)
        # get a File Name field
        line_edit = dialog.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, directory)
        qtbot.wait(100)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)

    # click the Browse button
    QtCore.QTimer.singleShot(100, handle_dialog)
    raw_data.browse.click()

    qtbot.wait(200)

    assert raw_data.files.count() == 7
    assert raw_data.get_selected() == []

    # select 2nd and 4th items

    qtbot.wait(100)

    item = raw_data.files.item(1)
    assert item.text() == "HYS_178922.nxs.h5"
    qtbot.mouseClick(raw_data.files.viewport(), QtCore.Qt.LeftButton, pos=raw_data.files.visualItemRect(item).center())
    qtbot.wait(100)

    item = raw_data.files.item(3)
    assert item.text() == "HYS_178924.nxs.h5"
    qtbot.mouseClick(
        raw_data.files.viewport(),
        QtCore.Qt.LeftButton,
        modifier=QtCore.Qt.KeyboardModifier.ControlModifier,
        pos=raw_data.files.visualItemRect(item).center(),
    )
    qtbot.wait(100)

    assert raw_data.get_selected() == [
        os.path.join(directory, "HYS_178922.nxs.h5"),
        os.path.join(directory, "HYS_178924.nxs.h5"),
    ]


def test_raw_data_editing_path(qtbot):
    """Test the ability to edit the path directly"""

    raw_data = RawData()
    qtbot.addWidget(raw_data)
    raw_data.show()

    assert raw_data.files.count() == 0

    directory = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw"))

    qtbot.keyClicks(raw_data.path, directory)
    qtbot.keyClick(raw_data.path, QtCore.Qt.Key_Enter)

    qtbot.wait(100)

    assert raw_data.files.count() == 7
    assert raw_data.get_selected() == []

    # Add non-existing path, make sure list is empty
    qtbot.keyClicks(raw_data.path, "/does/not/exist")
    qtbot.keyClick(raw_data.path, QtCore.Qt.Key_Enter)

    qtbot.wait(100)

    assert raw_data.files.count() == 0
    assert raw_data.get_selected() == []


def test_raw_data_set_selection(qtbot):
    """Test setting the selected files"""
    raw_data = RawData()
    qtbot.addWidget(raw_data)
    raw_data.show()

    assert raw_data.files.count() == 0

    directory = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw"))
    files = ("HYS_178922.nxs.h5", "HYS_178923.nxs.h5", "HYS_178926.nxs.h5")
    filenames = [os.path.join(directory, f) for f in files]

    raw_data.set_selected(filenames)

    qtbot.wait(100)

    assert raw_data.files.count() == 7
    selected = raw_data.files.selectedItems()
    assert len(selected) == 3
    for item in selected:
        assert item.text() in files

    assert raw_data.get_selected() == filenames
