"""pytest config"""
import pytest
from shiver import Shiver

# Need to import new algorithms before mantid.simpleapi
import shiver.models.makeslice  # noqa: F401 pylint: disable=unused-import


@pytest.fixture
def shiver_app(qtbot):
    """Create a Shiver app"""
    app = Shiver()
    qtbot.addWidget(app)
    app.show()
    return app
