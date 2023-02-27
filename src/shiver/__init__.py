"""
Contains the entry point for the application
"""

import sys
from qtpy.QtWidgets import QApplication
from .shiver import Shiver


def main():
    """
    Main entry point for Qt application
    """
    app = QApplication(sys.argv)
    window = Shiver()
    window.show()
    return app.exec_()
