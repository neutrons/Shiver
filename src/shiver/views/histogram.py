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


class HistogramParameter(QGroupBox):
    """Histogram parameters widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram parameters")

        layout = QVBoxLayout()

        projections = QWidget()
        playout = QFormLayout()
        playout.addRow("Name", QLineEdit("Plot 1"))
        playout.addRow("Projection u", QLineEdit("1,0,0"))
        playout.addRow("Projection v", QLineEdit("0,1,0"))
        playout.addRow("Projection w", QLineEdit("0,0,1"))
        projections.setLayout(playout)

        layout.addWidget(projections)

        dimensions_count = QWidget()
        dclayout = QHBoxLayout()
        cut_1d = QRadioButton("1D cut")
        cut_1d.setChecked(True)
        dclayout.addWidget(cut_1d)
        dclayout.addWidget(QRadioButton("2D slice"))
        dclayout.addWidget(QRadioButton("3D volume"))
        dclayout.addWidget(QRadioButton("4D volume"))
        dimensions_count.setLayout(dclayout)

        layout.addWidget(dimensions_count)

        layout.addWidget(Dimensions())

        symmetry = QWidget()

        slayout = QFormLayout()
        slayout.addRow("Symmetry operations", QLineEdit())
        slayout.addRow("Smoothing", QDoubleSpinBox())
        symmetry.setLayout(slayout)

        layout.addWidget(symmetry)

        layout.addStretch()

        layout.addWidget(QPushButton("Histogram"))

        self.setLayout(layout)


class Dimensions(QWidget):
    """Widget for handling the selection of output dimensions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        layout.addWidget(QLabel("Dimensions"), 0, 0)
        layout.addWidget(QLabel("Minimum"), 0, 1)
        layout.addWidget(QLabel("Maximum"), 0, 2)
        layout.addWidget(QLabel("Step"), 0, 3)

        combo1 = QComboBox()
        combo1.addItems(["H,0,0", "0,K,0", "0,0,L", "DeltaE"])

        layout.addWidget(combo1, 1, 0)
        layout.addWidget(QLineEdit(), 1, 1)
        layout.addWidget(QLineEdit(), 1, 2)
        layout.addWidget(QLineEdit(), 1, 3)

        combo2 = QComboBox()
        combo2.addItems(["H,0,0", "0,K,0", "0,0,L", "DeltaE"])
        combo2.setCurrentIndex(1)

        layout.addWidget(combo2, 2, 0)
        layout.addWidget(QLineEdit(), 2, 1)
        layout.addWidget(QLineEdit(), 2, 2)
        layout.addWidget(QLineEdit(), 2, 3)

        combo3 = QComboBox()
        combo3.addItems(["H,0,0", "0,K,0", "0,0,L", "DeltaE"])
        combo3.setCurrentIndex(2)

        layout.addWidget(combo3, 3, 0)
        layout.addWidget(QLineEdit(), 3, 1)
        layout.addWidget(QLineEdit(), 3, 2)

        combo4 = QComboBox()
        combo4.addItems(["H,0,0", "0,K,0", "0,0,L", "DeltaE"])
        combo4.setCurrentIndex(3)

        layout.addWidget(combo4, 4, 0)
        layout.addWidget(QLineEdit(), 4, 1)
        layout.addWidget(QLineEdit(), 4, 2)

        self.setLayout(layout)


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
