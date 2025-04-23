"""UI tests for the application"""

import functools
from qtpy import QtCore

from shiver import Shiver, __version__


def test_mainwindow(qtbot):
    """Test that the application starts successfully"""
    shiver = Shiver()
    shiver.show()
    qtbot.waitUntil(shiver.show, timeout=5000)
    assert shiver.isVisible()
    assert shiver.windowTitle() == f"SHIVER - {__version__}"


def test_conf_button(qtbot):
    """Test that the configuration settings button starts the dialog successfully"""
    shiver = Shiver()
    shiver.show()
    qtbot.waitUntil(shiver.show, timeout=5000)
    assert shiver.isVisible()
    assert shiver.windowTitle() == f"SHIVER - {__version__}"
    assert shiver.main_window.config.valid is True
    completed = False

    # This is to handle modal dialogs
    def handle_dialog():
        nonlocal completed

        qtbot.mouseClick(shiver.main_window.dialog.btn_cancel, QtCore.Qt.LeftButton)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog))
    # push the Nexus button
    qtbot.mouseClick(shiver.main_window.conf_button, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)
