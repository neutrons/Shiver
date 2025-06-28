"""
Adapter for the Configuration view to connect the presenter to the Trame state.
"""

class TrameConfigurationViewAdapter:
    """
    An adapter that mimics the PyQt ConfigurationView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._get_settings_callback = None
        self._apply_submit_callback = None
        self._reset_submit_callback = None

    def connect_get_settings_callback(self, callback):
        """Connects the callback for getting the settings."""
        self._get_settings_callback = callback

    def connect_apply_submit(self, callback):
        """Connects the callback for applying the settings."""
        self._apply_submit_callback = callback

    def connect_reset_submit(self, callback):
        """Connects the callback for resetting the settings."""
        self._reset_submit_callback = callback

    def on_server_ready(self):
        """Called when the server is ready."""
        self.populate_fields()

    def populate_fields(self):
        """Populates the fields from the model."""
        if self._get_settings_callback:
            settings = self._get_settings_callback()
            self._update_state_from_settings(settings)

    def get_settings(self):
        """Gets the settings from the state."""
        return self._get_settings_from_state()

    def apply_submit(self):
        """Applies the settings from the state."""
        if self._apply_submit_callback:
            settings = self._get_settings_from_state()
            self._apply_submit_callback(settings)

    def reset_submit(self):
        """Resets the settings."""
        if self._reset_submit_callback:
            default_settings = self._reset_submit_callback()
            self._update_state_from_settings(default_settings)

    def _update_state_from_settings(self, settings):
        """Updates the Trame state from the settings dictionary."""
        flat_settings = {}
        for section, section_settings in settings.items():
            for setting in section_settings:
                flat_settings[setting.name] = {
                    "value": setting.value,
                    "type": setting.set_type,
                    "allowed_values": setting.allowed_values,
                    "readonly": setting.readonly,
                    "section": section,
                    "comments": setting.comments,
                }
        self.state.configuration_settings = flat_settings

    def _get_settings_from_state(self):
        """Gets the settings from the Trame state."""
        settings = {}
        for name, setting_data in self.state.configuration_settings.items():
            settings[name] = {
                "section": setting_data["section"],
                "value": setting_data["value"],
            }
        return settings
