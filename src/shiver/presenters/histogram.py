"""Presenter for the Histogram tab"""


class HistogramPresenter:
    """Histogram presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self.view.histogram_parameters.connect_histogram_submit(self.handleButton)

        self.view.buttons.connect_load_file(self.load_file)
        self.model.connect_error_message(self.error_message)

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
        
    def handleButton(self, params_dict):
        symmetry = params_dict['Symmetry']
        self.model.symmetry_operations(symmetry)

    def error_message(self, msg):
        """Pass error message to the view"""
        self.view.show_error_message(msg)
