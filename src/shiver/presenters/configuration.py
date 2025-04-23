"""Presenter for the Configuration Parameters dialog"""

import json
from shiver.configuration import get_data


class ConfigurationPresenter:
    """Configuration Parameter presenter"""

    def __init__(self, view, model, config):
        self._view = view
        self._model = model
        self.config = config

        # connect populate and apply callbacks
        self.view.connect_get_settings_callback(self.get_settings)
        self.view.connect_apply_submit(self.handle_apply_submit)
        self.view.connect_reset_submit(self.handle_reset_submit)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def get_settings(self):
        """return settings stored in memory or disk"""
        if self.model.get_settings():
            # get from the model
            fields = self.model.get_settings()
            sectioned_fields = {}
            for field in fields.values():
                section = field.section
                if section not in sectioned_fields:
                    sectioned_fields[section] = []
                sectioned_fields[section].append(field)
            return sectioned_fields
        # parse the user's and template json files
        sectioned_fields = self.parse_user_configurations()
        return sectioned_fields

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
                # in case of list, store/view it in a list format
                # list are saved with multiline tab delimiters
                # optionally we can allow comma(,) as a delimiter but it is against the ini list format
                if filedata[conf_variable]["type"] == "list":
                    user_value = ",".join(user_value.lstrip("\n").replace(",", "\n").split("\n"))
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

    def handle_reset_submit(self):
        """get the configuration variables default values"""
        # get the default values
        settings = self.model.get_settings()
        template_file_path = self.config.template_file_path
        fields_per_section = {}
        parameters = {}
        with open(template_file_path, encoding="utf-8") as file_descriptor:
            filedata = json.load(file_descriptor)
            for conf_variable in filedata.keys():
                section = filedata[conf_variable]["section"]
                user_value = filedata[conf_variable]["default"]
                # update the setting in the model
                setting = settings[conf_variable]
                setting.set_value(user_value)

                if section not in fields_per_section:
                    fields_per_section[section] = []
                fields_per_section[section].append(setting)
                parameters[conf_variable] = {"section": section, "value": user_value}
        # update the file
        self.config.set_data(parameters)

        return fields_per_section
