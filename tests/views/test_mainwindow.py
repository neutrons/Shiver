"""UI tests for the application"""
from shiver import Shiver, __version__


def test_mainwindow(qtbot):
    """Test that the application starts successfully"""
    shiver = Shiver()
    shiver.show()
    qtbot.waitUntil(shiver.show, timeout=5000)
    assert shiver.isVisible()
    assert shiver.windowTitle() == f"SHIVER - {__version__}"
