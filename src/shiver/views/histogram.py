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
from qtpy.QtCore import Qt

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

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        self.input_workspaces.add_ws(name, ws_type)
        self.histogram_workspaces.add_ws(name, ws_type)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.input_workspaces.del_ws(name)
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.input_workspaces.clear_ws()
        self.histogram_workspaces.clear_ws()


class InputWorkspaces(QGroupBox):
    """MDE and Normalization workspace widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Input data in memory")

        self.mde_workspaces = ADSList(parent=self, WStype="mde")
        self.norm_workspaces = ADSList(parent=self, WStype="norm")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("MDE name"))
        layout.addWidget(self.mde_workspaces, stretch=2)
        layout.addWidget(QLabel("Normalization"))
        layout.addWidget(self.norm_workspaces, stretch=1)
        self.setLayout(layout)

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        self.mde_workspaces.add_ws(name, ws_type)
        self.norm_workspaces.add_ws(name, ws_type)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.mde_workspaces.del_ws(name)
        self.norm_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.mde_workspaces.clear()
        self.norm_workspaces.clear()


class ADSList(QListWidget):
    """List widget that will add and remove items from the ADS"""

    def __init__(self, parent=None, WStype=None):
        super().__init__(parent)
        self.ws_type = WStype
        self.setSortingEnabled(True)

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            self.addItem(name)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        for item in self.findItems(name, Qt.MatchExactly):
            self.takeItem(self.indexFromItem(item).row())


class HistogramWorkspaces(QGroupBox):
    """Histogram workspaces widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram data in memory")

        self.histogram_workspaces = ADSList(parent=self, WStype="mdh")
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        self.histogram_workspaces.add_ws(name, ws_type)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.histogram_workspaces.clear()
