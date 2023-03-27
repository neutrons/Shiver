"""PyQt widget for the correction tab"""
from qtpy.QtWidgets import QWidget

class Corrections(QWidget):
    """Correction widget"""
    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.ws_name = name
