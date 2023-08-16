"""Presenter for Configuration"""


class ConfigurationPresenter:
    """Configuration Parameter presenter"""

    def __init__(self, model, view):
        self._model = model
        self._view = view
        # connect get configuration settings from ConfigurationModel
        self.view.connect_get_config_callback(self.model.get_data)
        self.view.connect_valid_config_callback(self.model.is_valid)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model
