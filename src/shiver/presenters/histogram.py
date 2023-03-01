"""Presenter for the Histogram tab"""


class HistogramPresenter:
    """Histogram presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model
