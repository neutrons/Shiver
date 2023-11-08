"""Tests for printing the version"""
import sys
from pytest import raises
from shiver.shiver import gui
from shiver.version import __version__


def test_show_show_version(monkeypatch, capsys):
    """Test starting the app with invalid configuration"""

    # capture system exit
    with raises(SystemExit):
        # mock command line arguments
        mock_sys_argv = sys.argv
        mock_sys_argv.append("--v")
        # with patch.object(sys, 'argv', mock_sys_argv):
        monkeypatch.setattr("sys.argv", mock_sys_argv)
        print("asrg", sys.argv)
        gui()
    output, error = capsys.readouterr()
    assert output.endswith(f"{__version__}\n")
    assert error == ""
