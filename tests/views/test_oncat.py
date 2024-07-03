#!/usr/bin/env python
# pylint: disable=all
"""Test the views for the ONCat application."""
from qtpy.QtWidgets import QGroupBox
from qtpy.QtCore import Signal
import pytest
from shiver.views.oncat import (
    Oncat,
    get_data_from_oncat,
    get_dataset_names,
    get_dataset_info,
)


def test_oncat(monkeypatch, qtbot):
    """Test the Oncat class."""

    class MockLogin(QGroupBox):
        connection_updated = Signal(bool)

        def __init__(self, *args, parent, **kwargs):
            super().__init__(parent=parent)
            self.is_connected = True

        def get_agent_instance(self):
            return None

    def mock_dataset(login, ipts_number, instrument, use_notes, facility):
        return ["test_dataset1", "test_dataset2"]

    def mock_ipts(self, facility, instrument):
        return ["IPTS-1111", "IPTS-2222"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_names", mock_dataset)
    monkeypatch.setattr(Oncat, "get_oncat_ipts", mock_ipts)

    # mock get_dataset_info
    def mock_get_dataset_info(*args, **kwargs):
        return ["test_file1"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_info", mock_get_dataset_info)
    monkeypatch.setattr("shiver.views.oncat.ONCatLogin", MockLogin)

    err_msgs = []

    def error_message_callback(msg):
        err_msgs.append(msg)

    # test
    oncat = Oncat()
    oncat.connect_error_callback(error_message_callback)
    qtbot.addWidget(oncat)
    oncat.show()
    # test use_notes are saved from configuration settings
    assert oncat.use_notes is False
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


def test_get_dataset_names_invalid_keys(monkeypatch):
    """Use mock to test get_dataset_names with missing keys."""

    # monkeypatch get_data_from_oncat
    def mock_get_data_from_oncat(*args, **kwargs):
        mock_data = [
            {"metadata": {"entry": {"notes": "a"}}},
            {"metadata": {"notentry": {"daslogs": {"sequencename": {"value": "b"}}}}},
        ]
        return mock_data

    monkeypatch.setattr("shiver.views.oncat.get_data_from_oncat", mock_get_data_from_oncat)

    # test the function
    assert get_dataset_names("login", "ipts", "inst", use_notes=True) == []
    assert get_dataset_names("login", "ipts", "inst", use_notes=False) == []


def test_get_dataset_names_invalid_schema(monkeypatch):
    """Use mock to test get_dataset_names with missing keys."""

    # monkeypatch get_data_from_oncat
    def mock_get_data_from_oncat(*args, **kwargs):
        mock_data = {"metadata": {"entry": ""}}
        return mock_data

    monkeypatch.setattr("shiver.views.oncat.get_data_from_oncat", mock_get_data_from_oncat)

    # test the function
    assert get_dataset_names("login", "ipts", "inst", use_notes=True) == []
    assert get_dataset_names("login", "ipts", "inst", use_notes=False) == []


def test_get_dataset_info_empty_metadata(monkeypatch):
    """Use mock to test get_dataset__info with empty metadata."""
    def mock_get_data_from_oncat(*args, **kwargs):
        mock_data = [
            {
                "location": "/tmp/a",
                "indexed": {
                    "run_number": 1,
                },
                "metadata": {},
            },
            {
                "location": "/tmp/b",
                "indexed": {
                    "run_number": 2,
                },
                "metadata": {}
                ,
            },
        ]
        return mock_data

    monkeypatch.setattr("shiver.views.oncat.get_data_from_oncat", mock_get_data_from_oncat)

    # test the function
    # specify include_runs=[1,2] so len(good_runs) > 0 to prevent return false positive
    assert get_dataset_info(
        login="login",
        ipts_number="ipts",
        instrument="inst",
        include_runs=[1,2]
    ) == []



if __name__ == "__main__":
    pytest.main(["-v", __file__])
