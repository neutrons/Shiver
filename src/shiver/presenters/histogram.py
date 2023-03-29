"""Presenter for the Histogram tab"""


class HistogramPresenter:
    """Histogram presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self.view.histogram_parameters.connect_histogram_submit(self.handle_button)

        self.view.buttons.connect_load_file(self.load_file)
        self.view.connect_delete_workspace(self.delete_workspace)
        self.view.connect_rename_workspace(self.rename_workspace)
        self.model.connect_error_message(self.error_message)

        self.model.ws_change_call_back(self.ws_changed)

    def load_file(self, file_type, filename):
        """Call model to load the filename from the UI file dialog"""
        self.model.load(filename, file_type)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def handle_button(self, params_dict):
        """Validate symmetry histogram parameter"""
        symmetry = params_dict["Symmetry"]
        self.model.symmetry_operations(symmetry)

    def error_message(self, msg):
        """Pass error message to the view"""
        self.view.show_error_message(msg)

    def ws_changed(self, action, name, ws_type, frame=None):
        """Pass the workspace change to the view"""
        if action == "add":
            self.view.add_ws(name, ws_type, frame)
        elif action == "del":
            self.view.del_ws(name)
        elif action == "clear":
            self.view.clear_ws()

    def delete_workspace(self, name):
        """Called by the view to delete a workspace"""
        self.model.delete(name)

    def rename_workspace(self, old_name, new_name):
        """Called by the view to rename a workspace"""
        self.model.rename(old_name, new_name)
