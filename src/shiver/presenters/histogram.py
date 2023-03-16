"""Presenter for the Histogram tab"""


class HistogramPresenter:
    """Histogram presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self.view.histogram_parameters.connect_histogram_submit(self.handleButton)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model
        
    def handleButton(self, params_dict):
        print("HistogramPresenter")
        symmetry = params_dict['Symmetry']
        print(symmetry)
        self.model.symmetry_operations(symmetry)
