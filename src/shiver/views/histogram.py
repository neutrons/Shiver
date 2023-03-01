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
)


class Histogram(QWidget):
    """Histogram widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.buttons = Buttons(self)
        self.input_workspaces = InputWorkspaces(self)
        self.histogram_parameters = HistogramParameter(self)
        self.histogram_workspaces = HistogramWorkspaces(self)

        layout = QHBoxLayout()
        layout.addWidget(self.buttons)
        layout.addWidget(self.input_workspaces)
        layout.addWidget(self.histogram_parameters)
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)


class Buttons(QWidget):
    """Buttons for Loading"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.load_dataset = QPushButton("Load dataset")
        self.gen_dataset = QPushButton("Generate dataset")
        self.load_mde = QPushButton("Load MDE")
        self.load_norm = QPushButton("Load normalization")

        layout = QVBoxLayout()
        layout.addWidget(self.load_dataset)
        layout.addWidget(self.gen_dataset)
        layout.addWidget(self.load_mde)
        layout.addWidget(self.load_norm)
        layout.addStretch()
        self.setLayout(layout)


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

        self.histogram_workspaces = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)
