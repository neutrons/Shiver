"""
Adapter for the Histogram view to connect the presenter to the Trame state.
"""

class TrameHistogramViewAdapter:
    """
    An adapter that mimics the PyQt HistogramView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._histogram_submit_callback = None
        self._plot_display_name_callback = None

    def connect_histogram_submit(self, callback):
        self._histogram_submit_callback = callback

    def connect_plot_display_name_callback(self, callback):
        self._plot_display_name_callback = callback

    def get_plot_display_name(self):
        if self._plot_display_name_callback:
            return self._plot_display_name_callback()
        return ""

    def connect_make_slice_clicked(self, callback):
        # This is a UI event, so we don't need to do anything here.
        # The button click is handled by the controller.
        pass

    def connect_load_dataset(self, callback):
        pass

    def connect_load_file(self, callback):
        pass

    def connect_clone_workspace(self, callback):
        pass

    def connect_scale_workspace(self, callback):
        pass

    def connect_delete_workspace(self, callback):
        pass

    def connect_rename_workspace(self, callback):
        pass

    def connect_save_mde_workspace(self, callback):
        pass

    def connect_save_workspace(self, callback):
        pass

    def connect_save_workspace_to_ascii(self, callback):
        pass

    def connect_save_script_workspace(self, callback):
        pass

    def connect_save_polarization_state_workspace(self, callback):
        pass

    def connect_get_polarization_state_workspace(self, callback):
        pass

    def connect_corrections_tab(self, callback):
        pass

    def connect_refine_ub(self, callback):
        pass

    def connect_refine_ub_tab(self, callback):
        pass

    def connect_do_provenance_callback(self, callback):
        pass

    def connect_histogram_selected(self, callback):
        pass

    def show_error_message(self, msg, **kwargs):
        self.state.error_message = msg

    def show_warning_message(self, msg, **kwargs):
        # This would require a dialog in Trame.
        # For now, we will just log the warning.
        print(f"WARNING: {msg}")
        return True

    def makeslice_finish(self, workspace_dimensions, error=False):
        self.state.makeslice_in_progress = False
        if not error:
            self.state.plot_data = workspace_dimensions

    def ws_changed(self, action, name, ws_type, frame=None, ndims=0):
        # This would update the workspace lists in the UI.
        # For now, we will just log the change.
        print(f"Workspace changed: {action}, {name}, {ws_type}, {frame}, {ndims}")

    def add_ws(self, name, ws_type, frame, ndims):
        pass

    def del_ws(self, name):
        pass

    def clear_ws(self):
        pass

    def gather_workspace_data(self):
        return self.state.histogram_parameters.get("input_workspaces", [])

    def gather_workspace_background(self):
        return self.state.histogram_parameters.get("background_workspace")

    def gather_workspace_normalization(self):
        return self.state.histogram_parameters.get("normalization_workspace")

    def on_server_ready(self):
        """Called when the server is ready."""
        pass
