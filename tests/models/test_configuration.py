"""Tests for Configuration mechanism"""

import os
from pathlib import Path

import pytest
from qtpy.QtWidgets import QApplication
from shiver.shiver import Shiver
from shiver.configuration import Configuration, get_data, get_data_logs
from shiver.models.configuration import ConfigurationModel
from shiver.version import __version__ as current_version


def test_config_path_default():
    """Test configuration default file path"""
    config = Configuration()
    assert config.config_file_path.endswith(".shiver/configuration.ini") is True
    # check the valid state
    assert config.is_valid()
    assert config.valid == config.is_valid()


def test_config_path_in_folder(monkeypatch, tmp_path):
    """Test configuration configuration user-defined file path that does not exist in a new directory"""

    user_path = os.path.join(tmp_path, "temp2", "test_config.ini")
    assert not os.path.exists(user_path)

    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_path)

    config = Configuration()
    # check if the file exists now
    assert os.path.exists(user_path)
    assert config.is_valid()


def test_config_path_does_not_exist(monkeypatch, tmp_path):
    """Test configuration user-defined file path that does not exist"""
    user_path = os.path.join(tmp_path, "test_config.ini")
    assert not os.path.exists(user_path)

    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_path)

    config = Configuration()
    # check if the file is exists now
    assert os.path.exists(user_path)
    assert config.is_valid()


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.oncat]
        #url to oncat portal
        oncat_url = https://oncat.ornl.gov
        #client id for on cat; it is unique for Shiver
        client_id = 46c478f0-a472-4551-9264-a937626d5fc2

        [generate_tab.parameters]
        keep_logs = False
    """
    ],
    indirect=True,
)
def test_field_validate_fields_exist(monkeypatch, user_conf_file_with_version):
    """Test configuration validate all fields exist with the same values as templates
    Note: update the parameters if the fields increase"""
    # read the custom configuration file
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)
    user_config = Configuration()

    assert user_config.config_file_path.endswith(user_conf_file_with_version) is True
    # check if the file exists
    assert os.path.exists(user_conf_file_with_version)

    # check all fields are the same as the configuration template file
    project_directory = Path(__file__).resolve().parent.parent.parent
    template_file_path = os.path.join(project_directory, "src", "shiver", "configuration_template.json")
    template_config = user_config.convert_to_ini(template_file_path)

    # comments should be copied too
    for section in user_config.config.sections():
        for field in user_config.config[section]:
            if field != "version":
                assert user_config.config[section][field] == template_config[section][field]
            else:
                assert user_config.config[section][field].value == current_version
    assert get_data_logs() == [
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
        "vChTrans",
    ]


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.oncat]
        oncat_url = test_url
        client_id = 0000-0000
        use_notes = True

        [generate_tab.parameters]
        keep_logs = True
    """
    ],
    indirect=True,
)
def test_field_validate_fields_same(monkeypatch, user_conf_file_with_version):
    """Test configuration validate all fields exist with their values; different from the template,
    provided the version is the same"""

    # read the custom configuration file
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)
    user_config = Configuration()

    # check if the file exists
    assert os.path.exists(user_conf_file_with_version)
    assert user_config.config_file_path == user_conf_file_with_version

    # check all field values have the same values as the user configuration file
    assert get_data("generate_tab.oncat", "oncat_url") == "test_url"
    assert get_data("generate_tab.oncat", "client_id") == "0000-0000"
    # cast to bool
    assert get_data("generate_tab.oncat", "use_notes") is True
    assert get_data("software.info", "version") == current_version

    # check logs
    assert get_data_logs() == ""


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.oncat]
        oncat_url = test_url
        client_id = 0000-0000
        use_notes = True

        [generate_tab.parameters]
        keep_logs = False
        additional_logs = SensorA, SensorB
    """
    ],
    indirect=True,
)
def test_keep_logs(monkeypatch, user_conf_file_with_version):
    """Test keeping extra logs"""
    # read the custom configuration file
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)

    # check logs
    assert get_data_logs() == [
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
        "vChTrans",
        "SensorA",
        "SensorB",
    ]


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [generate_tab.oncat]
        oncat_url = test_url
        client_id = 0000-0000
        use_notes = True
    """
    ],
    indirect=True,
)
def test_field_validate_fields_update_different_version(monkeypatch, user_conf_file):
    """Test configuration update all fields, provided the version is not the same"""

    # read the custom configuration file
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    user_config = Configuration()

    # check if the file exists
    assert os.path.exists(user_conf_file)
    assert user_config.config_file_path == user_conf_file

    # check all field values have the same values as the user configuration file
    assert get_data("generate_tab.oncat", "oncat_url") != "test_url"
    assert get_data("generate_tab.oncat", "client_id") != "0000-0000"
    # version is included with the current version
    assert get_data("software.info", "version") == current_version


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.oncat]
        client_id = 0000-0000
    """
    ],
    indirect=True,
)
def test_field_validate_fields_missing(monkeypatch, user_conf_file_with_version):
    """Test configuration validate missing fields added from the template"""

    # read the custom configuration file
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)
    user_config = Configuration()

    # check if the file exists
    assert os.path.exists(user_conf_file_with_version)
    assert user_config.config_file_path == user_conf_file_with_version

    # check all field values have the same values as the user configuration file
    assert get_data("generate_tab.oncat", "oncat_url") == "https://oncat.ornl.gov"
    assert get_data("generate_tab.oncat", "client_id") == "0000-0000"
    assert get_data("generate_tab.oncat", "use_notes") is False


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_get_data_valid(monkeypatch, user_conf_file):
    """Test configuration get_data - valid"""

    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    config = Configuration()
    assert config.config_file_path.endswith(user_conf_file) is True
    # get the data
    # section fields with comments
    assert len(get_data("generate_tab.oncat", "")) == 7
    # fields
    assert get_data("generate_tab.oncat", "oncat_url") == "https://oncat.ornl.gov"
    assert get_data("generate_tab.oncat", "client_id") == "46c478f0-a472-4551-9264-a937626d5fc2"
    assert get_data("generate_tab.oncat", "use_notes") is False

    assert config.is_valid()


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_set_data(monkeypatch, user_conf_file):
    """Test configuration set_data - valid"""

    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    config = Configuration()
    # check the default data
    assert get_data("generate_tab.oncat", "use_notes") is False
    assert get_data("main_tab.plot", "display_title") == "full"

    # update the values
    data = {
        "use_notes": {"section": "generate_tab.oncat", "value": True},
        "display_title": {"section": "main_tab.plot", "value": "no_title"},
    }
    config.set_data(data)
    # check they are updated
    assert get_data("generate_tab.oncat", "use_notes") is True
    assert get_data("main_tab.plot", "display_title") == "no_title"

    assert config.is_valid()


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_set_invalid_data(monkeypatch, user_conf_file):
    """Test configuration set_data - invalid"""

    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    config = Configuration()

    # update the values
    data = {
        "notes": {"section": "note_section", "value": True},
        "no_options": {"section": "main_tab.plot", "value": "no_title"},
    }
    config.set_data(data)
    # check they are updated
    assert get_data("note_section", "notes") is None
    assert get_data("main_tab.plot", "no_options") is None
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
def test_get_data_invalid(monkeypatch, user_conf_file):
    """Test configuration get_data - invalid"""
    # read the custom configuration file
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    config = Configuration()
    assert config.config_file_path.endswith(user_conf_file) is True

    # section
    assert get_data("section_not_here", "") is None
    # fields with comments and space
    assert len(get_data("generate_tab.oncat", "")) == 7
    # field
    assert get_data("generate_tab.oncat", "field_not_here") is None


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        display_title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_conf_init_invalid(capsys, user_conf_file, monkeypatch):
    """Test starting the app with invalid configuration"""

    # initialization
    _ = QApplication([])
    # mock conf info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    def mock_is_valid(self):  # pylint: disable=unused-argument
        return False

    monkeypatch.setattr("shiver.configuration.Configuration.is_valid", mock_is_valid)
    with pytest.raises(SystemExit):
        shiver = Shiver()
        shiver.show()

    captured = capsys.readouterr()
    assert captured[0].startswith("Error with configuration settings!")


def test_config_template_not_exists(monkeypatch, tmp_path):
    """Test configuration template file path that does not exist"""
    tmpl_path = os.path.join(tmp_path, "test_config.ini")
    assert not os.path.exists(tmpl_path)

    monkeypatch.setattr("shiver.configuration.TEMPLATE_PATH_FILE", tmpl_path)
    config = Configuration()
    assert not config.is_valid()


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        display_title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_config_template_invalid_json(monkeypatch, user_conf_file):
    """Test configuration template file has invalid json format"""

    monkeypatch.setattr("shiver.configuration.TEMPLATE_PATH_FILE", user_conf_file)
    config = Configuration()
    assert not config.is_valid()


def test_configuration_model_add():
    """Test configuration model add"""
    config_model = ConfigurationModel()
    set_name = "option1"
    setting = {
        "name": set_name,
        "value": True,
        "conf_type": "bool",
        "section": "generate_section",
        "allowed_values": [],
        "comments": "this is a comment",
        "readonly": False,
    }
    assert len(config_model.get_settings().keys()) == 0
    config_model.add_setting(**setting)
    settings = config_model.get_settings()
    assert len(settings.keys()) == 1
    assert settings[set_name].name == setting["name"]
    assert settings[set_name].value == setting["value"]
    assert settings[set_name].set_type == setting["conf_type"]
    assert settings[set_name].section == setting["section"]
    assert settings[set_name].allowed_values == setting["allowed_values"]
    assert settings[set_name].comments == setting["comments"]
    assert settings[set_name].readonly == setting["readonly"]


def test_configuration_model_update():
    """Test configuration model add"""
    config_model = ConfigurationModel()
    set_name = "option1"
    setting = {
        "name": set_name,
        "value": True,
        "conf_type": "bool",
        "section": "generate_section",
        "allowed_values": [],
        "comments": "this is a comment",
        "readonly": False,
    }
    config_model.add_setting(**setting)
    settings = config_model.get_settings()
    assert len(settings.keys()) == 1
    assert settings[set_name].value == setting["value"]

    # update
    new_value = False
    update_settings = {set_name: {"value": new_value}}
    config_model.update_settings_values(update_settings)
    settings = config_model.get_settings()
    assert len(settings.keys()) == 1
    assert settings[set_name].name == setting["name"]
    assert settings[set_name].value == new_value
    assert settings[set_name].set_type == setting["conf_type"]
    assert settings[set_name].section == setting["section"]
    assert settings[set_name].allowed_values == setting["allowed_values"]
    assert settings[set_name].comments == setting["comments"]
    assert settings[set_name].readonly == setting["readonly"]
