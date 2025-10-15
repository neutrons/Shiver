"""Model for the Configuration Settings dialog"""

from mantid.kernel import Logger

logger = Logger("SHIVER")


class ConfigurationModel:
    """Configuration model"""

    def __init__(self):
        """constructor to create a configuration model"""
        self.settings = {}

    def add_setting(self, name, value, conf_type, section, allowed_values, comments, readonly):
        """add settings"""
        setting = UserSettingModel(name, value, conf_type, section, allowed_values, comments, readonly)
        self.settings[setting.name] = setting
        return setting

    def get_settings(self):
        """return settings"""
        return self.settings

    def update_settings_values(self, settings):
        """update settings"""
        for name, data in settings.items():
            self.settings[name].set_value(data["value"])


class UserSettingModel:  # noqa: R0903 pylint: disable=too-few-public-methods
    """User Configuration Setting model"""

    def __init__(self, name, value, set_type, section, allowed_values, comments, readonly):
        """constructor to create a configuration setting"""

        self.name = name
        self.value = value
        self.set_type = set_type
        self.section = section
        self.allowed_values = allowed_values
        self.comments = comments
        self.readonly = readonly

    def set_value(self, value):
        """set user's data value"""
        self.value = value
