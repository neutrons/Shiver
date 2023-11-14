from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QGridLayout,
    QLineEdit,
    QLabel,
    QGroupBox,
    QComboBox,
)
from qtpy.QtCore import Qt, QAbstractTableModel, QModelIndex

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


class PeaksTableModel(QAbstractTableModel):
    def __init__(self, data_model, parent=None):
        super().__init__(parent=parent)
        self._data_model = data_model
        self._headers = []
        self._refine = {}
        self._recenter = {}

    def rowCount(self, parent=QModelIndex()):
        return self._data_model.get_number_of_rows()

    def columnCount(self, parent=QModelIndex()):
        return 5

    def data(self, index, role=Qt.DisplayRole):
        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() > 1:
                return self._data_model.get_cell(index.row(), index.column() - 1)

        if role == Qt.CheckStateRole:
            if index.column() == 0:
                return Qt.CheckState.Checked if self._refine.get(index.row(), False) else Qt.CheckState.Unchecked
            if index.column() == 1:
                return Qt.CheckState.Checked if self._recenter.get(index.row(), False) else Qt.CheckState.Unchecked

        return None

    def setHorizontalHeaderLabels(self, labels):
        self._headers = labels

    def load_data(self, data_model):
        self.beginResetModel()
        self._refine = {}
        self._recenter = {}
        self._data_model = data_model
        self.endResetModel()

    def flags(self, index):
        if index.column() > 1:
            return super().flags(index) | Qt.ItemIsEditable | Qt.ItemIsSelectable

        return super().flags(index) | Qt.ItemIsUserCheckable

    def setData(self, index, value, role):
        if not index.isValid():
            return False

        if role == Qt.EditRole and index.column() > 1:
            try:
                self._data_model.set_cell_data(index.row(), index.column() - 1, value, False)
            except ValueError:
                return False

        if role == Qt.CheckStateRole:
            if index.column() == 0:
                self._refine[index.row()] = bool(value)
            elif index.column() == 1:
                self._recenter[index.row()] = bool(value)

        self.dataChanged.emit(index, index)
        return True

    def headerData(self, section, orientation, role):
        if role in (Qt.DisplayRole, Qt.EditRole) and orientation == Qt.Horizontal:
            if section < len(self._headers):
                return self._headers[section]
        else:
            return super().headerData(section, orientation, role)

    def recenter_rows(self):
        return sorted(k for k, v in self._recenter.items() if v)

    def refine_rows(self):
        return sorted(k for k, v in self._refine.items() if v)


class RefineUBView(QWidget):
    def __init__(self, sv, peaks_table, presenter, parent=None):
        super().__init__(parent)
        self.sv = sv
        self.presenter = presenter
        self.peaks_table = peaks_table
        self.setup_ui()
        self.populate_peaks_callback = None
        self.predict_peaks_callback = None
        self.recenter_peaks_callback = None

    def setup_ui(self):
        layout = QHBoxLayout()

        layout.addWidget(self.sv.view)

        peaks_layout = QVBoxLayout()

        self.populate_peaks = QPushButton("Populate Peaks")
        self.populate_peaks.setCheckable(True)
        self.populate_peaks.clicked.connect(self.populate_peaks_call)
        self.predict_peaks = QPushButton("Predict peaks")
        self.predict_peaks.clicked.connect(self.predict_peaks_call)
        self.recenter_peaks = QPushButton("Recenter")
        self.recenter_peaks.clicked.connect(self.recenter_peaks_call)

        peaks_layout.addWidget(self.populate_peaks)
        peaks_layout.addWidget(self.predict_peaks)
        peaks_layout.addWidget(self.recenter_peaks)
        peaks_layout.addWidget(self.peaks_table.view)

        layout.addLayout(peaks_layout)

        vlayout = QVBoxLayout()
        plot_layout = QHBoxLayout()
        self.canvas1 = FigureCanvas(Figure(figsize=(2, 2)))
        plot_layout.addWidget(self.canvas1)
        self.canvas2 = FigureCanvas(Figure(figsize=(2, 2)))
        plot_layout.addWidget(self.canvas2)
        self.canvas3 = FigureCanvas(Figure(figsize=(2, 2)))
        plot_layout.addWidget(self.canvas3)
        vlayout.addLayout(plot_layout)

        lattice = QGroupBox("Lattice")
        lattice_layout = QGridLayout()
        lattice_layout.addWidget(QLabel("a:"), 0, 0)
        lattice_layout.addWidget(QLabel("alpha:"), 1, 0)
        self.a = QLineEdit()
        self.a.setReadOnly(True)
        self.alpha = QLineEdit()
        self.alpha.setReadOnly(True)
        lattice_layout.addWidget(self.a, 0, 1)
        lattice_layout.addWidget(self.alpha, 1, 1)
        lattice_layout.addWidget(QLabel("b:"), 0, 2)
        lattice_layout.addWidget(QLabel("beta:"), 1, 2)
        self.b = QLineEdit()
        self.b.setReadOnly(True)
        self.beta = QLineEdit()
        self.beta.setReadOnly(True)
        lattice_layout.addWidget(self.b, 0, 3)
        lattice_layout.addWidget(self.beta, 1, 3)
        lattice_layout.addWidget(QLabel("c:"), 0, 4)
        lattice_layout.addWidget(QLabel("gamma:"), 1, 4)
        self.c = QLineEdit()
        self.c.setReadOnly(True)
        self.gamma = QLineEdit()
        self.gamma.setReadOnly(True)
        lattice_layout.addWidget(self.c, 0, 5)
        lattice_layout.addWidget(self.gamma, 1, 5)

        lattice_layout.addWidget(QLabel("Lattice type:"), 2, 0, 1, 2)
        combobox = QComboBox()
        combobox.addItems(
            ["", "Cubic", "Hexagonal", "Rhombohedral", "Tetragonal", "Orthorhombic", "Monoclinic", "Triclinic"]
        )
        lattice_layout.addWidget(combobox, 2, 2, 1, 4)

        self.refine_orientation_btn = QPushButton("Refine orientation only")
        self.refine_orientation_btn.clicked.connect(self.refine_orientation_call)
        lattice_layout.addWidget(self.refine_orientation_btn, 0, 6)
        self.refine_btn = QPushButton("Refine")
        self.refine_btn.clicked.connect(self.refine_call)
        lattice_layout.addWidget(self.refine_btn, 1, 6)
        self.undo_btn = QPushButton("Undo")
        lattice_layout.addWidget(self.undo_btn, 2, 6)
        lattice.setLayout(lattice_layout)

        vlayout.addWidget(lattice)
        vlayout.addStretch()

        self.close = QPushButton("Close")
        vlayout.addWidget(self.close)

        layout.addLayout(vlayout)
        self.setLayout(layout)

    def remove_sv(self):
        self.layout().removeWidget(self.sv.view)

    def set_sv(self, sv):
        self.layout().insertWidget(0, sv.view)
        self.sv = sv

    def connect_populate_peaks(self, callback):
        self.populate_peaks_callback = callback

    def populate_peaks_call(self, checked):
        if self.populate_peaks_callback:
            self.populate_peaks_callback(checked)

    def connect_predict_peaks(self, callback):
        self.predict_peaks_callback = callback

    def predict_peaks_call(self):
        if self.predict_peaks_callback:
            self.predict_peaks_callback()

    def connect_recenter_peaks(self, callback):
        self.recenter_peaks_callback = callback

    def recenter_peaks_call(self):
        if self.recenter_peaks_callback:
            self.recenter_peaks_callback()

    def connect_refine(self, callback):
        self.refine_callback = callback

    def refine_call(self):
        if self.refine_callback:
            self.refine_callback()

    def connect_refine_orientation(self, callback):
        self.refine_orientation_callback = callback

    def refine_orientation_call(self):
        if self.refine_orientation_callback:
            self.refine_orientation_callback()

    def set_lattice(self, parameters):
        self.a.setText(str(parameters["a"]))
        self.alpha.setText(str(parameters["alpha"]))
        self.b.setText(str(parameters["b"]))
        self.beta.setText(str(parameters["beta"]))
        self.c.setText(str(parameters["c"]))
        self.gamma.setText(str(parameters["gamma"]))
