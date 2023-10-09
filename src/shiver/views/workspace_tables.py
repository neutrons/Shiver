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
)

from qtpy.QtCore import Qt, Signal
from qtpy.QtGui import QCursor

from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel
from .invalid_styles import INVALID_QLISTWIDGET
from .plots import do_colorfill_plot, do_slice_viewer, plot_md_ws_from_names
from .workspace_icons import IconLegend, get_icon

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


class MDEList(ADSList):  # pylint: disable=too-many-public-methods
    """Special workspace list widget so that we can add a menu to each item"""

    def __init__(self, parent=None):
        super().__init__(parent, WStype="mde")
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self._data_u = None
        self._data_nsf = None
        self._data_sf = None
        self._background = None
        self.rename_workspace_callback = None
        self.delete_workspace_callback = None
        self.create_corrections_tab_callback = None
        self.do_provenance_callback = None
        self.save_polarization_state_callback = None
        self.get_polarization_state_callback = None

    def connect_save_polarization_state_workspace(self, callback):
        """connect a function to save the polarization state for workspace"""
        self.save_polarization_state_callback = callback

    def connect_get_polarization_state_workspace(self, callback):
        """connect a function to get the polariation state for workspace"""
        self.get_polarization_state_callback = callback

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
        pol_state = None
        if self.get_polarization_state_callback:
            pol_state = self.get_polarization_state_callback(selected_ws_name)
        menu = QMenu(self)

        if frame_value == Frame.QSample.value:
            data_submenu = menu.addMenu("Set as data")

            if selected_ws_name != self._data_u:
                selected_state = ""
                if pol_state is None or pol_state == "UP":
                    selected_state = "<--"
                unpol_data = QAction(f"Set as unpolarized data {selected_state}")
                unpol_data.triggered.connect(partial(self.set_data, selected_ws_name, "UP"))
                data_submenu.addAction(unpol_data)

            if selected_ws_name != self._data_nsf:
                selected_state = ""
                if pol_state == "NSF":
                    selected_state = "<--"
                data_nsf = QAction(f"Set as polarized NSF data {selected_state}")
                data_nsf.triggered.connect(partial(self.set_data, selected_ws_name, "NSF"))
                data_submenu.addAction(data_nsf)

            if selected_ws_name != self._data_sf:
                selected_state = ""
                if pol_state == "SF":
                    selected_state = "<--"
                data_sf = QAction(f"Set as polarized SF data {selected_state}")
                data_sf.triggered.connect(partial(self.set_data, selected_ws_name, "SF"))
                data_submenu.addAction(data_sf)

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
        provenance = QAction("Provenance")
        provenance.triggered.connect(partial(self.do_provenance, selected_ws_name))

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

    def do_provenance(self, workspace_name: str):
        """Method to open the provenance window

        Parameters
        ----------
        workspace_name : str
            Name of the workspace to open the provenance window for.
        """
        if self.do_provenance_callback:
            self.do_provenance_callback(workspace_name)  # pylint: disable=not-callable

    def set_data(self, name, pol_state):
        """method to set the selected workspace as data pol_state and update border color"""

        # current data workspace field
        pol_state_dict = {"SF": "_data_sf", "NSF": "_data_nsf", "UP": "_data_u"}
        pol_data = pol_state_dict[pol_state]

        # deselect other data workspaces that are not allowed based on the polarization rules
        not_allowed_workspaces = self.get_data_workspaces_not_allowed(pol_state)
        self.unset_selected_data(not_allowed_workspaces)

        # deselect the previous worskpaces state of this workspace with name
        self.unset_selected_states_with_name(name)

        # set the new workspace data state
        setattr(self, pol_data, name)

        # save the polarization state as a sample log
        if self.save_polarization_state_callback:
            self.save_polarization_state_callback(name, pol_state)

        item = self.findItems(name, Qt.MatchExactly)[0]
        item.setIcon(get_icon(pol_state))
        item.setSelected(True)
        self.set_field_valid_state(self)

        # if SF and NSF workspaces exist, background should be unselected
        if self._data_sf and self._data_nsf and self._background:
            if self.background is not None:
                self.unset_background(self.background)

    def set_background(self, name):
        """method to set the selected workspace as 'background' and update border color"""

        # if SF and NSF workspaces do not exist, background should can be set
        if self._data_sf is None or self._data_nsf is None or self._data_sf == name or self._data_nsf == name:
            if self._background:
                old_item = self.findItems(self._background, Qt.MatchExactly)[0]
                self._set_q_icon(old_item)
                old_item.setSelected(False)

            # remove the selected workspace from any other previous state
            self.unset_selected_states_with_name(name)
            # set the new one
            self._background = name

            item = self.findItems(name, Qt.MatchExactly)[0]
            item.setIcon(get_icon("background"))
            item.setSelected(True)

        # at least on data workspace should be selected
        self.validate_data_workspace_state()

    def unset_background(self, name):
        """method to unset the selected workspace as 'background'"""
        item = self.findItems(name, Qt.MatchExactly)[0]
        self._set_q_icon(item)
        item.setSelected(False)

        self._background = None

    def unset_selected_data(self, data_workspaces):
        """method to unset the selected workspaces in field defined by data_workspaces"""
        for data in data_workspaces:
            workspace = getattr(self, data)
            if workspace:
                # if item still exists in the list
                if self.findItems(workspace, Qt.MatchExactly):
                    old_item = self.findItems(workspace, Qt.MatchExactly)[0]
                    self._set_q_icon(old_item)
                    old_item.setSelected(False)
                setattr(self, data, None)

    def unset_selected_states_with_name(self, name):
        """method to unselect the workspace with name"""
        # defined in self
        data_workspaces = ["_background", "_data_u", "_data_nsf", "_data_sf"]
        same_name_workspaces = []
        # find all data workspaces fields that have name as value
        # Note there should be only one
        for data_workspace in data_workspaces:
            workspace = getattr(self, data_workspace)
            if workspace == name:
                same_name_workspaces.append(data_workspace)

        # deselect them
        if len(same_name_workspaces) > 0:
            self.unset_selected_data(same_name_workspaces)

    def get_data_workspaces_not_allowed(self, pol_state):
        """method to return unallowed data workspaces based on the polarization state"""
        if pol_state == "SF":
            # remove other unpolarized and SF workspaces: only 1 SF is allowed
            workspaces = ["_data_u", "_data_sf"]
        elif pol_state == "NSF":
            # remove other unpolarized and NSF workspaces: only 1 NSF is allowed
            workspaces = ["_data_u", "_data_nsf"]
        else:
            # remove other unpolarized, SF and NSF workspaces: only 1 unpolarized is allowed
            workspaces = ["_data_u", "_data_sf", "_data_nsf"]
        return workspaces

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

        # unselect the previous workspaces state of this workspace with name
        self.unset_selected_states_with_name(name)

        # at least one data workspace should be selected
        self.validate_data_workspace_state()

    def delete_ws(self, name):
        """method to delete the currently selected workspace"""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable

        # unselect the previous worskpaces state of this workspace with name
        self.unset_selected_states_with_name(name)

        # at least on data workspace should be selected
        self.validate_data_workspace_state()

    def validate_data_workspace_state(self):
        """method to check whether there is at least one selected data workspace and update boarder color-valid state"""

        # at least on data workspace: SF, NSF, UP should be selected
        selected_data = False
        all_data = [self._data_u, self._data_sf, self._data_nsf]
        for data in all_data:
            if data is not None:
                selected_data = True
                break
        if selected_data is False:
            self.set_field_invalid_state(self)

    def _set_q_icon(self, item):
        item.setIcon(get_icon(Frame(item.type()).name))

    def all_data(self):
        """return all the selected data workspace names"""
        workspaces = []
        if self._data_u:
            workspaces.append(self._data_u)
        if self._data_nsf:
            workspaces.append(self._data_nsf)
        if self._data_sf:
            workspaces.append(self._data_sf)
        return workspaces

    @property
    def data(self):
        """return unpolarized data"""
        return self.data_u

    @property
    def data_u(self):
        """return the workspace name set as unpolarized data"""
        return self._data_u

    @property
    def data_nsf(self):
        """return the workspace name set as polarized no spinflip data"""
        return self._data_nsf

    @property
    def data_sf(self):
        """return the workspace name set as polarized spinflip data"""
        return self._data_sf

    @property
    def background(self):
        """return the workspace name set as background (optional, may be None)"""
        return self._background

    def unset_all(self):
        """reset the list and update border color"""

        data_workspaces = ["_data_u", "_data_sf", "_data_nsf"]
        self.unset_selected_data(data_workspaces)
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
            self,
            "Select location to save script",
            "",
            "Python script (*.py);;All files (*)",
            options=QFileDialog.DontUseNativeDialog,
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
            self,
            "Select location to save workspace",
            "",
            "NeXus file (*.nxs);;All files (*)",
            options=QFileDialog.DontUseNativeDialog,
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
            self,
            "Select location to save workspace",
            "",
            "ASCII file (*.dat);;All files (*)",
            options=QFileDialog.DontUseNativeDialog,
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
