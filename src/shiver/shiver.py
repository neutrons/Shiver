"""
Main Qt application for shiver
"""

from qtpy.QtWidgets import QMainWindow
from shiver import __version__
from shiver.views.mainwindow import MainWindow


class Shiver(QMainWindow):
    """Main Shiver window"""

    __instance = None

    def __new__(cls):
        if Shiver.__instance is None:
            Shiver.__instance = QMainWindow.__new__(cls)  # pylint: disable=no-value-for-parameter
        return Shiver.__instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"SHIVER - {__version__}")
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
