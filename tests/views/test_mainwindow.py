"""UI tests for the application"""
from shiver import Shiver


def test_mainwindow():
    """Test that the application starts successfully"""
    shiver = Shiver()
    shiver.show()

    assert shiver.isVisible()
    assert shiver.windowTitle() == "SHIVER"
