"""pytest config"""
import pytest
from mantid.simpleapi import mtd
from shiver import Shiver

# Need to import the new algorithms so they are registered with mantid
import shiver.models.makeslice  # noqa: F401 pylint: disable=unused-import
import shiver.models.ConvertDGSToSingleMDE  # noqa: F401 pylint: disable=unused-import
import shiver.models.GenerateDGSMDE  # noqa: F401 pylint: disable=unused-import


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
