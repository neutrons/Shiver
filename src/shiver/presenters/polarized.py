"""Presenter for the Polarized Options dialog"""


class PolarizedPresenter:
    """Polarized Options presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self.model.connect_error_message(self.error_message)

        # button
        self.view.connect_apply_submit(self.handle_apply_button)
        self.view.connect_populate_polarized_options(self.get_polarization_logs)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def error_message(self, msg):
        """Pass error message to the view"""
        self.view.get_error_message(msg)

    def get_polarization_logs(self):
        """Retrieve the values for the sample logs"""
        sample_log_data = self.model.get_polarization_logs()
        return create_dictionary_polarized_options(sample_log_data)

    def handle_apply_button(self, polarization_logs):
        """Save the values for the sample logs"""
        saved_logs = {}
        saved_logs.update(polarization_logs)
        # do not update psda value if readonly field
        if self.view.dialog.disable_psda:
            del saved_logs["PSDA"]
        else:
            saved_logs["psda"] = saved_logs["PSDA"]
            del saved_logs["PSDA"]
        self.model.save_polarization_logs(saved_logs)


def create_dictionary_polarized_options(sample_log_data):
    """Create a dictionary from the values for the sample logs"""
    # map the sample logs names requested to the actual sample logs saved in the workspace
    sample_log_data["PSDA"] = sample_log_data["psda"]
    del sample_log_data["psda"]
    return sample_log_data
