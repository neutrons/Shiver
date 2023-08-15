"""Module to load the the settings from SHOME/.shiver/configuration.ini file

Will fall back to a default"""
import os
import shutil

from configparser import ConfigParser
from pathlib import Path
from mantid.kernel import Logger

logger = Logger("SHIVER")


class ConfigurationModel:
    """Configuration Data"""

    def __init__(self, user_path=None):
        """initialization of configuration mechanism"""
        # capture the current state
        self.valid = False

        # locate the template configuration file
        project_directory = Path(__file__).resolve().parent.parent
        self.template_file_path = os.path.join(project_directory, "configuration_template.ini")
        if not os.path.exists(self.template_file_path):
            logger.error(f"Template configuration file: {self.template_file_path} is missing!")

        # retrieve the file path of the file
        if user_path:
            self.config_file_path = user_path
        else:
            # default path
            self.config_file_path = os.path.join(Path.home(), ".shiver", "configuration.ini")
        logger.information(f"{self.config_file_path} with be used")

        # file does not exist create it from template
        if not os.path.exists(self.config_file_path):
            shutil.copy2(self.template_file_path, self.config_file_path)

        self.config = ConfigParser()
        # parse the file
        try:
            self.config.read(self.config_file_path)
            # validate the file has the all the latest variables
            self.validate()
            self.valid = True
        except ValueError as err:
            logger.error(str(err))
            logger.error(f"Problem with the file: {self.config_file_path}")

    def get_data(self, section, name=None):
        """retrieves the configuration data for a variable with name"""
        try:
            if name:
                return self.config[section][name]
            return self.config[section]
        except KeyError as err:
            # requested section/field do not exist
            logger.error(str(err))
            return None

    def validate(self):
        """validates that the fields exist at the config_file_path and writes any missing fields/data
        using the template configuration file: configuration_template.ini as a guide"""
        template_config = ConfigParser()
        template_config.read(self.template_file_path)
        for section in template_config.sections():
            # if section is missing
            if section not in self.config.sections():
                # copy the whole section
                self.config.add_section(section)

            for field in template_config[section]:
                if field not in self.config[section]:
                    # copy the field
                    self.config[section][field] = template_config[section][field]
        with open(self.config_file_path, "w", encoding="utf8") as config_file:
            self.config.write(config_file)

    def is_valid(self):
        """returns the configuration state"""
        return self.valid
