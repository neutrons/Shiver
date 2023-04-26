"""pytest config"""
import pytest
from mantid.simpleapi import mtd
from shiver import Shiver


@pytest.fixture
def shiver_app():
    """Create a Shiver app"""
    app = Shiver()
    app.show()
    return app


@pytest.fixture(autouse=True)
def clear_ads():
    """clear the ADS after every test"""
    mtd.clear()
