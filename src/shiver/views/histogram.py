"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QErrorMessage,
)
from qtpy.QtCore import Signal

from .loading_buttons import LoadingButtons
from .histogram_parameters import HistogramParameter
from .workspace_tables import InputWorkspaces, HistogramWorkspaces


class Histogram(QWidget):
    """Histogram widget"""

    error_message_signal = Signal(str)

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

        self.error_message_signal.connect(self._show_error_message)

    def show_error_message(self, msg):
        """Will show a error dialog with the given message

        This will emit a signal so that other threads can call this but have the GUI thread execute"""
        self.error_message_signal.emit(msg)

    def _show_error_message(self, msg):
        """Will show a error dialog with the given message from qt signal"""
        error = QErrorMessage(self)
        error.showMessage(msg)
        error.exec_()

    def add_ws(self, name, ws_type, frame=None):
        """Adds a workspace to the list if it is of the correct type"""
        self.input_workspaces.add_ws(name, ws_type, frame)
        self.histogram_workspaces.add_ws(name, ws_type, frame)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.input_workspaces.del_ws(name)
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.input_workspaces.clear_ws()
        self.histogram_workspaces.clear_ws()

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

    def connect_save_script_workspace(self, callback):
        """connect a function to the save script for workspace"""
        self.histogram_workspaces.histogram_workspaces.save_script_callback = callback

    def connect_corrections_tab(self, callback):
        """connect a function to the creation of a corrections tab"""
        self.input_workspaces.mde_workspaces.create_corrections_tab_callback = callback

    def gather_workspace_data(self) -> str:
        """Return the name of data workspace."""
        return self.input_workspaces.mde_workspaces.data

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
