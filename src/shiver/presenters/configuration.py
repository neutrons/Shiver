"""Presenter for the Configuration Parameters dialog"""

import json
from shiver.configuration import get_data


class ConfigurationPresenter:
    """Configuration Parameter presenter"""

    def __init__(self, view, model, config):
        self._view = view
        self._model = model
        self.config = config

        # connect populate callback
        self.view.connect_get_settings_callback(self.parse_user_configurations)
        self.view.connect_apply_submit(self.handle_apply_submit)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def parse_user_configurations(self):
        """parse the template json with all the field information,
        the user's configuration file for the values and store and return them for viewing"""
        # get all information from json
        template_file_path = self.config.template_file_path
        fields_per_section = {}
        with open(template_file_path, encoding="utf-8") as file_descriptor:
            filedata = json.load(file_descriptor)
            for conf_variable in filedata.keys():
                section = filedata[conf_variable]["section"]
                user_value = get_data(section, conf_variable)
                setting = self.model.add_setting(
                    conf_variable,
                    user_value,
                    filedata[conf_variable]["type"],
                    section,
                    filedata[conf_variable]["allowed_values"],
                    filedata[conf_variable]["comments"],
                    filedata[conf_variable]["readonly"],
                )
                if section not in fields_per_section:
                    fields_per_section[section] = []
                fields_per_section[section].append(setting)

        return fields_per_section

    def handle_apply_submit(self, parameters):
        """update the configuration variables' values"""
        # update model
        self.model.update_settings_values(parameters)
        # update the file
        self.config.set_data(parameters)
