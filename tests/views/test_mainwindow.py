"""UI tests for the application"""
from shiver import Shiver, __version__


def test_mainwindow():
    """Test that the application starts successfully"""
    shiver = Shiver()
    shiver.show()

    assert shiver.isVisible()
    assert shiver.windowTitle() == f"SHIVER - {__version__}"
