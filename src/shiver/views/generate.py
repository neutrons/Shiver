"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QGroupBox,
    QPushButton,
)
from .data import RawData


class Generate(QWidget):
    """Histogram widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        layout.setRowMinimumHeight(1, 200)
        layout.setRowMinimumHeight(2, 200)
        layout.setColumnMinimumWidth(1, 400)
        layout.setColumnMinimumWidth(2, 400)
        layout.setColumnMinimumWidth(3, 400)

        layout.addWidget(RawData(self), 1, 1)
        layout.addWidget(Oncat(self), 2, 1)
        layout.addWidget(MDEType(self), 1, 2)
        layout.addWidget(ReductionParameters(self), 2, 2)
        layout.addWidget(Buttons(self), 1, 3, 2, 1)

        self.setLayout(layout)


class Oncat(QGroupBox):
    """ONCat widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Oncat")


class MDEType(QGroupBox):
    """MDE type widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("MDE type")


class ReductionParameters(QGroupBox):
    """Generate reduction parameter widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Reduction Parameters")


class Buttons(QWidget):
    """Processing buttons"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Generate"))
        layout.addWidget(QPushButton("Save settings"))
        layout.addStretch()
        self.setLayout(layout)
