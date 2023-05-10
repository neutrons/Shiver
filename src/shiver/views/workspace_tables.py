"""PyQt widget for the histogram tab input workspaces"""
from functools import partial
from enum import Enum
from qtpy.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QLabel,
    QMenu,
    QAction,
    QInputDialog,
    QAbstractItemView,
    QFileDialog,
    QWidget,
    QFormLayout,
)

from qtpy.QtCore import Qt, QSize, Signal
from qtpy.QtGui import QIcon, QPixmap, QCursor

import matplotlib.pyplot as plt
from mantidqt.widgets.sliceviewer.presenters.presenter import SliceViewer
from mantidqt.plotting.functions import manage_workspace_names, plot_md_ws_from_names

from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel
from .histogram_parameters import INVALID_QLISTWIDGET

Frame = Enum("Frame", {"None": 1000, "QSample": 1001, "QLab": 1002, "HKL": 1003})


class InputWorkspaces(QGroupBox):
    """MDE and Normalization workspace widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Input data in memory")

        self.mde_workspaces = MDEList(parent=self)
        self.mde_workspaces.setToolTip(
            "List of multidimensional event workspaces in memory."
            "\nUse context menus (left and right click) for selection/options."
        )
        self.norm_workspaces = NormList(parent=self)
        self.norm_workspaces.setToolTip(
            "List of processed normalization workspaces in memory. Use mouse click to select (Ctrl+click to unselect)."
        )

        layout = QVBoxLayout()
        layout.addWidget(QLabel("MDE name"))
        layout.addWidget(self.mde_workspaces, stretch=2)
        layout.addWidget(IconLegend(self))
        layout.addWidget(QLabel("Normalization"))
        layout.addWidget(self.norm_workspaces, stretch=1)
        self.setLayout(layout)

    def initialize_default(self):
        """initialize invalid style color due to absence of data"""
        self.mde_workspaces.initialize_default()

    def add_ws(self, name, ws_type, frame, ndims):
        """Adds a workspace to the list if it is of the correct type"""
        self.mde_workspaces.add_ws(name, ws_type, frame, ndims)
        self.norm_workspaces.add_ws(name, ws_type, frame, ndims)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.mde_workspaces.del_ws(name)
        self.norm_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.mde_workspaces.clear()
        self.norm_workspaces.clear()

    def set_field_invalid_state(self, item):
        """if parent exists then call the corresponding function to disable the button"""
        if self.parent():
            self.parent().set_field_invalid_state(item)

    def set_field_valid_state(self, item):
        """if parent exists then call the corresponding function to enable the button"""
        if self.parent():
            self.parent().set_field_valid_state(item)


class ADSList(QListWidget):
    """List widget that will add and remove items from the ADS"""

    def __init__(self, parent=None, WStype=None):
        super().__init__(parent)
        self.ws_type = WStype
        self.setSortingEnabled(True)

    def add_ws(self, name, ws_type, frame, ndims):  # pylint: disable=unused-argument
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            self.addItem(QListWidgetItem(name))

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        for item in self.findItems(name, Qt.MatchExactly):
            self.takeItem(self.indexFromItem(item).row())


class NormList(ADSList):
    """List widget that will add and remove items from the ADS"""

    def __init__(self, parent=None):
        super().__init__(parent, WStype="norm")
        self.rename_workspace_callback = None
        self.delete_workspace_callback = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self, pos):  # pylint: disable=invalid-name
        """right-click event handler"""
        selected_ws = self.itemAt(pos)
        if selected_ws is None:
            return

        selected_ws = selected_ws.text()

        menu = QMenu(self)

        rename = QAction("Rename")
        rename.triggered.connect(partial(self.rename_ws, selected_ws))

        menu.addAction(rename)

        delete = QAction("Delete")
        delete.triggered.connect(partial(self.delete_ws, selected_ws))

        menu.addAction(delete)

        menu.exec_(self.mapToGlobal(pos))
        menu.setParent(None)  # Allow this QMenu instance to be cleaned up

    def rename_ws(self, name):
        """method to rename the currently selected workspace"""
        dialog = QInputDialog(self)
        dialog.setLabelText(f"Rename {name} to:")
        dialog.setTextValue(name)
        dialog.setOkButtonText("Rename")
        if not dialog.exec_():
            return

        if self.rename_workspace_callback:
            self.rename_workspace_callback(name, dialog.textValue())  # pylint: disable=not-callable

    def delete_ws(self, name):
        """method to delete the currently selected workspace"""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable

    def set_selected(self, name):
        """method to set the selected workspace as selected

        Parameters
        ----------
        name : str
            Name of the workspace to select
        """
        # NOTE: norm list is in single selection mode, so we don't have to
        #       explicitly deselect the other items
        items = self.findItems(name, Qt.MatchExactly)
        if items:
            self.setCurrentItem(items[0])

    def deselect_all(self):
        """reset the list"""
        for item in self.selectedItems():
            item.setSelected(False)

    def get_selected(self):
        """method to get the selected workspace

        Returns
        -------
        str
            Name of the selected workspace
        """
        selected = self.selectedItems()
        if selected:
            return selected[0].text()
        return None


class MDEList(ADSList):
    """Special workspace list widget so that we can add a menu to each item"""

    def __init__(self, parent=None):
        super().__init__(parent, WStype="mde")
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self._data = None
        self._background = None
        self.rename_workspace_callback = None
        self.delete_workspace_callback = None
        self.create_corrections_tab_callback = None

    def initialize_default(self):
        """initialize invalid style color due to absence of data"""
        self.set_field_invalid_state(self)

    def add_ws(self, name, ws_type, frame, ndims):
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            frame_type = Frame[frame]
            item = QListWidgetItem(name, type=frame_type.value)
            self._set_q_icon(item)
            self.addItem(item)

    def mousePressEvent(self, event):  # pylint: disable=invalid-name
        """mouse click event handler"""
        selected_ws = self.itemAt(event.pos())

        if selected_ws is None:
            return

        frame_value = selected_ws.type()
        selected_ws_name = selected_ws.text()

        menu = QMenu(self)

        if selected_ws_name != self._data and frame_value == Frame.QSample.value:
            set_data = QAction("Set as data")
            set_data.triggered.connect(partial(self.set_data, selected_ws_name))
            menu.addAction(set_data)

        if selected_ws_name == self._background:
            background = QAction("Unset as background")
            background.triggered.connect(partial(self.unset_background, selected_ws_name))
        else:
            background = QAction("Set as background")
            background.triggered.connect(partial(self.set_background, selected_ws_name))

        sample_parameters = QAction("Set sample parameters")
        sample_parameters.triggered.connect(partial(self.set_sample, selected_ws_name))
        menu.addAction(sample_parameters)

        menu.addAction(background)
        menu.addAction(sample_parameters)
        menu.addSeparator()

        # data properties
        provenance = QAction("Provenance")  # To be implemented

        sample_parameters = QAction("Set sample parameters")
        sample_parameters.triggered.connect(partial(self.set_sample, selected_ws_name))

        corrections = QAction("Set corrections")
        corrections.triggered.connect(partial(self.set_corrections, selected_ws_name))

        menu.addAction(provenance)
        menu.addAction(sample_parameters)
        menu.addAction(corrections)
        menu.addSeparator()

        # data manipulation
        rename = QAction("Rename")
        rename.triggered.connect(partial(self.rename_ws, selected_ws_name))
        menu.addAction(rename)

        delete = QAction("Delete")
        delete.triggered.connect(partial(self.delete_ws, selected_ws_name))
        menu.addAction(delete)

        menu.exec_(QCursor.pos())
        menu.setParent(None)  # Allow this QMenu instance to be cleaned up

    def set_data(self, name):
        """method to set the selected workspace as 'data' and update border color"""
        if self._data:
            old_item = self.findItems(self._data, Qt.MatchExactly)[0]
            self._set_q_icon(old_item)
            old_item.setSelected(False)

        if self._background == name:
            self._background = None
        self._data = name
        item = self.findItems(name, Qt.MatchExactly)[0]
        item.setIcon(get_icon("data"))
        self.set_field_valid_state(self)
        item.setSelected(True)

    def set_background(self, name):
        """method to set the selected workspace as 'background' and update border color"""
        if self._background:
            old_item = self.findItems(self._background, Qt.MatchExactly)[0]
            self._set_q_icon(old_item)
            old_item.setSelected(False)

        self._background = name
        if self._data == name:
            self._data = None
            self.set_field_invalid_state(self)
        item = self.findItems(name, Qt.MatchExactly)[0]
        item.setIcon(get_icon("background"))
        item.setSelected(True)

    def unset_background(self, name):
        """method to unset the selected workspace as 'background'"""
        item = self.findItems(name, Qt.MatchExactly)[0]
        self._set_q_icon(item)
        item.setSelected(False)

        self._background = None

    def set_corrections(self, name):
        """method to open the correction tab to apply correction for given workspace"""
        if self.create_corrections_tab_callback:
            self.create_corrections_tab_callback(name)  # pylint: disable=not-callable

    def set_sample(self, name):
        """method to set sample parameters in the selected workspace"""

        sample = SampleView()
        sample_model = SampleModel(name)
        SamplePresenter(sample, sample_model)

        # open the dialog
        dialog = sample.start_dialog()
        dialog.populate_sample_parameters()
        dialog.exec_()

    def rename_ws(self, name):
        """method to rename the currently selected workspace"""
        dialog = QInputDialog(self)
        dialog.setLabelText(f"Rename {name} to:")
        dialog.setTextValue(name)
        dialog.setOkButtonText("Rename")
        if not dialog.exec_():
            return

        if self.rename_workspace_callback:
            self.rename_workspace_callback(name, dialog.textValue())  # pylint: disable=not-callable

        if self._data == name:
            self._data = None
            self.set_field_invalid_state(self)
        if self._background == name:
            self._background = None

    def delete_ws(self, name):
        """method to delete the currently selected workspace"""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable

        if self._data == name:
            self._data = None
            self.set_field_invalid_state(self)
        if self._background == name:
            self._background = None

    def _set_q_icon(self, item):
        item.setIcon(get_icon(Frame(item.type()).name))

    @property
    def data(self):
        """return the workspace name set as data"""
        return self._data

    @property
    def background(self):
        """return the workspace name set as background (optional, may be None)"""
        return self._background

    def unset_all(self):
        """reset the list and update border color"""
        # NOTE: DO NOT change the order, this is the correct logic to unset
        #       the data and background
        if self.data is not None:
            self.set_background(self.data)
            self.set_field_invalid_state(self)
        if self.background is not None:
            self.unset_background(self.background)

    def set_field_invalid_state(self, item):
        """if parent exists then call the corresponding function and update the color"""
        if self.parent():
            self.parent().set_field_invalid_state(item)
        item.setStyleSheet(INVALID_QLISTWIDGET)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and its invalid style, if it was previously invalid
        and enable the corresponding button"""
        if self.parent():
            self.parent().set_field_valid_state(item)
        item.setStyleSheet("")


class HistogramWorkspaces(QGroupBox):
    """Histogram workspaces widget"""

    histogram_selected_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram data in memory")

        self.histogram_workspaces = MDHList(parent=self)
        self.histogram_workspaces.setToolTip("List of histogrammed data in memory. Use right click for options.")
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)
        self.histogram_workspaces.itemClicked.connect(self.on_item_clicked)

    def add_ws(self, name, ws_type, frame, ndims):
        """Adds a workspace to the list if it is of the correct type"""
        self.histogram_workspaces.add_ws(name, ws_type, frame, ndims)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.histogram_workspaces.clear()

    def on_item_clicked(self, item):
        """method to emit a signal when a workspace is selected"""
        self.histogram_selected_signal.emit(item.text())


class MDHList(ADSList):
    """List widget that will add and remove items from the ADS"""

    def __init__(self, parent=None):
        super().__init__(parent, WStype="mdh")
        self.delete_workspace_callback = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.save_callback = None
        self.save_to_ascii_callback = None
        self.save_script_callback = None
        self.plot_callback = None

    def contextMenu(self, pos):  # pylint: disable=invalid-name
        """right-click event handler"""
        selected_ws = self.itemAt(pos)
        if selected_ws is None:
            return

        ndims = selected_ws.type()
        selected_ws = selected_ws.text()

        menu = QMenu(self)

        if ndims == 1:
            plot = QAction("Plot 1D")
            plot.triggered.connect(partial(self.plot_1d, selected_ws, False, False))
            menu.addAction(plot)

            overplot = QAction("Overplot 1D")
            overplot.triggered.connect(partial(self.plot_1d, selected_ws, False, True))
            menu.addAction(overplot)

            plot_err = QAction("Plot 1D with errors")
            plot_err.triggered.connect(partial(self.plot_1d, selected_ws, True, False))
            menu.addAction(plot_err)

            overplot_err = QAction("Overplot 1D with errors")
            overplot_err.triggered.connect(partial(self.plot_1d, selected_ws, True, True))
            menu.addAction(overplot_err)
        elif ndims == 2:
            colorfill = QAction("Plot colorfill")
            colorfill.triggered.connect(partial(self.plot_2d, selected_ws))
            menu.addAction(colorfill)

        if ndims > 1:
            sliceviewer = QAction("Show Slice Viewer")
            sliceviewer.triggered.connect(partial(self.plot_slice_viewer, selected_ws))
            menu.addAction(sliceviewer)

        menu.addSeparator()

        script = QAction("Save Script")
        script.triggered.connect(partial(self.save_script, selected_ws))
        menu.addAction(script)

        save = QAction("Save Nexus Data")
        save.triggered.connect(partial(self.save_ws, selected_ws))
        menu.addAction(save)

        save_ascii = QAction("Save ASCII Data")
        save_ascii.triggered.connect(partial(self.save_ws_to_ascii, selected_ws))
        menu.addAction(save_ascii)

        menu.addSeparator()

        delete = QAction("Delete")
        delete.triggered.connect(partial(self.delete_ws, selected_ws))

        menu.addAction(delete)

        menu.exec_(self.mapToGlobal(pos))
        menu.setParent(None)  # Allow this QMenu instance to be cleaned up

    def add_ws(self, name, ws_type, frame, ndims):
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            self.addItem(QListWidgetItem(name, type=ndims))

    def plot_1d(self, name, errors, overplot):
        """method to do 1D plots"""
        plot_md_ws_from_names([name], errors, overplot)

    def plot_2d(self, name):
        """method to do 2D plots"""
        do_colorfill_plot([name])

    def plot_slice_viewer(self, name):
        """method to open sliceviewer"""
        do_slice_viewer([name], self)

    def save_script(self, name):
        """method to handle the saving of script"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select location to save script", "", "Python script (*.py);;All files (*)"
        )
        if filename and self.save_script_callback:
            self.save_script_callback(name, filename)  # pylint: disable=not-callable

    def save_ws(self, name: str):
        """Method to handle the saving data to NeXus file.

        Parameters
        ----------
        name
            name of the workspace to be saved
        """
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select location to save workspace", "", "NeXus file (*.nxs);;All files (*)"
        )
        if filename and self.save_callback:
            self.save_callback(name, filename)  # pylint: disable=not-callable

    def save_ws_to_ascii(self, name: str):
        """Method to handle the saving data to ASCII file.

        Parameters
        ----------
        name
            name of the workspace to be saved
        """
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select location to save workspace", "", "ASCII file (*.dat);;All files (*)"
        )

        # check if filename has a .dat or .csv extension
        if filename and not (filename.endswith(".dat") or filename.endswith(".csv")):
            filename += ".dat"

        if filename and self.save_to_ascii_callback:
            self.save_to_ascii_callback(name, filename)  # pylint: disable=not-callable

    def delete_ws(self, name):
        """Method to delete the currently selected workspace."""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable


class IconLegend(QWidget):
    """Legend for the icons in the MDE table"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout()

        q_sample = QLabel()
        q_sample.setPixmap(get_icon("QSample").pixmap(QSize(20, 14)))
        layout.addRow(q_sample, QLabel("Q-sample workspace"))

        q_lab = QLabel()
        q_lab.setPixmap(get_icon("QLab").pixmap(QSize(20, 14)))
        layout.addRow(q_lab, QLabel("Q-lab workspace"))

        data = QLabel()
        data.setPixmap(get_icon("data").pixmap(QSize(10, 14)))
        layout.addRow(data, QLabel("Selected data workspace"))

        bkg = QLabel()
        bkg.setPixmap(get_icon("background").pixmap(QSize(10, 14)))
        layout.addRow(bkg, QLabel("Selected background workspace"))

        self.setLayout(layout)


def get_icon(name: str) -> QIcon:
    """return a icon for the given name"""
    if name == "data":
        return QIcon(
            QPixmap(
                ["5 7 2 1", "N c None", ". c #0000FF", "...NN", ".NN.N", ".NNN.", ".NNN.", ".NNN.", ".NN.N", "...NN"]
            ).scaled(QSize(10, 14))
        )

    if name == "background":
        return QIcon(
            QPixmap(
                [
                    "5 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "....N",
                    ".NNN.",
                    ".NNN.",
                    "....N",
                    ".NNN.",
                    ".NNN.",
                    "....N",
                ]
            ).scaled(QSize(10, 14))
        )

    if name == "QSample":
        return QIcon(
            QPixmap(
                [
                    "10 7 2 1",
                    "N c None",
                    ". c #000000",
                    "N...NNNNNN",
                    ".NNN.NNNNN",
                    ".NNN.NN...",
                    ".NNN.N.NNN",
                    ".N.N.NN..N",
                    ".NN.NNNNN.",
                    "N..N.N...N",
                ]
            ).scaled(QSize(20, 14))
        )

    if name == "QLab":
        return QIcon(
            QPixmap(
                [
                    "10 7 2 1",
                    "N c None",
                    ". c #000000",
                    "N...NNNNNN",
                    ".NNN.NNNNN",
                    ".NNN.N.NNN",
                    ".NNN.N.NNN",
                    ".N.N.N.NNN",
                    ".NN.NN.NNN",
                    "N..N.N....",
                ]
            ).scaled(QSize(20, 14))
        )

    raise ValueError(f"{name} doesn't correspond to a valid icon")


@manage_workspace_names
def do_colorfill_plot(workspaces):
    """Create a colormesh plot for the provided workspace"""
    fig, axis = plt.subplots(subplot_kw={"projection": "mantid"})
    colormesh = axis.pcolormesh(workspaces[0])
    axis.set_title(workspaces[0].name())
    fig.colorbar(colormesh)
    fig.show()


@manage_workspace_names
def do_slice_viewer(workspaces, parent=None):
    """Open sliceviewer for the provided workspace"""
    presenter = SliceViewer(ws=workspaces[0], parent=parent)
    presenter.view.show()
