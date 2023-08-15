"""Tests for ConfigurationModel"""
import os
from configparser import ConfigParser
from pathlib import Path

import pytest
from shiver.models.configuration import ConfigurationModel


def test_config_path_default():
    """Test configuration default file path"""
    config = ConfigurationModel()
    assert config.config_file_path.endswith(".shiver/configuration.ini") is True
    # check the valid state
    assert config.is_valid()
    assert config.valid == config.is_valid()


def test_config_path_in_folder(tmp_path):
    """Test configuration configuration user-defined file path that does not exist in a new directory"""
    user_path = os.path.join(tmp_path, "temp2", "test_config.ini")
    assert not os.path.exists(user_path)

    config = ConfigurationModel(user_path)
    # check if the file exists now
    assert os.path.exists(user_path)
    assert config.is_valid()


def test_config_path_does_not_exist(tmp_path):
    """Test configuration user-defined file path that does not exist"""
    user_path = os.path.join(tmp_path, "test_config.ini")
    assert not os.path.exists(user_path)

    config = ConfigurationModel(user_path)
    # check if the file is exists now
    assert os.path.exists(user_path)
    assert config.is_valid()


def test_config_path_invalid_format():
    """Test configuration user-defined file path that does not exist"""
    user_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
    )
    config = ConfigurationModel(user_path)
    # check if the file exists
    assert not config.is_valid()


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [generate_tab.oncat]
        oncat_url = https://oncat.ornl.gov
        client_id = 99025bb3-ce06-4f4b-bcf2-36ebf925cd1d
        use_notes = 1

    """
    ],
    indirect=True,
)
def test_field_validate_fields_exist(user_conf_file):
    """Test configuration validate all fields exist with the same values as templates
    Note: update the parameters if the fields increase"""
    # read the custom configuration file
    user_config = ConfigurationModel(user_conf_file)

    assert user_config.config_file_path.endswith(user_conf_file) is True
    # check if the file exists
    assert os.path.exists(user_conf_file)

    # check all fields are the same as the configuration template file
    project_directory = Path(__file__).resolve().parent.parent.parent
    template_file_path = os.path.join(project_directory, "src", "shiver", "configuration_template.ini")
    template_config = ConfigParser()
    template_config.read(template_file_path)
    for section in user_config.config.sections():
        for field in user_config.config[section]:
            assert user_config.config[section][field] == template_config[section][field]


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [generate_tab.oncat]
        oncat_url = test_url
        client_id = 0000-0000
        use_notes = 1
    """
    ],
    indirect=True,
)
def test_field_validate_fields_same(user_conf_file):
    """Test configuration validate all fields exist with their values; different from the template"""

    # read the custom configuration file
    user_config = ConfigurationModel(user_conf_file)

    # check if the file exists
    assert os.path.exists(user_conf_file)

    # check all field values have the same values as the user configuration file
    assert user_config.get_data("generate_tab.oncat", "oncat_url") == "test_url"
    assert user_config.get_data("generate_tab.oncat", "client_id") == "0000-0000"
    assert user_config.get_data("generate_tab.oncat", "use_notes") == "1"


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [generate_tab.oncat]
        client_id = 0000-0000
    """
    ],
    indirect=True,
)
def test_field_validate_fields_missing(user_conf_file):
    """Test configuration validate missing fields added from the template"""
    # read the custom configuration file

    user_config = ConfigurationModel(user_conf_file)

    # check if the file exists
    assert os.path.exists(user_conf_file)

    # check all field values have the same values as the user configuration file
    assert user_config.get_data("generate_tab.oncat", "oncat_url") == "https://oncat.ornl.gov"
    assert user_config.get_data("generate_tab.oncat", "client_id") == "0000-0000"
    assert user_config.get_data("generate_tab.oncat", "use_notes") == "1"


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_get_data_valid(user_conf_file):
    """Test configuration get_data - valid"""
    config = ConfigurationModel(user_conf_file)
    assert config.config_file_path.endswith(user_conf_file) is True
    # get the data
    # section
    assert len(config.get_data("generate_tab.oncat", "")) == 3
    # fields
    assert config.get_data("generate_tab.oncat", "oncat_url") == "https://oncat.ornl.gov"
    assert config.get_data("generate_tab.oncat", "client_id") == "99025bb3-ce06-4f4b-bcf2-36ebf925cd1d"
    assert config.get_data("generate_tab.oncat", "use_notes") == "1"

    assert config.is_valid()


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [generate_tab.oncat]
        oncat_url = test_url
        client_id = 0000-0000
        use_notes = 1
    """
    ],
    indirect=True,
)
def test_get_data_invalid(user_conf_file):
    """Test configuration get_data - invalid"""
    # read the custom configuration file
    config = ConfigurationModel(user_conf_file)
    assert config.config_file_path.endswith(user_conf_file) is True

    # section
    assert config.get_data("section_not_here", "") is None

    assert len(config.get_data("generate_tab.oncat", "")) == 3
    # field
    assert config.get_data("generate_tab.oncat", "field_not_here") is None
