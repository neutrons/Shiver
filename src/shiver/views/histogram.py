"""PyQt widget for the histogram tab"""

from qtpy.QtCore import Signal
from qtpy.QtWidgets import QErrorMessage, QHBoxLayout, QMessageBox, QWidget

from shiver.configuration import get_data

from .histogram_parameters import HistogramParameter
from .loading_buttons import LoadingButtons
from .plots import do_default_plot
from .workspace_tables import HistogramWorkspaces, InputWorkspaces


class Histogram(QWidget):  # pylint: disable=too-many-public-methods
    """Histogram widget"""

    error_message_signal = Signal(str)
    makeslice_finish_signal = Signal(str, int)
    msg_queue = []

    def __init__(self, parent=None):
        super().__init__(parent)

        # check the state of the required fields
        # based on the fields states
        self.field_errors = []
        self.plot_display_name_callback = None
        self.refine_ub_tab_callback = None

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

        self.error_message_signal.connect(self._show_error_message)
        self.makeslice_finish_signal.connect(self._make_slice_finish)

        self.buttons.connect_error_msg(self.show_error_message)

        # initialize default value
        self.histogram_parameters.initialize_default()
        self.input_workspaces.initialize_default()

    def connect_plot_display_name_callback(self, callback):
        """callback for the display name-description for the plot"""
        self.plot_display_name_callback = callback

    def set_field_invalid_state(self, item):
        """include the item in the field_error list and disable the corresponding button"""
        if item not in self.field_errors:
            self.field_errors.append(item)
        self.histogram_parameters.histogram_btn.setEnabled(False)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and enable the corresponding button"""
        if item in self.field_errors:
            self.field_errors.remove(item)
        if len(self.field_errors) == 0:
            self.histogram_parameters.histogram_btn.setEnabled(True)

    def is_valid(self):
        """return whether the field_errors is empty"""
        return len(self.field_errors) == 0

    def disable_while_running(self, disable):
        """This will disable the UI elements for histgramming while MakeSlice is running"""
        self.input_workspaces.setDisabled(disable)
        self.histogram_parameters.setDisabled(disable)

    def make_slice_finish(self, ws_name, ndims):
        """Handle the UI updates for when MakeSlice has finished.

        This will emit a signal so that other threads can call this but have the GUI thread execute it.
        """
        self.makeslice_finish_signal.emit(ws_name, ndims)

    def _make_slice_finish(self, ws_name, ndims):
        if ws_name == "UB_refinement_workspace" and ndims == 3 and self.refine_ub_tab_callback:
            self.refine_ub_tab_callback()
        else:
            display_name, intensity_limits = self.get_plot_data(ws_name, ndims)
            do_default_plot(ws_name, ndims, display_name, intensity_limits)
            self.histogram_workspaces.histogram_workspaces.set_selected(ws_name)

    def show_error_message(self, msg, accumulate=False):
        """Will show a error dialog with the given message.

        This will emit a signal so that other threads can call this but have the GUI thread execute it.

        Parameters
        ----------
        msg : str
            The message to show
        accumulate : bool, optional
            If True, the error message will be accumulated and shown when accumulate is False
        """
        if not accumulate:
            msg = "\n".join(self.msg_queue) + "\n" + msg
            self.error_message_signal.emit(msg)
            self.msg_queue = []
        else:
            self.msg_queue.append(msg)

    def _show_error_message(self, msg):
        """Will show a error dialog with the given message from qt signal"""
        error = QErrorMessage(self)
        error.showMessage(msg)
        error.exec_()

    def show_warning_message(self, msg):
        """Will show a warning dialog with the given message and return button click as True/False"""
        warning_box = QMessageBox(self)
        warning_box.setIcon(QMessageBox.Information)
        warning_box.setText(msg)
        warning_box.setWindowTitle("NSF-SF Workspace Flipping Ratio Mismatch")
        warning_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        user_input = warning_box.exec()
        if user_input == QMessageBox.Ok:
            return True
        return False

    def add_ws(self, name, ws_type, frame=None, ndims=0):
        """Adds a workspace to the list if it is of the correct type"""
        self.input_workspaces.add_ws(name, ws_type, frame, ndims)
        self.histogram_workspaces.add_ws(name, ws_type, frame, ndims)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.input_workspaces.del_ws(name)
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.input_workspaces.clear_ws()
        self.histogram_workspaces.clear_ws()

    def connect_clone_workspace(self, callback):
        """connect a function to clone a workspace"""
        self.input_workspaces.mde_workspaces.clone_workspace_callback = callback

    def connect_scale_workspace(self, callback):
        """connect a function to scale the workspace"""
        self.input_workspaces.mde_workspaces.scale_workspace_callback = callback

    def connect_delete_workspace(self, callback):
        """connect a function to the selection of a filename"""
        self.input_workspaces.mde_workspaces.delete_workspace_callback = callback
        self.input_workspaces.norm_workspaces.delete_workspace_callback = callback
        self.histogram_workspaces.histogram_workspaces.delete_workspace_callback = callback

    def connect_rename_workspace(self, callback):
        """connect a function to the selection of a filename"""
        self.input_workspaces.mde_workspaces.rename_workspace_callback = callback
        self.input_workspaces.norm_workspaces.rename_workspace_callback = callback

    def connect_save_workspace(self, callback):
        """connect a function to the save a workspace"""
        self.histogram_workspaces.histogram_workspaces.save_callback = callback

    def connect_save_workspace_to_ascii(self, callback):
        """connect a function to the save a workspace to ascii"""
        self.histogram_workspaces.histogram_workspaces.save_to_ascii_callback = callback

    def connect_save_script_workspace(self, callback):
        """connect a function to the save script for workspace"""
        self.histogram_workspaces.histogram_workspaces.save_script_callback = callback

    def connect_corrections_tab(self, callback):
        """connect a function to the creation of a corrections tab"""
        self.input_workspaces.mde_workspaces.create_corrections_tab_callback = callback

    def connect_refine_ub(self, callback):
        """connect a function to the Refine sample parameters button"""
        self.input_workspaces.mde_workspaces.refine_ub_callback = callback

    def connect_refine_ub_tab(self, callback):
        """connect a function to the creation of a Refine UB tab"""
        self.refine_ub_tab_callback = callback

    def connect_do_provenance_callback(self, callback):
        """connect a function to the creation of a corrections tab.

        Parameters
        ----------
        callback : function
            The function to call when the provenance button is clicked.
        """
        self.input_workspaces.mde_workspaces.do_provenance_callback = callback

    def gather_workspace_data(self) -> list:
        """Return the name of data workspace unpolarized."""
        return self.input_workspaces.mde_workspaces.all_data()

    def gather_workspace_background(self):
        """Return the name of background workspace."""
        return self.input_workspaces.mde_workspaces.background

    def gather_workspace_normalization(self):
        """Return the name of normalization workspace."""
        # NOTE: since there is no explicit setting normalization
        #       workspace, we will use the first item from the
        #       selected list of normalization workspaces
        selected_items = self.input_workspaces.norm_workspaces.selectedItems()
        return None if len(selected_items) == 0 else selected_items[0].text()

    def set_data(self, data, pol_state):
        """Set the data unpolarized workspace and update its valid state."""
        self.input_workspaces.mde_workspaces.set_data(data, pol_state)
        self.set_field_valid_state(self.input_workspaces.mde_workspaces)

    def set_background(self, background):
        """Set the background workspace."""
        self.input_workspaces.mde_workspaces.set_background(background)

    def select_normalization(self, normalization):
        """Select the normalization workspace."""
        self.input_workspaces.norm_workspaces.set_selected(normalization)

    def get_selected_normalization(self):
        """Return the selected normalization workspace."""
        return self.input_workspaces.norm_workspaces.get_selected()

    def unset_all(self):
        """Unset all workspaces."""
        self.input_workspaces.mde_workspaces.unset_all()
        self.input_workspaces.norm_workspaces.deselect_all()
        self.set_field_invalid_state(self.input_workspaces.mde_workspaces)

    def get_plot_data(self, ws_name, ndims):
        """Get display name and intensities data for plotting."""
        plot_title_preference = get_data("main_tab.plot", "display_title")
        display_name = None
        if plot_title_preference == "full":
            display_name = self.plot_display_name_callback(ws_name, ndims)
        if plot_title_preference == "name_only":
            display_name = str(ws_name)
        min_intensity = self.histogram_parameters.dimensions.intensity_min.text()
        max_intensity = self.histogram_parameters.dimensions.intensity_max.text()
        intensity_limits = {
            "min": float(min_intensity) if min_intensity != "" else None,
            "max": float(max_intensity) if max_intensity != "" else None,
        }
        return (display_name, intensity_limits)
