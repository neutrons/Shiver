"""
Contains the entry point for the application
"""

import sys
from qtpy.QtWidgets import QApplication

from mantidqt.gui_helper import set_matplotlib_backend

# make sure the algorithms have been loaded so they are available to the AlgorithmManager
import mantid.simpleapi  # noqa: F401
import shiver.models.makeslice  # noqa: F401 pylint: disable=unused-import
import shiver.models.ConvertDGSToSingleMDE  # noqa: F401 pylint: disable=unused-import

# make sure matplotlib is correctly set before we import shiver
set_matplotlib_backend()

from .shiver import Shiver  # noqa: E402 pylint: disable=wrong-import-position


def main():
    """
    Main entry point for Qt application
    """
    app = QApplication(sys.argv)
    window = Shiver()
    window.show()
    sys.exit(app.exec_())