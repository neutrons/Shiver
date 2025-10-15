"""UI tests for Sample Parameters dialog: buttons"""

import re

import pytest
from qtpy import QtCore
from qtpy.QtWidgets import QLabel

from shiver.configuration import Configuration, get_data
from shiver.models.configuration import ConfigurationModel
from shiver.presenters.configuration import ConfigurationPresenter
from shiver.views.configuration import ConfigurationDialog, ConfigurationView


def test_cancel_button(qtbot):
    """Test for pushing the help button"""

    dialog = ConfigurationDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    assert dialog.isVisible()
    # push the cancel button
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
    total_variables = 15
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
    display_title_field = None
    additional_logs_field = None
    use_notes_field = None
    field_names = {"version", "display_title", "additional_logs", "use_notes"}
    for i in range(total_sections):
        item = dialog.fields_layout.itemAt(i).widget()
        sections.append(item.title())
        section_variables = list(item.text() for item in item.findChildren(QLabel))
        variables += section_variables
        if len(list(set(section_variables) & field_names)) > 0:
            for field in item.findChildren(QLabel):
                if field.text() == "version":
                    version_field = field.buddy()
                if field.text() == "display_title":
                    display_title_field = field.buddy()
                if field.text() == "additional_logs":
                    additional_logs_field = field.buddy()
                if field.text() == "use_notes":
                    use_notes_field = field.buddy()

    assert version_field is not None
    assert display_title_field is not None
    assert additional_logs_field is not None
    assert use_notes_field is not None

    # update values
    # version
    assert version_field.text() != ""
    assert not version_field.isEnabled()

    # options
    assert display_title_field.currentItem().text() == "full"
    qtbot.keyClicks(display_title_field, "name_only")
    assert display_title_field.currentItem().text() == "name_only"

    # additional_logs
    assert additional_logs_field.text() == ""
    qtbot.keyClicks(additional_logs_field, "log1, ")

    # not a valid list yet check banckground color and button
    color_search = re.compile("border-color: (.*);")
    css_style = additional_logs_field.styleSheet()
    bg_color = color_search.search(css_style).group(1)
    assert bg_color == "red"
    assert not dialog.btn_apply.isEnabled()
    qtbot.keyClicks(additional_logs_field, "log2")

    # use_notes
    assert not use_notes_field.isChecked()
    use_notes_field.setChecked(True)
    # push the apply button
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    # close dialog
    dialog.close()

    # start dialog
    dialog = config_view.start_dialog()
    dialog.show()
    assert dialog.isVisible()

    # check updated values are shown
    assert not version_field.isEnabled()
    assert display_title_field.currentItem().text() == "name_only"
    assert additional_logs_field.text() == "log1, log2"
    assert use_notes_field.isChecked()

    # check the files saved in the ini file
    assert get_data("main_tab.plot", "display_title") == "name_only"
    assert get_data("generate_tab.parameters", "additional_logs") == "log1, log2"
    assert get_data("generate_tab.oncat", "use_notes") is True

    # close dialog
    dialog.close()


@pytest.mark.parametrize("user_conf_file", [""""""], indirect=True)
def test_reset_button(qtbot, monkeypatch, user_conf_file):  # noqa: R0912 pylint: disable=too-many-branches
    """Test for updating the form"""

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
    display_title_field = None
    additional_logs_field = None
    use_notes_field = None
    field_names = {"version", "display_title", "additional_logs", "use_notes"}
    for i in range(total_sections):
        item = dialog.fields_layout.itemAt(i).widget()
        sections.append(item.title())
        section_variables = list(item.text() for item in item.findChildren(QLabel))
        variables += section_variables
        if len(list(set(section_variables) & field_names)) > 0:
            for field in item.findChildren(QLabel):
                if field.text() == "version":
                    version_field = field.buddy()
                if field.text() == "display_title":
                    display_title_field = field.buddy()
                if field.text() == "additional_logs":
                    additional_logs_field = field.buddy()
                if field.text() == "use_notes":
                    use_notes_field = field.buddy()

    assert version_field is not None
    assert display_title_field is not None
    assert additional_logs_field is not None
    assert use_notes_field is not None

    # update values
    # version
    assert version_field.text() != ""
    assert not version_field.isEnabled()

    # options
    assert display_title_field.currentItem().text() == "full"
    qtbot.keyClicks(display_title_field, "name_only")
    assert display_title_field.currentItem().text() == "name_only"

    # additional_logs
    assert additional_logs_field.text() == ""
    qtbot.keyClicks(additional_logs_field, "log1,log2")

    # use_notes
    assert not use_notes_field.isChecked()
    use_notes_field.setChecked(True)
    # push the apply button
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)
    # puth the reset button
    qtbot.mouseClick(dialog.btn_reset, QtCore.Qt.LeftButton)

    for i in range(total_sections):
        item = dialog.fields_layout.itemAt(i).widget()
        sections.append(item.title())
        section_variables = list(item.text() for item in item.findChildren(QLabel))
        variables += section_variables
        if len(list(set(section_variables) & field_names)) > 0:
            for field in item.findChildren(QLabel):
                if field.text() == "version":
                    version_field = field.buddy()
                if field.text() == "display_title":
                    display_title_field = field.buddy()
                if field.text() == "additional_logs":
                    additional_logs_field = field.buddy()
                if field.text() == "use_notes":
                    use_notes_field = field.buddy()

    # check updated values are shown
    assert not version_field.isEnabled()
    assert display_title_field.currentItem().text() == "full"
    assert additional_logs_field.text() == ""
    assert not use_notes_field.isChecked()

    # check the files saved in the ini file
    assert get_data("main_tab.plot", "display_title") == "full"
    assert get_data("generate_tab.parameters", "additional_logs") == ""
    assert get_data("generate_tab.oncat", "use_notes") is False

    # close dialog
    dialog.close()
