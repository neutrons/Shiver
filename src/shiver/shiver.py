"""
Main Qt application for shiver
"""

import sys
from qtpy.QtWidgets import QApplication, QMainWindow

from mantid.kernel import Logger
from mantidqt.gui_helper import set_matplotlib_backend

# make sure matplotlib is correctly set before we import shiver
set_matplotlib_backend()

# make sure the algorithms have been loaded so they are available to the AlgorithmManager
import mantid.simpleapi  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position

# Need to import the new algorithms so they are registered with mantid
import shiver.models.makeslice  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position
import shiver.models.makeslices  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position
import shiver.models.convert_dgs_to_single_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position
import shiver.models.generate_dgs_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position

from shiver.configuration import Configuration  # noqa: E402 pylint: disable=wrong-import-position
from shiver.version import __version__  # noqa: E402 pylint: disable=wrong-import-position
from shiver.views.mainwindow import MainWindow  # noqa: E402 pylint: disable=wrong-import-position

logger = Logger("SHIVER")


class Shiver(QMainWindow):
    """Main Shiver window"""

    __instance = None

    def __new__(cls):
        if Shiver.__instance is None:
            Shiver.__instance = QMainWindow.__new__(cls)  # pylint: disable=no-value-for-parameter
        return Shiver.__instance

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.information(f"Shiver version: {__version__}")
        config = Configuration()
        if not config.is_valid():
            msg = (
                "Error with configuration settings!",
                f"Check and update your file: {config.config_file_path}",
                "with the latest settings found here:",
                f"{config.template_file_path} and start the application again.",
            )

            print(" ".join(msg))
            sys.exit(-1)
        self.setWindowTitle(f"SHIVER - {__version__}")
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)


def gui():
    """
    Main entry point for Qt application
    """
    input_flags = sys.argv[1::]
    if "--v" in input_flags:
        print(__version__)
        sys.exit()
    else:
        app = QApplication(sys.argv)
        window = Shiver()
        window.show()
        sys.exit(app.exec_())
