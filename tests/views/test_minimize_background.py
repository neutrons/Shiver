"""Test for the BackgroundMinimization widget"""
import os
import re
from qtpy import QtCore, QtWidgets
from shiver.views.minimize_background import MinimizeBackgroundOptions

color_search = re.compile("border-color: (.*);")


def test_background_options_grouping_file(qtbot):
    """Test the background minimization grouping file"""

    widget = MinimizeBackgroundOptions()
    qtbot.addWidget(widget)
    widget.show()

    widget.set_enabled(True)

    assert widget.group_path.text() == ""
    assert color_search.search(widget.group_path.styleSheet()).group(1) == "red"

    group_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/HYS_groups.xml"))

    # This is to handle modal dialogs
    def handle_dialog():
        # get a reference to the dialog and handle it here
        dialog = widget.findChild(QtWidgets.QFileDialog)
        # get a File Name field
        line_edit = dialog.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, group_file)
        qtbot.wait(100)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)

    # click the Browse button
    QtCore.QTimer.singleShot(100, handle_dialog)
    widget.group_browse.click()
    qtbot.wait(200)

    assert widget.group_path.text() == group_file
    assert widget.group_path.styleSheet() == ""


def test_background_options_min_max(qtbot):
    """Test the background minimization min/max options"""

    widget = MinimizeBackgroundOptions()
    qtbot.addWidget(widget)
    widget.show()

    widget.set_enabled(True)

    assert widget.percent_min.styleSheet() == ""
    assert widget.percent_max.styleSheet() == ""

    qtbot.keyClick(widget.percent_min, QtCore.Qt.Key_Backspace)
    qtbot.keyClicks(widget.percent_min, "50")

    assert color_search.search(widget.percent_min.styleSheet()).group(1) == "red"
    assert color_search.search(widget.percent_max.styleSheet()).group(1) == "red"

    qtbot.keyClick(widget.percent_max, QtCore.Qt.Key_Backspace)
    qtbot.keyClick(widget.percent_max, QtCore.Qt.Key_Backspace)
    qtbot.keyClicks(widget.percent_max, "75")
    assert widget.percent_min.styleSheet() == ""
    assert widget.percent_max.styleSheet() == ""

    qtbot.keyClick(widget.percent_min, QtCore.Qt.Key_Backspace)
    qtbot.keyClick(widget.percent_min, QtCore.Qt.Key_Backspace)
    assert color_search.search(widget.percent_min.styleSheet()).group(1) == "red"
    assert color_search.search(widget.percent_max.styleSheet()).group(1) == "red"

    qtbot.keyClick(widget.percent_max, QtCore.Qt.Key_Backspace)
    qtbot.keyClick(widget.percent_max, QtCore.Qt.Key_Backspace)
    assert widget.percent_min.styleSheet() == ""
    assert widget.percent_max.styleSheet() == ""
