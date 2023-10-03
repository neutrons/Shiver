"""
Contains the entry point for the application
"""

from .version import __version__  # noqa: F401


def Shiver():  # pylint: disable=invalid-name
    """This is needed for backward compatibility because mantid workbench does "from shiver import Shiver" """
    from .shiver import Shiver as shiver  # pylint: disable=import-outside-toplevel

    return shiver()
