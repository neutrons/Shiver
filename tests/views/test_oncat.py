#!/usr/bin/env python
# pylint: disable=all
"""Test the views for the ONCat application."""
import pytest
from shiver.views.oncat import (
    OncatToken,
    OnCatAgent,
    OnCatLogin,
    Oncat,
    get_data_from_oncat,
    get_dataset_names,
    get_dataset_info,
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
    assert agent.get_ipts("facility", "inst") == ["test_id", "test_id2"]
    # test get_dataset_names
    assert agent.get_datasets("facility", "inst", 1) == ["test1", "test2"]
    # test get agent instance
    assert agent.get_agent_instance() is not None


def test_oncat_login(monkeypatch):
    """Test the login window"""
    pass


def test_oncat():
    """Test the Oncat class."""
    pass


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
