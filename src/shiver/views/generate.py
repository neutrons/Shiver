"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import QWidget


class Generate(QWidget):
    """Histogram widget"""

    def __init__(self, parent=None):
        super().__init__(parent)