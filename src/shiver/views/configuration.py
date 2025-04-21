"""PyQt QDialog for Configuration Parameters"""

from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QLabel,
    QDialog,
    QCheckBox,
    QListWidget,
    QGroupBox,
)

from qtpy.QtCore import Qt, QSize
from .invalid_styles import INVALID_QLINEEDIT


class ConfigurationView(QWidget):
    """View for Configuration Parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialog = None
        # button callbacks
        self.btn_apply_callback = None
        self.get_settings_callback = None
        self.btn_reset_callback = None

    def connect_get_settings_callback(self, callback):
        """callback for the getting the settings fields"""
        self.get_settings_callback = callback

    def start_dialog(self):
        """initialize and start dialog"""
        self.dialog = ConfigurationDialog(parent=self)
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        self.populate_fields()
        return self.dialog

    def connect_apply_submit(self, callback):
        """callback for the apply submit button"""
        self.btn_apply_callback = callback

    def connect_reset_submit(self, callback):
        """callback for the apply submit button"""
        self.btn_reset_callback = callback

    def populate_fields(self):
        """populate fields from model"""
        settings = self.get_settings_callback()
        self.dialog.populate_fields(settings)


class ConfigurationDialog(QDialog):
    """Configuration dialo widget"""

    conf_settings = []

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent  # define parent
        # keep track of the fields with invalid inputs
        self.invalid_fields = []

        self.layout = QVBoxLayout()
        self.setWindowTitle("Configuration Settings")
        self.setMinimumSize(QSize(630, 400))

        # inputs
        self.fields_layout = QVBoxLayout()
        self.layout.addLayout(self.fields_layout)

        # loading buttons
        self.btn_layout = QHBoxLayout()
        self.btn_apply = QPushButton("Apply")
        self.btn_layout.addWidget(self.btn_apply)

        self.btn_reset = QPushButton("Reset")
        self.btn_layout.addWidget(self.btn_reset)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_layout.addWidget(self.btn_cancel)

        self.layout.addLayout(self.btn_layout)
        # set the layout
        self.setLayout(self.layout)

        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_reset.clicked.connect(self.btn_reset_submit)

    def set_field_invalid_state(self, item):
        """include the item in the field_error list and disable the corresponding button"""
        if item not in self.invalid_fields:
            self.invalid_fields.append(item)
        item.setStyleSheet(INVALID_QLINEEDIT)
        self.btn_apply.setEnabled(False)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and enable the corresponding button"""
        if item in self.invalid_fields:
            self.invalid_fields.remove(item)
        if len(self.invalid_fields) == 0:
            self.btn_apply.setEnabled(True)
        item.setStyleSheet("")

    def btn_apply_submit(self):
        """Check everything is valid and then call the submit the form"""
        fields = self.get_fields()
        self.parent.btn_apply_callback(fields)

    def btn_reset_submit(self):
        """Reset all the fields of the form to the default state"""
        default_fields = self.parent.btn_reset_callback()
        # remove fields
        self.clear_layout(self.fields_layout)

        # populate
        self.populate_fields(default_fields)

    def clear_layout(self, layout):
        """clear layout and items"""

        if layout is not None:
            while layout.count() > 0:
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def btn_cancel_action(self):
        """Cancel the sample dialog"""
        self.done(1)

    def populate_fields(self, sectioned_settings):
        """Create qwidgets from sectioned settings"""

        for name, settings in sectioned_settings.items():

            section_group_box = QGroupBox(name)
            section_layout = QGridLayout()
            for index, setting in enumerate(settings):
                # set label
                set_label = QLabel(setting.name)
                # set tooltip
                set_label.setToolTip(setting.comments)
                section_layout.addWidget(set_label, index, 0)

                # set field and value
                if len(setting.allowed_values) > 0:
                    # setting.type == "list":
                    set_field_value = QListWidget()
                    set_field_value.addItems(setting.allowed_values)
                    item = set_field_value.item(setting.allowed_values.index(setting.value))
                    set_field_value.setCurrentItem(item)
                elif setting.set_type == "bool":
                    set_field_value = QCheckBox(set_label)
                    set_field_value.setChecked(setting.value)
                else:
                    set_value = setting.value
                    set_field_value = QLineEdit(set_value)
                    if setting.set_type == "list":
                        # allow only comma-separated list of values
                        # on log change
                        set_field_value.textEdited.connect(self.list_format_validate)
                # set readonly
                set_field_value.setDisabled(setting.readonly)
                set_label.setBuddy(set_field_value)
                section_layout.addWidget(set_field_value, index, 1)

                # set validator
            # add section to the form
            section_group_box.setLayout(section_layout)
            self.fields_layout.addWidget(section_group_box)

    def get_fields(self):
        """gather all the edtiable fields with their values"""

        fields = {}
        for i in range(self.fields_layout.count()):
            item = self.fields_layout.itemAt(i).widget()
            section = item.title()
            for field in item.findChildren(QLabel):
                field_value = field.buddy()
                # filter the editable fields
                if field_value.isEnabled():
                    field_name = field.text()
                    fields[field_name] = {"section": section}
                    if isinstance(field_value, QListWidget):
                        fields[field_name]["value"] = field_value.currentItem().text()
                    elif isinstance(field_value, QCheckBox):
                        fields[field_name]["value"] = field_value.isChecked()
                    else:
                        # QLineEdit
                        fields[field_name]["value"] = field_value.text()
        return fields

    def list_format_validate(self):
        """Validate the ratio value"""
        sender = self.sender()
        self.set_field_valid_state(sender)
        value = sender.text().split(",")
        # check if there is are empty elements e.g. ,,,
        if len(value) > 1 and not all(len(element) > 0 and element != " " for element in value):
            self.set_field_invalid_state(sender)
