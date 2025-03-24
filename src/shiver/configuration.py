"""Module to load the the settings from SHOME/.shiver/configuration.ini file

Will fall back to a default"""

import os
import shutil

from configparser import ConfigParser
from pathlib import Path
from mantid.kernel import Logger
from shiver.version import __version__ as current_version

logger = Logger("SHIVER")

# configuration settings file path
CONFIG_PATH_FILE = os.path.join(Path.home(), ".shiver", "configuration.ini")


class Configuration:
    """Load and validate Configuration Data"""

    def __init__(self):
        """initialization of configuration mechanism"""
        # capture the current state
        self.valid = False

        # locate the template configuration file
        project_directory = Path(__file__).resolve().parent
        self.template_file_path = os.path.join(project_directory, "configuration_template.ini")

        # retrieve the file path of the file
        self.config_file_path = CONFIG_PATH_FILE
        logger.information(f"{self.config_file_path} with be used")

        version_update = None
        # if template conf file path exists
        if os.path.exists(self.template_file_path):
            # file does not exist create it from template
            if not os.path.exists(self.config_file_path):
                # if directory structure does not exist create it
                if not os.path.exists(os.path.dirname(self.config_file_path)):
                    os.makedirs(os.path.dirname(self.config_file_path))
                shutil.copy2(self.template_file_path, self.config_file_path)

            self.config = ConfigParser(allow_no_value=True, comment_prefixes="/")

            # the file already exists, check the version
            self.config.read(self.config_file_path)
            config_version = get_data("software.info", "version")

            # in case of missing version or version mismatch
            if not config_version or config_version != current_version:
                # update the whole configuration file and the version
                shutil.copy2(self.template_file_path, self.config_file_path)
                version_update = current_version

            # parse the file
            try:
                self.config.read(self.config_file_path)
                # validate the file has the all the latest variables
                self.validate(version_update)
            except ValueError as err:
                logger.error(str(err))
                logger.error(f"Problem with the file: {self.config_file_path}")
        else:
            logger.error(f"Template configuration file: {self.template_file_path} is missing!")

    def validate(self, version=None):
        """validates that the fields exist at the config_file_path and writes any missing fields/data
        using the template configuration file: configuration_template.ini as a guide
        if version is not None, the version value is set/updated in the configuration file"""
        template_config = ConfigParser(allow_no_value=True, comment_prefixes="/")
        template_config.read(self.template_file_path)
        for section in template_config.sections():
            # if section is missing
            if section not in self.config.sections():
                # copy the whole section
                self.config.add_section(section)

            for item in template_config.items(section):
                field, _ = item
                # if a new version is passed set that in the file
                if version and field == "version":
                    self.config[section][field] = version
                if field not in self.config[section]:
                    # copy the field
                    self.config[section][field] = template_config[section][field]
        with open(self.config_file_path, "w", encoding="utf8") as config_file:
            self.config.write(config_file)
        self.valid = True

    def is_valid(self):
        """returns the configuration state"""
        return self.valid


def get_data(section, name=None):
    """retrieves the configuration data for a variable with name"""
    # default file path location
    config_file_path = CONFIG_PATH_FILE
    if os.path.exists(config_file_path):
        config = ConfigParser()
        # parse the file
        config.read(config_file_path)
        try:
            if name:
                value = config[section][name]
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
    return None

def get_data_logs(section="generate_tab.parameters", name="keep_logs"):
    logs = get_data(section, name)
    default_logs = ["SequenceName", "phi", "chi", "omega", "pause", "proton_charge",
                    "run_title",  "EnergyRequest", "psda", "psr", "s2", "msd"]
    if logs is False:
        return default_logs
    if logs is True or logs is None:
        return ""
    parts = logs.split(",")
    default_logs.extend([p.strip() for p in parts])
    return default_logs
