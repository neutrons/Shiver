from qtpy.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton
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
                return Qt.CheckState.Checked if self._refine.get(index.row(), True) else Qt.CheckState.Unchecked
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


class RefineUBView(QWidget):
    def __init__(self, sv, peaks_table, parent=None):
        super().__init__(parent)
        self.sv = sv
        self.peaks_table = peaks_table
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()

        layout.addWidget(self.sv.view)

        peaks_layout = QVBoxLayout()

        self.populate_peaks = QPushButton("Populate Peaks")
        self.populate_peaks.setCheckable(True)
        self.predict_peaks = QPushButton("Predict peaks")
        self.recenter_peaks = QPushButton("Recenter")

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
        vlayout.addStretch()
        layout.addLayout(vlayout)

        self.setLayout(layout)
