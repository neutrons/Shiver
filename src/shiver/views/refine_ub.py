"""View for the Refine UB widget"""

import types
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

from matplotlib.backends.backend_qtagg import FigureCanvas  # pylint: disable=no-name-in-module
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt


class PeaksTableModel(QAbstractTableModel):
    """A QAbstractTableModel for use with a QTableView"""

    def __init__(self, data_model, parent=None):
        super().__init__(parent=parent)
        self._data_model = data_model
        self._headers = []
        self._refine = {}
        self._recenter = {}

    def rowCount(self, _):  # pylint: disable=invalid-name
        """Returns the number of rows"""
        return self._data_model.get_number_of_rows()

    def columnCount(self, _):  # pylint: disable=invalid-name
        """Returns the number of columns"""
        return 5

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data stored under the given role for the item referred to by the index."""
        if role in (Qt.DisplayRole, Qt.EditRole):
            if index.column() > 1:
                return self._data_model.get_cell(index.row(), index.column() - 1)

        if role == Qt.CheckStateRole:
            if index.column() == 0:
                return Qt.CheckState.Checked if self._refine.get(index.row(), False) else Qt.CheckState.Unchecked
            if index.column() == 1:
                return Qt.CheckState.Checked if self._recenter.get(index.row(), False) else Qt.CheckState.Unchecked

        return None

    def setHorizontalHeaderLabels(self, labels):  # pylint: disable=invalid-name
        """Update the attribute storing the header labels"""
        self._headers = labels

    def load_data(self, data_model):
        """update the data used in this model"""
        self.beginResetModel()
        self._data_model = data_model
        self.endResetModel()

    def flags(self, index):
        """Returns the item flags for the given index."""
        if index.column() > 1:
            return super().flags(index) | Qt.ItemIsEditable | Qt.ItemIsSelectable

        return super().flags(index) | Qt.ItemIsUserCheckable

    def setData(self, index, value, role):  # pylint: disable=invalid-name
        """Sets the role data for the item at index to value."""
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

    def headerData(self, section, orientation, role):  # pylint: disable=invalid-name
        """Returns the data for the given role and section in the header with the specified orientation."""
        if role in (Qt.DisplayRole, Qt.EditRole) and orientation == Qt.Horizontal and section < len(self._headers):
            return self._headers[section]

        return super().headerData(section, orientation, role)

    def recenter_rows(self):
        """Return a list of row number where "Recenter" box is checked"""
        return sorted(k for k, v in self._recenter.items() if v)

    def refine_rows(self):
        """Return a list of row number where "Refine" box is checked"""
        return sorted(k for k, v in self._refine.items() if v)

    def select_all(self):
        """Select all refine/recenter checkboxes"""
        self._refine = {n: True for n in range(self.rowCount(0))}
        self._recenter = {n: True for n in range(self.rowCount(0))}
        self.dataChanged.emit(QModelIndex(), QModelIndex())  # force view to redraw

    def deselect_all(self):
        """Deselect all refine/recenter checkboxes"""
        self._refine = {}
        self._recenter = {}
        self.dataChanged.emit(QModelIndex(), QModelIndex())  # force view to redraw

    def round_hkl(self):
        """Round all HKL values to integer"""
        for row in range(self.rowCount(0)):
            for index in range(1, 4):
                self._data_model.set_cell_data(row, index, round(self._data_model.get_cell(row, index)), False)

        self.dataChanged.emit(QModelIndex(), QModelIndex())  # force view to redraw


class RefineUBView(QWidget):
    """The view for the Refine UB widget"""

    def __init__(self, sliceviewer, peaks_table, presenter, parent=None):
        super().__init__(parent)
        self.sliceviewer = sliceviewer
        self.presenter = presenter
        self.peaks_table = peaks_table
        self.populate_peaks_callback = None
        self.predict_peaks_callback = None
        self.recenter_peaks_callback = None
        self.peak_selected_callback = None
        self.refine_callback = None
        self.refine_orientation_callback = None
        self.undo_callback = None
        self._selected_rows = None

        self._override_sliceviewer_methods()
        self._setup_ui()

    def _override_sliceviewer_methods(self):
        # disable setVisible so that the peaksviewer is never shown
        def _setVisible(self, visible):  # pylint: disable=unused-argument,invalid-name
            pass

        self.sliceviewer.view.peaks_view.setVisible = types.MethodType(_setVisible, self.sliceviewer.view.peaks_view)

        # force W_MATRIX to be used as projection matrix
        def _get_proj_matrix(self):
            return self.projection_matrix_from_log(self._get_ws())

        self.sliceviewer.model.get_proj_matrix = types.MethodType(_get_proj_matrix, self.sliceviewer.model)

    def _setup_ui(self):
        """setup all the UI layout and widgets"""
        layout = QHBoxLayout()

        layout.addWidget(self.sliceviewer.view)

        peaks_layout = QVBoxLayout()

        btn_layout = QGridLayout()
        self.populate_peaks = QPushButton("Populate Peaks")
        self.populate_peaks.setCheckable(True)
        self.populate_peaks.clicked.connect(self._populate_peaks_call)
        self.predict_peaks = QPushButton("Predict peaks")
        self.predict_peaks.clicked.connect(self._predict_peaks_call)
        self.recenter_peaks = QPushButton("Recenter")
        self.recenter_peaks.clicked.connect(self._recenter_peaks_call)

        self.select_all = QPushButton("Select All")
        self.select_all.clicked.connect(self._select_all_call)
        self.deselect_all = QPushButton("Deselect All")
        self.deselect_all.clicked.connect(self._deselect_all_call)
        self.round_hkl = QPushButton("Round HKL")
        self.round_hkl.clicked.connect(self._round_hkl_call)

        btn_layout.addWidget(self.populate_peaks, 0, 0)
        btn_layout.addWidget(self.predict_peaks, 0, 1)
        btn_layout.addWidget(self.recenter_peaks, 0, 2)
        btn_layout.addWidget(self.select_all, 1, 0)
        btn_layout.addWidget(self.deselect_all, 1, 1)
        btn_layout.addWidget(self.round_hkl, 1, 2)

        peaks_layout.addLayout(btn_layout)
        peaks_layout.addWidget(self.peaks_table.view)
        self.peaks_table.view.selectionModel().currentRowChanged.connect(self._on_row_selected)

        layout.addLayout(peaks_layout)

        vlayout = QVBoxLayout()
        plot_layout = QHBoxLayout()
        self.figure, self.axes = plt.subplots(1, 3, subplot_kw={"projection": "mantid"}, figsize=(8, 2))
        self.figure.tight_layout(w_pad=4)
        self.figure.set_layout_engine("tight")
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        plot_layout.addWidget(self.canvas)
        vlayout.addLayout(plot_layout)

        lattice = QGroupBox("Lattice")
        lattice_layout = QGridLayout()
        lattice_layout.addWidget(QLabel("a:"), 0, 0)
        lattice_layout.addWidget(QLabel("alpha:"), 1, 0)
        self.lattice_a = QLineEdit()
        self.lattice_a.setReadOnly(True)
        self.lattice_alpha = QLineEdit()
        self.lattice_alpha.setReadOnly(True)
        lattice_layout.addWidget(self.lattice_a, 0, 1)
        lattice_layout.addWidget(self.lattice_alpha, 1, 1)
        lattice_layout.addWidget(QLabel("b:"), 0, 2)
        lattice_layout.addWidget(QLabel("beta:"), 1, 2)
        self.lattice_b = QLineEdit()
        self.lattice_b.setReadOnly(True)
        self.lattice_beta = QLineEdit()
        self.lattice_beta.setReadOnly(True)
        lattice_layout.addWidget(self.lattice_b, 0, 3)
        lattice_layout.addWidget(self.lattice_beta, 1, 3)
        lattice_layout.addWidget(QLabel("c:"), 0, 4)
        lattice_layout.addWidget(QLabel("gamma:"), 1, 4)
        self.lattice_c = QLineEdit()
        self.lattice_c.setReadOnly(True)
        self.lattice_gamma = QLineEdit()
        self.lattice_gamma.setReadOnly(True)
        lattice_layout.addWidget(self.lattice_c, 0, 5)
        lattice_layout.addWidget(self.lattice_gamma, 1, 5)

        lattice_layout.addWidget(QLabel("Lattice type:"), 2, 0, 1, 2)
        self.lattice_type = QComboBox()
        self.lattice_type.addItems(
            ["", "Cubic", "Hexagonal", "Rhombohedral", "Tetragonal", "Orthorhombic", "Monoclinic", "Triclinic"]
        )
        lattice_layout.addWidget(self.lattice_type, 2, 2, 1, 4)

        self.refine_orientation_btn = QPushButton("Refine orientation only")
        self.refine_orientation_btn.clicked.connect(self.refine_orientation_call)
        lattice_layout.addWidget(self.refine_orientation_btn, 0, 6)
        self.refine_btn = QPushButton("Refine")
        self.refine_btn.clicked.connect(self.refine_call)
        lattice_layout.addWidget(self.refine_btn, 1, 6)
        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo_call)
        lattice_layout.addWidget(self.undo_btn, 2, 6)
        lattice.setLayout(lattice_layout)

        vlayout.addWidget(lattice)
        vlayout.addStretch()

        self.close_btn = QPushButton("Close")
        vlayout.addWidget(self.close_btn)

        layout.addLayout(vlayout)
        self.setLayout(layout)

    def remove_sliceviewer(self):
        """remove the current sliceviewer

        this will prevent issues when the workspace is updated"""
        self.layout().removeWidget(self.sliceviewer.view)

    def set_sliceviewer(self, sliceviewer):
        """insert the new sliceviewer into the layout"""
        self.layout().insertWidget(0, sliceviewer.view)
        self.sliceviewer = sliceviewer
        self._override_sliceviewer_methods()

    def connect_populate_peaks(self, callback):
        """connect the "populate peaks" button callback"""
        self.populate_peaks_callback = callback

    def _populate_peaks_call(self, checked):
        """call when "populate peaks" button pressed"""
        if self.populate_peaks_callback:
            self.populate_peaks_callback(checked)

    def connect_predict_peaks(self, callback):
        """connect the "predict peaks" button callback"""
        self.predict_peaks_callback = callback

    def _predict_peaks_call(self):
        """call when "predict peaks" button pressed"""
        if self.predict_peaks_callback:
            self.predict_peaks_callback()

    def connect_recenter_peaks(self, callback):
        """connect the recenter button callback"""
        self.recenter_peaks_callback = callback

    def _recenter_peaks_call(self):
        """call when recenter button pressed"""
        if self.recenter_peaks_callback:
            self.recenter_peaks_callback()

    def _select_all_call(self):
        """call when select all button pressed"""
        self.peaks_table.view.model().select_all()

    def _deselect_all_call(self):
        """call when deselect all button pressed"""
        self.peaks_table.view.model().deselect_all()

    def _round_hkl_call(self):
        """call when round HKL button pressed"""
        self.peaks_table.view.model().round_hkl()

    def connect_refine(self, callback):
        """connect the refine button callback"""
        self.refine_callback = callback

    def refine_call(self):
        """call when refine button pressed"""
        if self.refine_callback:
            self.refine_callback()

    def connect_refine_orientation(self, callback):
        """connect the refine orientation button callback"""
        self.refine_orientation_callback = callback

    def refine_orientation_call(self):
        """call when "refine orientation" button pressed"""
        if self.refine_orientation_callback:
            self.refine_orientation_callback()

    def connect_undo(self, callback):
        """connect the undo button callback"""
        self.undo_callback = callback

    def undo_call(self):
        """call when Undo button pressed"""
        if self.undo_callback:
            self.undo_callback()

    def set_lattice(self, parameters):
        """Update the lattice parameters widget from the parameters dict"""
        self.lattice_a.setText(str(parameters["a"]))
        self.lattice_alpha.setText(str(parameters["alpha"]))
        self.lattice_b.setText(str(parameters["b"]))
        self.lattice_beta.setText(str(parameters["beta"]))
        self.lattice_c.setText(str(parameters["c"]))
        self.lattice_gamma.setText(str(parameters["gamma"]))

    def get_lattice_type(self):
        """return the lattice type from the combobox"""
        return self.lattice_type.currentText()

    def _on_row_selected(self, selected, _):
        """Call the peak selection callback after row selected"""
        self._selected_rows = selected.row()
        if self.peak_selected_callback:
            self.peak_selected_callback(selected.row())

    def selected_rows(self):
        """return the currently selected rows in peak table"""
        return self._selected_rows

    def select_row(self, row):
        """Set which peaks is currently selected"""
        self.peaks_table.view.selectRow(row)

    def connect_peak_selection(self, callback):
        """Connect the peak selection callback"""
        self.peak_selected_callback = callback

    def plot_perpendicular_slice(self, centers, *slices):
        """Update the 3 plots with the workspace slices and draw peak positions"""
        for num, workspace in enumerate(slices):
            self.axes[num].cla()
            if workspace:
                self.axes[num].pcolormesh(workspace)
                x, y = centers[num]  # pylint: disable=invalid-name
                self.axes[num].plot((x - 0.1, x + 0.1), (y - 0.1, y + 0.1), color="r", lw=0.8)
                self.axes[num].plot((x - 0.1, x + 0.1), (y + 0.1, y - 0.1), color="r", lw=0.8)
                self.axes[num].set_aspect(1)

        self.canvas.draw_idle()
