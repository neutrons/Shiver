"""Tests for printing the version"""
import sys
from pytest import raises
from shiver.shiver import gui
from shiver.version import __version__


def test_show_version_v(monkeypatch, capsys):
    """Test for showing the version with --v"""

    # capture system exit
    with raises(SystemExit):
        # mock command line arguments
        mock_sys_argv = sys.argv
        mock_sys_argv.append("--v")
        monkeypatch.setattr("sys.argv", mock_sys_argv)
        gui()
    output, error = capsys.readouterr()
    assert output.endswith(f"{__version__}\n")
    assert error == ""


def test_show_version_version(monkeypatch, capsys):
    """Test for showing the version with --version"""

    # capture system exit
    with raises(SystemExit):
        # mock command line arguments
        mock_sys_argv = sys.argv
        mock_sys_argv.append("--version")
        monkeypatch.setattr("sys.argv", mock_sys_argv)
        gui()
    output, error = capsys.readouterr()
    assert output.endswith(f"{__version__}\n")
    assert error == ""
