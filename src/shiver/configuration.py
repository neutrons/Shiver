"""Module to load the the settings from SHOME/.shiver/configuration.ini file

Will fall back to a default"""

import os
import json
from copy import deepcopy
from pathlib import Path
from configupdater import ConfigUpdater

from mantid.kernel import Logger
from shiver.version import __version__ as current_version

logger = Logger("SHIVER")

# configuration settings file path
CONFIG_PATH_FILE = os.path.join(Path.home(), ".shiver", "configuration.ini")
# locate the template configuration file
TEMPLATE_PATH_FILE = os.path.join(Path(__file__).resolve().parent, "configuration_template.json")


class Configuration:
    """Load and validate Configuration Data"""

    def __init__(self):
        """initialization of configuration mechanism"""
        self.template_file_path = ""
        self.template_config_ini = None
        self.config = None
        # capture the current state
        self.valid = False

        # locate the template configuration file
        self.template_file_path = TEMPLATE_PATH_FILE
        # retrieve the file path of the file
        self.config_file_path = CONFIG_PATH_FILE
        logger.information(f"{self.config_file_path} with be used")
        # if template conf file path exists
        if os.path.exists(self.template_file_path):
            self.template_config_ini = self.convert_to_ini(self.template_file_path)
            if self.is_valid():
                version_update = None
                # file does not exist create it from template
                if not os.path.exists(self.config_file_path):
                    # if directory structure does not exist create it
                    if not os.path.exists(os.path.dirname(self.config_file_path)):
                        os.makedirs(os.path.dirname(self.config_file_path))
                    with open(self.config_file_path, "w", encoding="utf-8") as configfile:
                        self.template_config_ini.write(configfile)
                self.config = ConfigUpdater(allow_no_value=True)

                # the file already exists, check the version
                self.config.read(self.config_file_path)
                config_version = get_data("software.info", "version")
                # print("config_version", config_version, current_version)
                # in case of missing version or version mismatch
                if not config_version or config_version != current_version:
                    # update the whole configuration file and the version
                    with open(self.config_file_path, "w", encoding="utf-8") as configfile:
                        self.template_config_ini.write(configfile)
                    version_update = current_version

                # parse the file
                self.config.read(self.config_file_path)
                # validate the file has the all the latest variables
                self.validate(version_update)

            else:
                logger.error(f"Template configuration file: {self.template_file_path} is invalid!")
        else:
            logger.error(f"Template configuration file: {self.template_file_path} is missing!")
            self.valid = False

    def validate(self, version=None):
        """validates that the fields exist at the config_file_path and writes any missing fields/data
        using the template configuration file: configuration_template.ini as a guide
        if version is not None, the version value is set/updated in the configuration file"""
        template_config = self.template_config_ini
        for section in template_config.sections():
            # if section is missing
            if section not in self.config.sections():
                # copy the whole section
                self.config.add_section(section)

            for index, item in enumerate(template_config.items(section)):
                name, field = item
                # if a new version is passed set that in the file
                if version and name == "version":
                    self.config[section][name] = version
                if name not in self.config[section]:
                    # copy the field
                    self.config[section][name] = deepcopy(field)

                    # find the comments that are hidden in the container structure
                    comment_lines = ",".join(
                        field._container._structure[index * 2]._lines  # pylint: disable=protected-access
                    )
                    self.config[section][name].add_before.comment(comment_lines)

        with open(self.config_file_path, "w", encoding="utf8") as config_file:
            self.config.write(config_file)
        self.valid = True

    def is_valid(self):
        """returns the configuration state"""
        return self.valid

    def convert_to_ini(self, filepath):
        """converts a json to ini format"""
        config_ini = ConfigUpdater(allow_no_value=True)
        with open(filepath, encoding="utf-8") as file_descriptor:
            try:
                filedata = json.load(file_descriptor)
                for conf_variable in filedata.keys():
                    section = filedata[conf_variable]["section"]
                    # if section is missing
                    if section not in config_ini.sections():
                        # create the whole section
                        config_ini.add_section(section)
                        # config_ini[section].add_after.space(1)
                    default_value = str(filedata[conf_variable]["default"])
                    config_ini[section][conf_variable] = default_value
                    config_ini[section][conf_variable].add_before.comment(filedata[conf_variable]["comments"])
                self.valid = True
            except json.JSONDecodeError as err:
                # invalid json format
                logger.error(str(err))
                self.valid = False
            return config_ini

    def set_data(self, settings):
        """retrieves the configuration data and updates the config and user's file"""
        for conf_variable in settings:
            self.set_field_data(conf_variable, settings[conf_variable]["section"], settings[conf_variable]["value"])
        with open(self.config_file_path, "w", encoding="utf8") as config_file:
            self.config.write(config_file)
        self.valid = True

    def set_field_data(self, name, section, value):
        """updates the configuration setting 'name' from 'section' with 'value'"""
        if self.config.has_option(section, name):
            # to conform to ini format for lists: line-separated
            if isinstance(value, str) and "," in value:
                self.config[section][name].set_values(value)
            self.config[section][name] = value


def get_data(section, name=None):
    """retrieves the configuration data for a variable with name"""
    # default file path location
    config_file_path = CONFIG_PATH_FILE
    if os.path.exists(config_file_path):
        config = ConfigUpdater()
        # parse the file
        config.read(config_file_path)
        try:
            if name and config.has_section(section):
                if not config.has_option(section, name):
                    return None
                value = config.get(section, name, None).value
                # in case of boolean string value cast it to bool
                if value in ("True", "False"):
                    return value == "True"
                # in case of None
                if value == "None":
                    return None
                return value
            return config[section]
        except KeyError as err:
            # requested section/field do not exist
            logger.error(str(err))
    return None


def get_data_logs():
    """Get the logs to keep in the generation of MDE workspaces"""
    keep_logs = get_data("generate_tab.parameters", "keep_logs")
    logs = get_data("generate_tab.parameters", "additional_logs")

    default_logs = [
        "SequenceName",
        "phi",
        "chi",
        "omega",
        "pause",
        "proton_charge",
        "run_title",
        "EnergyRequest",
        "psda",
        "psr",
        "s2",
        "msd",
    ]
    if keep_logs is False:
        return default_logs
    if keep_logs is True and len(logs) == 0:
        return ""
    parts = logs.split(" ")
    default_logs.extend([p.strip() for p in parts])
    return default_logs
