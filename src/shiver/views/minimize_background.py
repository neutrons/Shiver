"""Widget for background minimization options"""

from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
)
from qtpy import QtGui
from .invalid_styles import INVALID_QLINEEDIT


class MinimizeBackgroundOptions(QGroupBox):
    """Background minimization options"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Background minimization options")
        layout = QGridLayout()

        layout.addWidget(QLabel("Grouping File"), 0, 0)

        self.group_path = QLineEdit()
        self.group_path.setToolTip(
            "Name of the grouping file. Only used when doing 'Background (minimized by angle and energy'"
        )
        layout.addWidget(self.group_path, 0, 1, 1, 2)

        self.group_browse = QPushButton("Browse")
        self.group_browse.setToolTip("Browse to the grouping file.")
        self.group_browse.clicked.connect(self._group_browse)
        layout.addWidget(self.group_browse, 0, 3)

        double_validator = QtGui.QDoubleValidator(self)
        double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        layout.addWidget(QLabel("Percent Min"), 1, 0)
        self.percent_min = QLineEdit("0", self)
        self.percent_min.setValidator(double_validator)
        layout.addWidget(self.percent_min, 1, 1)

        layout.addWidget(QLabel("Percent Max"), 1, 2)
        self.percent_max = QLineEdit("20", self)
        self.percent_max.setValidator(double_validator)
        layout.addWidget(self.percent_max, 1, 3)

        self.setLayout(layout)

        self.percent_min.textEdited.connect(self.min_max_checked)
        self.percent_max.textEdited.connect(self.min_max_checked)
        self.group_path.textEdited.connect(self.check_grouping_file)

    def set_enabled(self, enabled):
        """Set this widget as enabled or not, and set correct valid state"""
        self.setEnabled(enabled)

        if enabled:
            self.min_max_checked()
            self.check_grouping_file()
        else:
            self.set_field_valid_state(self.percent_min)
            self.set_field_valid_state(self.percent_max)
            self.set_field_valid_state(self.group_path)

    def min_max_checked(self):
        """Ensure Minimum and Maximum value pairs are valid"""
        self.set_field_valid_state(self.percent_min)
        self.set_field_valid_state(self.percent_max)

        if not self.check_num_input(self.percent_min.text(), self.percent_max.text()):
            self.set_field_invalid_state(self.percent_min)
            self.set_field_invalid_state(self.percent_max)

    def check_grouping_file(self):
        """Check that the grouping filename has been set"""
        self.set_field_valid_state(self.group_path)

        if self.group_path.text() == "":
            self.set_field_invalid_state(self.group_path)

    def set_field_invalid_state(self, item):
        """include the item in the field_error list and disable the corresponding button"""
        if self.parent():
            self.parent().set_field_invalid_state(item)
        item.setStyleSheet(INVALID_QLINEEDIT)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and enable the corresponding button"""
        if self.parent():
            self.parent().set_field_valid_state(item)
        item.setStyleSheet("")

    def check_num_input(self, min_value, max_value):
        """Ensure numbers are:
        float, Minimum < Maximum, between 0 and 100 and both exist at the same time"""
        valid = True
        if (len(max_value) == 0 and len(min_value) != 0) or (len(max_value) != 0 and len(min_value) == 0):
            valid = False
        else:
            if len(min_value) != 0 and len(max_value) != 0:
                try:
                    maxnum = float(max_value)
                    minnum = float(min_value)
                    if maxnum <= minnum or minnum < 0 or maxnum > 100:
                        valid = False
                except ValueError:
                    valid = False
        return valid

    def as_dict(self):
        """Return the background minimization widget as a dictionary."""
        return {
            "DetectorGroupingFile": self.group_path.text(),
            "PercentMin": self.percent_min.text() if self.percent_min.text() else None,
            "PercentMax": self.percent_max.text() if self.percent_max.text() else None,
        }

    def populate_from_dict(self, param_dict):
        """Populate this widget from a dictionary"""

        self.group_path.setText(str(param_dict.get("DetectorGroupingFile", "")))
        self.percent_min.setText(str(param_dict.get("PercentMin", "0")))
        self.percent_max.setText(str(param_dict.get("PercentMax", "20")))
        self.set_enabled(self.isEnabled())  # fix validation

    def _group_browse(self):
        """Open the file dialog and update the path"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select one file to open",
            filter="Data File (*.xml *.map);;All Files (*)",
            options=QFileDialog.DontUseNativeDialog,
        )
        if not filename:
            return
        self.group_path.setText(filename)
        self.check_grouping_file()
