"""Test the generate view."""

# pylint: disable=all

import re
import os
from qtpy import QtCore
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QGroupBox, QLabel
from shiver.views.generate import Generate, is_valid_name, has_special_char


def test_mde_name_check():
    """Test the mde name check."""
    assert is_valid_name("test") is True
    assert is_valid_name("_test") is True
    assert is_valid_name("test0") is True
    assert is_valid_name("0test") is False
    assert is_valid_name("?test_0") is False
    assert is_valid_name("test?_0") is False
    assert is_valid_name("test-0") is False


def test_path_check():
    """Test the path check function."""
    assert has_special_char("/tmp/test") is False
    assert has_special_char("/tmp/test?") is True
    assert has_special_char("/tmp/test/me#") is True
    assert has_special_char("C:\\tmp") is False


def test_mde_type_widget(qtbot):
    """Test for the generate widget (view)."""
    generate = Generate()
    mde_type_widget = generate.mde_type_widget
    qtbot.addWidget(generate)
    generate.show()

    errors_list = []

    def error_callback(msg):
        """Callback for error."""
        errors_list.append(msg)

    mde_type_widget.connect_error_callback(error_callback)

    # all three required fields are empty
    assert len(generate.field_errors[generate.buttons.save_btn]) == 3
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 3

    # set files
    directory = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw"))
    files = ("HYS_178922.nxs.h5", "HYS_178923.nxs.h5", "HYS_178926.nxs.h5")
    filenames = [os.path.join(directory, f) for f in files]
    generate.raw_data_widget.set_selected(filenames)

    # check happy path (ui -> dict)
    mde_type_widget.mde_name.setText("test")
    mde_type_widget.output_dir.setText("/tmp/test")
    mde_type_widget.mde_type_background_integrated.setChecked(True)
    rst_dict = mde_type_widget.as_dict()
    #
    ref_dict = {
        "mde_name": "test",
        "output_dir": "/tmp/test",
        "mde_type": "Background (angle integrated)",
    }
    #
    assert rst_dict == ref_dict

    # check happy path (dict -> ui)
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict(ref_dict)
    # assert no errors
    assert mde_type_widget.mde_name.text() == "test"
    assert mde_type_widget.output_dir.text() == "/tmp/test"
    assert mde_type_widget.mde_type_background_integrated.isChecked() is True
    assert len(generate.field_errors[generate.buttons.save_btn]) == 0
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 0

    #
    ref_dict["mde_type"] = "Data"
    mde_type_widget.populate_from_dict(ref_dict)
    assert mde_type_widget.mde_type_data.isChecked() is True
    assert len(generate.field_errors[generate.buttons.save_btn]) == 0
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 0
    #
    ref_dict["mde_type"] = "Background (minimized by angle and energy)"
    mde_type_widget.populate_from_dict(ref_dict)
    assert mde_type_widget.mde_type_background_minimized.isChecked() is True
    assert len(generate.field_errors[generate.buttons.save_btn]) == 1
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 1

    # check error_1: invalid mde name
    mde_type_widget.re_init_widget()
    ref_dict["mde_name"] = "test?"
    mde_type_widget.populate_from_dict(ref_dict)
    assert not mde_type_widget.as_dict()
    assert errors_list[-1] == "Invalid MDE name found in history."
    assert len(generate.field_errors[generate.buttons.save_btn]) == 1
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 1

    # check error_2: empty output dir
    mde_type_widget.re_init_widget()
    mde_type_widget.mde_name.setText("test")
    mde_type_widget.output_dir.setText(" ")
    assert not mde_type_widget.as_dict()
    assert len(generate.field_errors[generate.buttons.save_btn]) == 1

    # check error_3: invalid output dir
    mde_type_widget.re_init_widget()
    ref_dict["mde_name"] = "test"
    ref_dict["output_dir"] = "/tmp/test?"
    mde_type_widget.populate_from_dict(ref_dict)
    assert not mde_type_widget.as_dict()
    assert errors_list[-1] == "Invalid output directory found in history."
    assert len(generate.field_errors[generate.buttons.save_btn]) == 2

    # check error_4: invalid dict used to populate UI
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict({"mde_name": "test?"})
    assert errors_list[-1] == "Invalid MDE name found in history."
    assert len(generate.field_errors[generate.buttons.save_btn]) == 2

    #
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict(
        {
            "mde_name": "test",
            "output_dir": "/tmp/test?",
        }
    )

    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict(
        {
            "mde_name": "test",
            "output_dir": "/tmp/test",
            "mde_type": "Data_",
        }
    )


def test_generate_widget_colors_invalid(qtbot):
    """Test for the generate widget border colors and save button for invalid cases"""
    generate = Generate()
    mde_type_widget = generate.mde_type_widget
    raw_data_widget = generate.raw_data_widget
    qtbot.addWidget(generate)
    generate.show()

    color_search = re.compile("border-color: (.*);")

    # all three required fields are empty
    assert len(generate.field_errors[generate.buttons.save_btn]) == 3
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 3
    # check mde_name border
    qtbot.keyClicks(mde_type_widget.mde_name, "")

    css_style_mde_name = mde_type_widget.mde_name.styleSheet()
    color = color_search.search(css_style_mde_name).group(1)
    assert color == "red"
    assert len(generate.field_errors[generate.buttons.save_btn]) == 3
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 3

    qtbot.keyClicks(mde_type_widget.output_dir, "/tmp/test?")
    # check output_dir border
    css_style_output_dir = mde_type_widget.output_dir.styleSheet()
    color = color_search.search(css_style_output_dir).group(1)
    assert color == "red"
    assert len(generate.field_errors[generate.buttons.save_btn]) == 3

    # check files border
    css_style_files = raw_data_widget.files.styleSheet()
    color = color_search.search(css_style_files).group(1)
    assert color == "red"
    assert len(generate.field_errors[generate.buttons.save_btn]) == 3
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 3

    # assert buttons are deactivated
    assert generate.buttons.save_btn.isEnabled() is False
    assert generate.buttons.generate_btn.isEnabled() is False


def test_generate_widget_colors_valid(qtbot):
    """Test for the generate widget border colors and save button for valid cases"""
    generate = Generate()
    mde_type_widget = generate.mde_type_widget
    raw_data_widget = generate.raw_data_widget
    qtbot.addWidget(generate)
    generate.show()

    assert len(generate.field_errors[generate.buttons.save_btn]) == 3
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 3

    # set mde_name
    qtbot.keyClicks(mde_type_widget.mde_name, "mde_test_2")
    css_style_mde_name = mde_type_widget.mde_name.styleSheet()
    assert css_style_mde_name == ""
    assert len(generate.field_errors[generate.buttons.save_btn]) == 2

    # set output_dir
    qtbot.keyClicks(mde_type_widget.output_dir, "/tmp/")
    css_style_output_dir = mde_type_widget.output_dir.styleSheet()
    assert css_style_output_dir == ""
    assert len(generate.field_errors[generate.buttons.save_btn]) == 1

    # set files
    assert raw_data_widget.files.count() == 0

    directory = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw"))
    files = ("HYS_178922.nxs.h5", "HYS_178923.nxs.h5", "HYS_178926.nxs.h5")
    filenames = [os.path.join(directory, f) for f in files]

    raw_data_widget.set_selected(filenames)

    qtbot.wait(100)
    css_style_files = raw_data_widget.files.styleSheet()
    assert css_style_files == ""
    assert len(generate.field_errors[generate.buttons.save_btn]) == 0
    assert len(generate.field_errors[generate.buttons.generate_btn]) == 0

    # assert buttons are activated
    assert generate.buttons.save_btn.isEnabled() is True
    assert generate.buttons.generate_btn.isEnabled() is True
    qtbot.mouseClick(generate.buttons.save_btn, QtCore.Qt.LeftButton)


def test_generate_update_raw_data_widget_selection_default(qtbot, monkeypatch):
    """Test for the generate widget updating the selected files in the oncat widget: default"""

    # mock oncat login

    class MockLogin(QGroupBox):
        connection_updated = Signal(bool)
        status_label = QLabel("Test")

        def __init__(self, *args, parent, **kwargs):
            super().__init__(parent=parent)
            self.is_connected = True

        def get_agent_instance(self):
            return None

    def mock_dataset(login, ipts_number, instrument, use_notes, facility):
        return ["test_dataset1", "test_dataset2"]

    def mock_ipts(self, facility, instrument):
        return ["IPTS-2222", "IPTS-1111"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_names", mock_dataset)
    monkeypatch.setattr("shiver.views.oncat.Oncat.get_oncat_ipts", mock_ipts)

    # mock get_dataset_info
    def mock_get_dataset_info(*args, **kwargs):
        return ["test_file1"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_info", mock_get_dataset_info)
    monkeypatch.setattr("shiver.views.oncat.ONCatLogin", MockLogin)

    err_msgs = []

    def error_message_callback(msg):
        err_msgs.append(msg)

    generate = Generate()
    oncat = generate.oncat_widget
    oncat.connect_error_callback(error_message_callback)

    qtbot.addWidget(generate)
    generate.show()

    # test connect status check
    assert oncat.connected_to_oncat is True
    # test get_suggested_path
    assert oncat.get_suggested_path() == "/SNS/ARCS/IPTS-2222/nexus"
    # test get_suggested_selected_files
    oncat.dataset.setCurrentText("test_dataset1")
    assert oncat.get_suggested_selected_files() == ["test_file1"]

    generate.update_raw_data_widget_selection()
    # assert len(raw_data_widget.files) == 1
    assert generate.oncat_widget.angle_pv == "omega"
    assert len(oncat.get_suggested_selected_files()) == 1


def test_generate_update_raw_data_widget_selection_new_value(qtbot, monkeypatch):
    """Test for the generate widget updating the selected files in the oncat widget: goniometer value"""
    # mock oncat login

    class MockLogin(QGroupBox):
        connection_updated = Signal(bool)
        status_label = QLabel("Test")

        def __init__(self, *args, parent, **kwargs):
            super().__init__(parent=parent)
            self.is_connected = True

        def get_agent_instance(self):
            return None

    def mock_dataset(login, ipts_number, instrument, use_notes, facility):
        return ["test_dataset1", "test_dataset2"]

    def mock_ipts(self, facility, instrument):
        return ["IPTS-2222", "IPTS-1111"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_names", mock_dataset)
    monkeypatch.setattr("shiver.views.oncat.Oncat.get_oncat_ipts", mock_ipts)

    # mock get_dataset_info
    def mock_get_dataset_info(*args, **kwargs):
        return ["test_file1"]

    monkeypatch.setattr("shiver.views.oncat.get_dataset_info", mock_get_dataset_info)
    monkeypatch.setattr("shiver.views.oncat.ONCatLogin", MockLogin)

    err_msgs = []

    def error_message_callback(msg):
        err_msgs.append(msg)

    generate = Generate()
    oncat = generate.oncat_widget
    oncat.connect_error_callback(error_message_callback)

    qtbot.addWidget(generate)
    generate.show()

    # test connect status check
    assert oncat.connected_to_oncat is True
    # test get_suggested_path
    assert oncat.get_suggested_path() == "/SNS/ARCS/IPTS-2222/nexus"
    # test get_suggested_selected_files
    oncat.dataset.setCurrentText("test_dataset1")
    assert oncat.get_suggested_selected_files() == ["test_file1"]

    generate.update_raw_data_widget_selection(update_angle_pv=True, angle_pv="g1")
    # invalid value
    assert generate.oncat_widget.angle_pv == "g1"


def test_generate_update_raw_data_widget_selection_no_update(qtbot, monkeypatch):
    """Test for the generate widget updating the selected files in the oncat widget: goniometer value no update"""
    generate = Generate()

    def mock_connect_to_oncat():
        return True

    monkeypatch.setattr("shiver.views.oncat.Oncat.connected_to_oncat", mock_connect_to_oncat)

    qtbot.addWidget(generate)
    generate.show()
    generate.update_raw_data_widget_selection(update_angle_pv=False, angle_pv="g1")
    assert generate.oncat_widget.angle_pv == "omega"


def test_generate_update_raw_data_widget_selection_empty(qtbot, monkeypatch):
    """Test for the generate widget updating the selected files in the oncat widget: goniometer empty value"""
    generate = Generate()

    def mock_connect_to_oncat():
        return True

    monkeypatch.setattr("shiver.views.oncat.Oncat.connected_to_oncat", mock_connect_to_oncat)

    qtbot.addWidget(generate)
    generate.show()
    generate.update_raw_data_widget_selection(update_angle_pv=True, angle_pv="")
    # back to default
    assert generate.oncat_widget.angle_pv == "omega"
