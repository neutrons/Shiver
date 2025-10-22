"""pytest config"""

import os
import warnings
from configparser import ConfigParser

import pytest
from mantid.simpleapi import mtd
from mantidqt.gui_helper import set_matplotlib_backend

from shiver import Shiver
from shiver.version import __version__ as current_version

# make sure matplotlib is correctly set before we run tests
set_matplotlib_backend()


@pytest.fixture
def shiver_app():
    """Create a Shiver app"""
    app = Shiver()
    app.show()
    return app


@pytest.fixture(autouse=True)
def clear_ads():
    """clear the ADS after every test"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mtd.clear()


@pytest.fixture(scope="session")
def user_conf_file(tmp_path_factory, request):
    """Fixture to create a custom configuration file in tmp_path"""
    # custom configuration file
    config_data = request.param
    user_config = ConfigParser(allow_no_value=True)
    user_config.read_string(config_data)
    user_path = os.path.join(tmp_path_factory.mktemp("data"), "test_config.ini")
    with open(user_path, "w", encoding="utf8") as config_file:
        user_config.write(config_file)
    return user_path


@pytest.fixture(scope="session")
def user_conf_file_with_version(tmp_path_factory, request):
    """Fixture to create a custom configuration file in tmp_path"""
    # custom configuration file
    user_config = ConfigParser(allow_no_value=True)
    # include current version
    version_block = f"[software.info]\nversion = {current_version}\n"
    config_data = request.param + version_block
    user_config.read_string(config_data)
    user_path = os.path.join(tmp_path_factory.mktemp("data"), "test_config.ini")
    with open(user_path, "w", encoding="utf8") as config_file:
        user_config.write(config_file)
    return user_path


@pytest.fixture(autouse=True)
def _get_login(monkeypatch: pytest.fixture) -> None:
    monkeypatch.setattr(os, "getlogin", lambda: "test")
