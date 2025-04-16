"""UI tests for Sample Parameters dialog: buttons"""

import pytest
from qtpy import QtCore
from qtpy.QtWidgets import QLabel
from shiver.configuration import Configuration
from shiver.views.configuration import ConfigurationView
from shiver.presenters.configuration import ConfigurationPresenter
from shiver.models.configuration import ConfigurationModel


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_cancel_button(qtbot, monkeypatch, user_conf_file):
    """Test for pushing the help button"""
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    config = Configuration()
    config_view = ConfigurationView()
    config_model = ConfigurationModel()
    ConfigurationPresenter(config_view, config_model, config)
    dialog = config_view.start_dialog()

    dialog.show()
    assert dialog.isVisible()
    # push the Help button
    qtbot.mouseClick(dialog.btn_cancel, QtCore.Qt.LeftButton)

    dialog.close()


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_populate_fields(qtbot, monkeypatch, user_conf_file):
    """Test for populating the sections and fields"""
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    config = Configuration()
    config_view = ConfigurationView()
    config_model = ConfigurationModel()
    ConfigurationPresenter(config_view, config_model, config)
    dialog = config_view.start_dialog()
    dialog.show()
    assert dialog.isVisible()

    # the total number of sections at the moment
    total_sections = 6
    assert dialog.fields_layout.count() == total_sections

    # the total number of fields at the moment
    total_variables = 13
    variables = []
    sections = []
    for i in range(total_sections):
        item = dialog.fields_layout.itemAt(i).widget()
        sections.append(item.title())
        variables += (item.text() for item in item.findChildren(QLabel))

    assert len(variables) == total_variables
    assert "software.info" in sections
    assert "generate_tab.oncat" in sections
    assert "generate_tab.parameters" in sections

    assert "keep_logs" in variables
    assert "oncat_url" in variables
    assert "version" in variables

    # push the cancel button
    qtbot.mouseClick(dialog.btn_cancel, QtCore.Qt.LeftButton)
    dialog.close()


@pytest.mark.parametrize("user_conf_file", ["""[generate_tab.oncat]"""], indirect=True)
def test_apply_button(qtbot, monkeypatch, user_conf_file):
    """Test for updating the form"""
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    config = Configuration()
    config_view = ConfigurationView()
    config_model = ConfigurationModel()
    ConfigurationPresenter(config_view, config_model, config)
    dialog = config_view.start_dialog()
    dialog.show()
    assert dialog.isVisible()

    # the total number of sections at the moment
    total_sections = 6
    assert dialog.fields_layout.count() == total_sections

    # the total number of fields at the moment
    variables = []
    sections = []
    version_field = None
    options_field = None
    additional_logs_field = None
    use_notes_field = None
    field_names = {"version", "options", "additional_logs", "use_notes"}
    for i in range(total_sections):
        item = dialog.fields_layout.itemAt(i).widget()
        sections.append(item.title())
        section_variables = list(item.text() for item in item.findChildren(QLabel))
        variables += section_variables
        if len(list(set(section_variables) & field_names)) > 0:
            for field in item.findChildren(QLabel):
                if field.text() == "version":
                    version_field = field.buddy()
                if field.text() == "options":
                    options_field = field.buddy()
                if field.text() == "additional_logs":
                    additional_logs_field = field.buddy()
                if field.text() == "use_notes":
                    use_notes_field = field.buddy()

    assert version_field is not None
    assert options_field is not None
    assert additional_logs_field is not None
    assert use_notes_field is not None
    # here update values

    # push the cancel button
    qtbot.mouseClick(dialog.btn_cancel, QtCore.Qt.LeftButton)
    dialog.close()
