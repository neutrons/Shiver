#!/usr/bin/env python
# pylint: disable=all
"""Test the views for the ONCat application."""
import pytest
import pyoncat
from qtpy.QtWidgets import QGroupBox
from shiver.views.oncat import (
    OncatToken,
    OnCatAgent,
    OnCatLogin,
    Oncat,
    get_data_from_oncat,
    get_dataset_names,
    get_dataset_info,
    ONCAT_URL,
    CLIENT_ID,
)


class MockRecord:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def list(self, *args, **kwargs) -> list:
        return [{"id": "test_id"}, {"id": "test_id2"}]


class MockONcat:
    """Mock Oncat instance for testing"""

    def __init__(self, *args, **kwargs) -> None:
        self.Facility = MockRecord()
        self.Experiment = MockRecord()

    def login(self, *args, **kwargs) -> None:
        """Mock login"""
        pass


def test_oncat_token(tmp_path):
    """Test the OncatToken class."""
    token_path = str(tmp_path / "shiver_test")

    token = OncatToken(token_path)

    # test write
    token.write_token("test_token")

    # test read
    assert token.read_token() == "test_token"


def test_oncat_agent(monkeypatch):
    """Test the OnCatAgent class."""

    # mockey patch get_dataset_names
    def mock_get_dataset_names(*args, **kwargs):
        return ["test1", "test2"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_names", mock_get_dataset_names)

    # mockey patch class pyoncat.ONCat
    monkeypatch.setattr("pyoncat.ONCat", MockONcat)

    # test the class
    agent = OnCatAgent()
    # test login
    agent.login("test_login", "test_password")
    # test is_connected
    assert agent.is_connected is True
    # test get_ipts
    assert set(agent.get_ipts("facility", "inst")) == {"test_id2", "test_id"}
    # test get_dataset_names
    assert set(agent.get_datasets("facility", "inst", 1)) == {"test1", "test2"}
    # test get agent instance
    assert agent.get_agent_instance() is not None


def test_oncat_login(qtbot):
    """Test the login window"""

    # fake oncat agent
    class FakeOnCatAgent:
        def __init__(self) -> None:
            pass

        def login(self, *args, **kwargs) -> None:
            pass

    class DummyOnCatAgent:
        def __init__(self) -> None:
            self._agent = pyoncat.ONCat(
                ONCAT_URL,
                client_id=CLIENT_ID,
                flow=pyoncat.RESOURCE_OWNER_CREDENTIALS_FLOW,
            )

        def login(self, username: str, password: str) -> None:
            self._agent.login(username, password)

    # fake parent widget
    class FakeParent(QGroupBox):
        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.oncat_agent = FakeOnCatAgent()

        def sync_with_remote(self, *args, **kwargs):
            pass

    class DummyParent(QGroupBox):
        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self.oncat_agent = DummyOnCatAgent()

        def sync_with_remote(self, *args, **kwargs):
            pass

    err_msgs = []

    def error_message_callback(msg):
        err_msgs.append(msg)

    # Use Fake ones to test happy path
    # case: login successfully (based on fake oncat agent)
    fake_parent = FakeParent()
    qtbot.addWidget(fake_parent)
    oncat_login_wgt = OnCatLogin(fake_parent, error_message_callback)
    qtbot.addWidget(oncat_login_wgt)
    oncat_login_wgt.show()
    #
    oncat_login_wgt.user_obj.setText("test_login")
    oncat_login_wgt.user_pwd.setText("test_password")
    oncat_login_wgt.button_login.click()
    assert len(err_msgs) == 0

    # Use Dummy ones to test unhappy path
    dummy_parent = DummyParent()
    qtbot.addWidget(dummy_parent)
    # case: login without password
    oncat_login_wgt1 = OnCatLogin(dummy_parent, error_message_callback)
    qtbot.addWidget(oncat_login_wgt1)
    #
    oncat_login_wgt1.user_obj.setText("test_login")
    oncat_login_wgt1.user_pwd.setText("")
    oncat_login_wgt1.button_login.click()
    assert err_msgs[-1] == "A username and/or password was not provided when logging in."
    #
    oncat_login_wgt2 = OnCatLogin(dummy_parent, error_message_callback)
    qtbot.addWidget(oncat_login_wgt2)
    oncat_login_wgt2.show()
    # case: login with wrong password
    oncat_login_wgt2.user_obj.setText("test_login")
    oncat_login_wgt2.user_pwd.setText("wrong_password")
    oncat_login_wgt2.button_login.click()
    assert err_msgs[-1] == "Invalid username or password. Please try again."


def test_oncat(monkeypatch, qtbot):
    """Test the Oncat class."""

    # mockpatch OnCatAgent
    class MockOnCatAgent:
        def __init__(self) -> None:
            pass

        def login(self, *args, **kwargs) -> None:
            pass

        @property
        def is_connected(self) -> bool:
            return True

        def get_ipts(self, *args, **kwargs) -> list:
            return ["IPTS-1111", "IPTS-2222"]

        def get_datasets(self, *args, **kwargs) -> list:
            return ["test_dataset1", "test_dataset2"]

        def get_agent_instance(self):
            return "test_agent"

        @property
        def has_token(self):
            return True

    monkeypatch.setattr("shiver.views.oncat.OnCatAgent", MockOnCatAgent)

    # mock get_dataset_info
    def mock_get_dataset_info(*args, **kwargs):
        return ["test_file1"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_info", mock_get_dataset_info)

    err_msgs = []

    def error_message_callback(msg):
        err_msgs.append(msg)

    # test
    oncat = Oncat()
    oncat.connect_error_callback(error_message_callback)
    qtbot.addWidget(oncat)
    oncat.show()
    # test connect status check
    assert oncat.connected_to_oncat is True
    # test get_suggested_path
    assert oncat.get_suggested_path() == "/SNS/ARCS/IPTS-1111/nexus"
    # test get_suggested_selected_files
    # case 1: no suggestion
    oncat.dataset.setCurrentText("custom")
    assert oncat.get_suggested_selected_files() == []
    # case 2: suggestion
    oncat.dataset.setCurrentText("test_dataset1")
    assert oncat.get_suggested_selected_files() == ["test_file1"]
    # test set_dataset_to_custom
    oncat.set_dataset_to_custom()
    assert oncat.dataset.currentText() == "custom"
    # test active connect to oncat
    oncat.connect_to_oncat()
    # test as_dict
    assert oncat.as_dict() == {"angle_target": 0.1, "dataset": "custom", "instrument": "ARCS", "ipts": "IPTS-1111"}
    # test populate from dict
    oncat.populate_from_dict({"angle_target": 0.2, "dataset": "custom", "instrument": "HYSPEC", "ipts": "IPTS-1111"})
    assert oncat.angle_target.value() == 0.2
    # test get_ipts
    assert oncat.get_ipts() == "IPTS-1111"
    # test get_dataset
    assert oncat.get_dataset() == "custom"
    # test get_instrument
    assert oncat.get_instrument() == "HYS"
    oncat.instrument.setCurrentText("SEQUOIA")
    assert oncat.get_instrument() == "SEQ"
    # test get_facility
    assert oncat.get_facility() == "SNS"


def test_get_data_from_oncat():
    """Use mock to test get_data_from_oncat."""

    # make a mock pyoncat agent
    class MockDataFile:
        def __init__(self, name):
            self.name = name

        def list(self, **kwargs):
            return ["a", "b", "c"]

    class MockAgent:
        def __init__(self):
            self.Datafile = MockDataFile("datafile")

    agent = MockAgent()

    # test the function
    assert get_data_from_oncat(
        agent,
        "projection",
        "ipts",
        "inst",
    ) == ["a", "b", "c"]


def test_get_dataset_names(monkeypatch):
    """Use mock to test get_dataset_names."""

    # monkeypatch get_data_from_oncat
    def mock_get_data_from_oncat(*args, **kwargs):
        mock_data = [
            {"metadata": {"entry": {"notes": "a"}}},
            {"metadata": {"entry": {"daslogs": {"sequencename": {"value": "b"}}}}},
        ]
        return mock_data

    monkeypatch.setattr("shiver.views.oncat.get_data_from_oncat", mock_get_data_from_oncat)

    # test the function
    assert get_dataset_names("login", "ipts", "inst", use_notes=True) == ["a"]
    assert get_dataset_names("login", "ipts", "inst", use_notes=False) == ["b"]


def test_get_dataset_info(monkeypatch):
    """Use mock to test get_dataset_info."""

    # monkeypatch get_data_from_oncat
    def mock_get_data_from_oncat(*args, **kwargs):
        mock_data = [
            {
                "location": "/tmp/a",
                "indexed": {
                    "run_number": 1,
                },
                "metadata": {"entry": {"notes": "a"}},
            },
            {
                "location": "/tmp/b",
                "indexed": {
                    "run_number": 2,
                },
                "metadata": {
                    "entry": {
                        "daslogs": {
                            "sequencename": {"value": "b"},
                            "omega": {"average": 1.0},
                        }
                    }
                },
            },
        ]
        return mock_data

    monkeypatch.setattr("shiver.views.oncat.get_data_from_oncat", mock_get_data_from_oncat)

    # test the function (legacy format)
    assert get_dataset_info(
        login="login",
        ipts_number="ipts",
        instrument="inst",
        dataset_name="a",
        use_notes=True,
    ) == ["/tmp/a"]

    # test the function (new format)
    assert get_dataset_info(
        login="login",
        ipts_number="ipts",
        instrument="inst",
        dataset_name="b",
        use_notes=False,
    ) == ["/tmp/b"]


if __name__ == "__main__":
    pytest.main(["-v", __file__])
