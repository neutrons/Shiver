"""
Contains the entry point for the application
"""

import sys
from qtpy.QtWidgets import QApplication

# make sure the algorithms have been loaded so they are available to the AlgorithmManager
import mantid.simpleapi  # noqa: F401
import shiver.models.makeslice  # noqa: F401 pylint: disable=unused-import

from .shiver import Shiver


def main():
    """
    Main entry point for Qt application
    """
    app = QApplication(sys.argv)
    window = Shiver()
    window.show()
    return app.exec_()
