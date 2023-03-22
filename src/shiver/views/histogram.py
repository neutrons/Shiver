"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QGridLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QDoubleSpinBox,
    QErrorMessage,
)

from .loading_buttons import LoadingButtons
from .histogram_parameters import HistogramParameter


class Histogram(QWidget):
    """Histogram widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.buttons = LoadingButtons(self)
        self.input_workspaces = InputWorkspaces(self)
        self.histogram_parameters = HistogramParameter(self)
        self.histogram_workspaces = HistogramWorkspaces(self)

        layout = QHBoxLayout()
        layout.addWidget(self.buttons)
        layout.addWidget(self.input_workspaces)
        layout.addWidget(self.histogram_parameters)
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)

    def show_error_message(self, msg):
        """Will show a error dialog with the given message"""
        error = QErrorMessage()
        error.showMessage(msg)
        error.exec_()


class InputWorkspaces(QGroupBox):
    """MDE and Normalization workspace widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Input data in memory")

        self.mde_workspaces = QListWidget()
        self.norm_workspaces = QListWidget()

        layout = QHBoxLayout()
        layout.addWidget(self.mde_workspaces)
        layout.addWidget(self.norm_workspaces)
        self.setLayout(layout)


class HistogramWorkspaces(QGroupBox):
    """Histogram workspaces widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram data in memory")

        self.histogram_workspaces = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)
