"""UI tests for the application"""
from shiver import Shiver


def test_mainwindow(qtbot):
    """Test that the application starts successfully"""
    shiver = Shiver()
    qtbot.addWidget(shiver)
    shiver.show()

    assert shiver.isVisible()
    assert shiver.windowTitle() == "SHIVER"
