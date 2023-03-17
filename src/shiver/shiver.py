"""
Main Qt application for shiver
"""

from qtpy.QtWidgets import QMainWindow
from shiver.views.mainwindow import MainWindow


class Shiver(QMainWindow):
    """Main Shiver window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHIVER")
        self.main_window = MainWindow(self)
        self.setCentralWidget(self.main_window)
