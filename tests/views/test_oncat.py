#!/usr/bin/env python
"""Test the views for the ONCat application."""
import pytest
import pyoncat
from shiver.views.oncat import (
    OncatToken,
    OnCatAgent,
    OnCatLogin,
    Oncat,
    get_data_from_oncat,
    get_dataset_names,
    get_dataset_info,
)


class MockONcat:
    """Mock Oncat instance for testing"""

    def __init__(self, *args, **kwargs) -> None:
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
    pass


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

        def list(self, **kwargs):  # pylint: disable=unused-argument
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
        "inst",) == ["a", "b", "c"]


def test_get_dataset_names(monkeypatch):
    """Use mock to test get_dataset_names."""
    # monkeypatch get_data_from_oncat
    def mock_get_data_from_oncat(*args, **kwargs):  # pylint: disable=unused-argument
        mock_data = [
            {"metadata": 
                {
                    "entry": {
                        "notes": "a"
                        }
                }
            },
            {"metadata": 
                {
                    "entry": {
                        "daslogs": {
                             "sequencename": {"value": "b"}
                            }
                        }
                }
            },
        ]
        return mock_data

    monkeypatch.setattr("shiver.views.oncat.get_data_from_oncat", mock_get_data_from_oncat)

    # test the function
    assert get_dataset_names("login", "ipts", "inst", use_notes=True) == ["a"]
    assert get_dataset_names("login", "ipts", "inst", use_notes=False) == ["b"]


def test_get_dataset_info(monkeypatch):
    """Use mock to test get_dataset_info."""
    # monkeypatch get_data_from_oncat
    def mock_get_data_from_oncat(*args, **kwargs):  # pylint: disable=unused-argument
        mock_data = [
            {   
                "location": "/tmp/a",
                "indexed": {
                    "run_number": 1,
                },
                "metadata": 
                {
                    "entry": {
                        "notes": "a"
                        }
                }
            },
            {
                "location": "/tmp/b",
                "indexed": {
                    "run_number": 2,
                },
                "metadata": 
                {
                    "entry": {
                        "daslogs": {
                             "sequencename": {"value": "b"},
                             "omega": {"average": 1.0},
                            }
                        }
                }
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
    ) == ['/tmp/a']

    # test the function (new format)
    assert get_dataset_info(
        login="login",
        ipts_number="ipts",
        instrument="inst",
        dataset_name="b",
        use_notes=False,
    ) == ['/tmp/b']


if __name__ == "__main__":
    pytest.main(["-v", __file__])
