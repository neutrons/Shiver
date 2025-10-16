"""PyQt QDialog for Sample Parameters"""

import re

from qtpy import QtGui
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QCheckBox,
    QDialog,
    QErrorMessage,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")

from shiver.models.help import help_function

from .invalid_styles import INVALID_QLINEEDIT, INVALID_QTABLEWIDGET


def return_valid(validity, teststring, pos):
    """Returns state during validation"""
    if QString == str:
        return (validity, teststring, pos)
    return (validity, pos)


class ADValidator(QtGui.QValidator):
    """Validates the additional dimensions value"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def validate_cell(self, teststring, start, end, pos):
        """Validates in 3-element comma-separated format: <string>,<min_number>,<max_number>"""
        elements = str(teststring).split(",")[start:end]
        if len(elements) == 3 and len(str(elements[0].strip())) != 0:
            try:
                # valid case with 1 string 2 float numbers
                str(elements[0])
                min_num = float(elements[1])
                max_num = float(elements[2])
                if min_num < max_num:
                    return return_valid(QtGui.QValidator.Acceptable, teststring, pos)
                return return_valid(QtGui.QValidator.Intermediate, teststring, pos)
            except ValueError:
                try:
                    # invalid case in progress of writing the array
                    str(elements[0] + "")
                    float(elements[1] + "1")
                    float(elements[2] + "1")
                    return return_valid(QtGui.QValidator.Intermediate, teststring, pos)
                except ValueError:
                    return return_valid(QtGui.QValidator.Invalid, teststring, pos)
        return return_valid(QtGui.QValidator.Intermediate, teststring, pos)

    def validate(self, teststring, pos):
        """Validates the 3-element values"""
        group = 3
        # empty string is allowed
        if len(teststring.strip()) == 0:
            return return_valid(QtGui.QValidator.Acceptable, teststring, pos)

        elements = str(teststring.strip()).split(",")
        if len(elements) % group == 0:
            groups = len(elements) // group
            for i in range(groups):
                state = self.validate_cell(teststring, group * i, group * i + 3, pos)
                if state[0] != QtGui.QValidator.Acceptable:
                    return state
            return state
        # invalid number of digits maybe in progress
        return return_valid(QtGui.QValidator.Intermediate, teststring, pos)


class AdvancedDialog(QDialog):  # pylint: disable=too-many-public-methods
    """Advanced Options widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setWindowTitle("Advanced Options")
        self.parent = parent
        # validators
        self.double_validator = QtGui.QDoubleValidator(self)
        # standard decimal point-format for example: 1.2
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.ad_validator = ADValidator(self)
        # keep track of the fields with invalid inputs
        self.invalid_fields = []
        self.invalid_cells = []

        self.error = None
        # table data
        table_label = QLabel("Mask Bank, Tube, Pixel")
        table_label.setAlignment(Qt.AlignTop)
        layout.addWidget(table_label, 0, 0)

        self.table_view = QTableWidget()
        self.table_view.setToolTip("Input parameters for masking pixels (see MaskBTP algorithm).")
        # hide the header bars
        self.table_view.verticalHeader().hide()
        self.table_view.setRowCount(3)
        self.table_view.setColumnCount(3)
        self.table_view.resizeRowsToContents()
        self.table_view.resizeColumnsToContents()

        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_headers = ["Bank", "Tube", "Pixel"]
        self.table_view.setHorizontalHeaderLabels(self.table_headers)
        self.initialize_cells()

        layout.addWidget(self.table_view, 0, 1)

        table_btns = QWidget()
        table_btn_layout = QVBoxLayout()
        table_btn_layout.setAlignment(Qt.AlignTop)

        self.add_btn = QPushButton("Add Row")
        self.add_btn.setToolTip("Add a row to the mask table.")
        table_btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Row")
        self.delete_btn.setToolTip("Delete a row from the mask table.")
        table_btn_layout.addWidget(self.delete_btn)

        table_btns.setLayout(table_btn_layout)
        layout.addWidget(table_btns, 0, 2)

        e_widget = QWidget()
        e_layout = QGridLayout()
        e_layout.setContentsMargins(0, 0, 0, 0)
        # Emin - Emax
        emin_label = QLabel("Emin")
        emin_label.setToolTip("Minimum energy transfer (default -0.95*Ei).")
        e_layout.addWidget(emin_label, 0, 0)

        self.emin_input = QLineEdit()
        self.emin_input.setToolTip("Minimum energy transfer (default -0.95*Ei).")
        self.emin_input.setValidator(self.double_validator)
        self.emin_input.setFixedWidth(80)
        e_layout.addWidget(self.emin_input, 0, 1)

        # Emax
        emax_label = QLabel("Emax")
        emax_label.setToolTip("Maximum energy transfer (default 0.95*Ei).")
        e_layout.addWidget(emax_label, 0, 2)

        self.emax_input = QLineEdit()
        self.emax_input.setToolTip("Maximum energy transfer (default 0.95*Ei).")
        self.emax_input.setValidator(self.double_validator)
        self.emax_input.setFixedWidth(80)
        e_layout.addWidget(self.emax_input, 0, 3)

        e_widget.setLayout(e_layout)
        layout.addWidget(e_widget, 1, 0, 1, 2)

        # 2nd row
        # filter
        self.filter_check = QCheckBox("Apply filter bad pulses")
        self.filter_check.setToolTip("Flag to filter pulses with low proton charge.")
        e_layout.addWidget(self.filter_check, 1, 0, 1, 2)

        self.lcutoff_label = QLabel("LowerCutoff (%)")
        self.lcutoff_label.setToolTip(
            "Percentage of the average proton charge per pulse below which events are rejected."
        )
        e_layout.addWidget(self.lcutoff_label, 1, 2)

        self.lcutoff_input_default = "95"
        self.lcutoff_input = QLineEdit(self.lcutoff_input_default)
        self.lcutoff_input.setToolTip(
            "Percentage of the average proton charge per pulse below which events are rejected."
        )
        self.lcutoff_input.setValidator(self.double_validator)
        self.lcutoff_input.setFixedWidth(80)
        e_layout.addWidget(self.lcutoff_input, 1, 3)

        # 3rd row
        tib_widget = QWidget()
        tib_layout = QHBoxLayout()
        tib_layout.setContentsMargins(0, 0, 0, 0)

        # Apply TIB
        tib_label = QLabel("Apply TIB")
        tib_layout.addWidget(tib_label)
        tib_tooltip = (
            "Time independent subtraction method:\n * Instrument default - available for CNCS and HYSPEC."
            "\n * Yes - needs manual input for both minimum and maximum."
            "\n * No - no time independent background subtraction."
        )
        tib_label.setToolTip(tib_tooltip)

        self.tib_default = QRadioButton("Instrument default")
        self.tib_default.setToolTip(tib_tooltip)
        tib_layout.addWidget(self.tib_default)

        self.tib_yes = QRadioButton("Yes")
        self.tib_yes.setToolTip(tib_tooltip)
        tib_layout.addWidget(self.tib_yes)

        self.tib_no = QRadioButton("No")
        self.tib_no.setToolTip(tib_tooltip)
        tib_layout.addWidget(self.tib_no)

        tib_widget.setLayout(tib_layout)
        layout.addWidget(tib_widget, 3, 0, 1, 2)

        # 4th row
        tibmm_widget = QWidget()
        tibmm_layout = QHBoxLayout()
        tibmm_layout.setContentsMargins(0, 0, 0, 0)
        tibmm_layout.addStretch(1)

        # TIB min- max
        self.tib_min_label = QLabel("TIB min")
        self.tib_min_label.setToolTip(
            "Lower limit for time independent background. "
            "TIB min must be less than TIB max, and both have to be in the raw data range."
        )
        tibmm_layout.addWidget(self.tib_min_label)

        self.tib_min_input = QLineEdit()
        self.tib_min_input.setToolTip(
            "Lower limit for time independent background. "
            "TIB min must be less than TIB max, and both have to be in the raw data range."
        )
        self.tib_min_input.setValidator(self.double_validator)
        self.tib_min_input.setFixedWidth(80)
        tibmm_layout.addWidget(self.tib_min_input)

        # TIB max
        self.tib_max_label = QLabel("TIB max")
        self.tib_max_label.setToolTip(
            "Upper limit for time independent background. "
            "TIB min must be less than TIB max, and both have to be in the raw data range."
        )
        tibmm_layout.addWidget(self.tib_max_label)

        self.tib_max_input = QLineEdit()
        self.tib_max_input.setToolTip(
            "Upper limit for time independent background."
            "TIB min must be less than TIB max, and both have to be in the raw data range."
        )
        self.tib_max_input.setValidator(self.double_validator)
        self.tib_max_input.setFixedWidth(80)
        tibmm_layout.addWidget(self.tib_max_input)

        tibmm_widget.setLayout(tibmm_layout)
        layout.addWidget(tibmm_widget, 4, 0, 1, 2)

        # text inputs

        # Goniometer
        gonio_label = QLabel("Goniometer")
        gonio_label.setToolTip(
            "Name of the vertical axis of the goniometer. By default will use the chi, phi, omega "
            "values in the file (see SetGoniometer algorithm)."
        )
        layout.addWidget(gonio_label, 5, 0)

        self.gonio_input = QLineEdit()
        self.gonio_input.setToolTip(
            "Name of the vertical axis of the goniometer. By default will use the chi, phi, omega "
            "values in the file (see SetGoniometer algorithm)."
        )
        layout.addWidget(self.gonio_input, 5, 1)

        # Additional Dimensions
        adt_dim_label = QLabel("Additional Dimensions")
        adt_dim_label.setToolTip(
            "Additional dimensions. Must be comma separated triples of sample log name,\nminimum value, maximum value."
        )
        layout.addWidget(adt_dim_label, 6, 0)

        self.adt_dim_input = QLineEdit()
        self.adt_dim_input.setToolTip(
            "Additional dimensions. Must be comma separated triples of sample log name,\nminimum value, maximum value."
        )
        self.adt_dim_input.setValidator(self.ad_validator)
        layout.addWidget(self.adt_dim_input, 6, 1)

        # buttons
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setStyleSheet("margin-right:30px;padding:3px;")
        layout.addWidget(self.btn_apply, 7, 0)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("margin-right:130px;padding:3px;")
        layout.addWidget(self.btn_cancel, 7, 1)

        self.btn_help = QPushButton("Help")
        layout.addWidget(self.btn_help, 7, 2)

        # on filter check
        self.filter_check.toggled.connect(self.lcutoff_update)
        self.lcutoff_input.textEdited.connect(self.lcutoff_color_update)

        # on emin/emax change
        self.emin_input.textEdited.connect(lambda: self.min_max_checked(self.emin_input, self.emax_input, False))
        self.emax_input.textEdited.connect(lambda: self.min_max_checked(self.emin_input, self.emax_input, False))
        # on tib min/max change
        self.tib_min_input.textEdited.connect(
            lambda: self.min_max_checked(self.tib_min_input, self.tib_max_input, True)
        )
        self.tib_max_input.textEdited.connect(
            lambda: self.min_max_checked(self.tib_min_input, self.tib_max_input, True)
        )

        # on apply tib change
        self.tib_yes.toggled.connect(self.tib_update)
        self.tib_no.toggled.connect(self.tib_update)
        self.tib_default.toggled.connect(self.tib_update)

        # on additional dimensions change
        self.adt_dim_input.textEdited.connect(self.adt_dim_update)

        # button actions
        self.add_btn.clicked.connect(self.btn_add_row)
        self.delete_btn.clicked.connect(self.btn_delete_row)

        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_help.clicked.connect(self.btn_help_action)

        # initialize inputs' visibility
        self.tib_default.setChecked(True)
        self.lcutoff_label.setVisible(False)
        self.lcutoff_input.setVisible(False)

        # cell validation
        self.cell_boundaries = {
            self.table_headers[0]: {"min": 1, "max": 200},  # "Bank",
            self.table_headers[1]: {"min": 1, "max": 8},  # "Tube"
            self.table_headers[2]: {"min": 1, "max": 128},  # "Pixel"
        }
        self.clicked_row = -1
        self.table_view.itemChanged.connect(self.validate_cell)
        self.table_view.itemSelectionChanged.connect(self.get_clicked_row)

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

    def set_cell_invalid_state(self, item):
        """include the item in the invalid_cells and field_error list and disable the corresponding button"""
        if item not in self.invalid_fields:
            self.invalid_fields.append(item)
        if item not in self.invalid_cells:
            self.invalid_cells.append(item)

        if len(self.invalid_cells) > 0:
            self.table_view.setStyleSheet(INVALID_QTABLEWIDGET)
        self.btn_apply.setEnabled(False)

    def set_cell_valid_state(self, item):
        """remove the item from the invalid_cells and field_error list and enable the corresponding button"""
        if item in self.invalid_fields:
            self.invalid_fields.remove(item)
        if item in self.invalid_cells:
            self.invalid_cells.remove(item)

        if len(self.invalid_cells) == 0:
            self.table_view.setStyleSheet("")
        if len(self.invalid_fields) == 0:
            self.btn_apply.setEnabled(True)

    def initialize_cells(self):
        """Initialize table cells"""
        self.double_validator = QtGui.QDoubleValidator(self)
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        for row in range(3):
            for column in range(3):
                cell_item = QTableWidgetItem()
                self.table_view.setItem(row, column, cell_item)

    def btn_add_row(self):
        """Add a new row"""
        row = self.table_view.rowCount()
        self.table_view.insertRow(row)
        for column in range(3):
            cell_item = QTableWidgetItem()
            self.table_view.setItem(row, column, cell_item)

    def get_clicked_row(self):
        """Allow for one selected row to be return for possible deletion"""
        selected_items = self.table_view.selectedItems()
        if len(selected_items) == 3:
            row = selected_items[0].row()
            self.clicked_row = row
            for item in selected_items:
                if item.row() != row:
                    self.clicked_row = -1
                    break
        else:
            self.clicked_row = -1

    def btn_delete_row(self):
        """Delete selected row"""
        selected = self.clicked_row
        if selected >= 0:
            # validate the three cells and remove the whole row
            self.set_cell_valid_state(self.table_view.item(selected, 0))
            self.set_cell_valid_state(self.table_view.item(selected, 1))
            self.set_cell_valid_state(self.table_view.item(selected, 2))
            self.table_view.removeRow(selected)
            self.clicked_row = -1
        else:
            self.show_error_message("Select the whole row you would like to delete.")

    def validate_cell(self):
        """Validates the cells using the IntArrayProperty-based format:
        <num1>,<num2>, ..,
        <range1>-<range2>,
        <range1>:<range2>
        <range1>:<range2>:<step>"""

        self.set_cell_valid_state(self.sender().currentItem())
        # check if item exists
        if self.table_view.currentItem():
            cellstring = self.table_view.currentItem().text()
            # empty string is allowed
            teststring = cellstring.strip()
            if len(teststring) != 0:
                column = self.table_view.currentColumn()
                header_label = self.table_view.horizontalHeaderItem(column).text()
                cell_boundaries = self.cell_boundaries[header_label]
                elements = str(teststring).split(",")
                # check each element in the list
                for element in elements:
                    # case it is a single-number
                    try:
                        int(element)
                        if int(element) >= cell_boundaries["min"] and int(element) <= cell_boundaries["max"]:
                            # it is valid move to the next item
                            continue
                        # invalid! add the item to the list of invalid fields
                        self.set_cell_invalid_state(self.sender().currentItem())
                        break
                    except ValueError:
                        # allow any number of white spaces between number(s) and symbols: - , :
                        # case it is a range: <num1>-<num2>
                        found_dash_range = re.match(
                            r"""
                        ^\s*\d+\s* #number with space(s) before and/or after
                        - #range symbol
                        \s*\d+\s*$ #number with space(s) before and/or after
                        """,
                            element,
                            re.VERBOSE,
                        )
                        # case it is a range: <num1>:<num2>, <num1>:<num2>:<step>
                        found_semicolon_range = re.match(
                            r"""^\s*\d+\s* #number with space(s) before and/or after
                        : #semicolon symbol
                        \s*\d+\s* #number with space(s) before and/or after
                        [:\s*\d+\s*]*$ #repeat sequence :<space>*<number><space>* for step
                        """,
                            element,
                            re.VERBOSE,
                        )
                        if found_dash_range or found_semicolon_range:
                            nums = re.split("[-|:]", element)
                            num1, num2 = nums[0], nums[1]
                            # a range should be num1<num2: e.g. 1-4
                            if (
                                int(num1) < int(num2)
                                and int(num1) >= cell_boundaries["min"]
                                and int(num2) <= cell_boundaries["max"]
                            ):
                                # it is valid move to the next item
                                continue
                            # invalid! add the item to the list of invalid fields
                            self.set_cell_invalid_state(self.sender().currentItem())
                            break
                        self.set_cell_invalid_state(self.sender().currentItem())
                        break

    def tib_update(self):
        """Enable/Disable TIB min and max based on the apply tib radio buttons"""
        self.set_field_valid_state(self.tib_min_input)
        self.set_field_valid_state(self.tib_max_input)

        if self.tib_yes.isChecked():
            self.tib_min_label.setVisible(True)
            self.tib_min_input.setVisible(True)
            self.tib_max_label.setVisible(True)
            self.tib_max_input.setVisible(True)
            if self.tib_min_input.text() == "" and self.tib_max_input.text() == "":
                self.set_field_invalid_state(self.tib_min_input)
                self.set_field_invalid_state(self.tib_max_input)
        else:
            self.tib_min_label.setVisible(False)
            self.tib_min_input.setVisible(False)
            self.tib_max_label.setVisible(False)
            self.tib_max_input.setVisible(False)

    def lcutoff_update(self):
        """Enable/Disable LowerCutoff based on the filter check box"""
        if self.filter_check.isChecked():
            self.lcutoff_label.setVisible(True)
            self.lcutoff_input.setVisible(True)
        else:
            self.lcutoff_label.setVisible(False)
            self.lcutoff_input.setVisible(False)

        if self.lcutoff_input.text() == "":
            self.lcutoff_input.setText(self.lcutoff_input_default)
        self.set_field_valid_state(self.lcutoff_input)

    def lcutoff_color_update(self):
        """Update LowerCutoff valid state based on the input"""
        self.set_field_valid_state(self.lcutoff_input)
        if len(self.lcutoff_input.text()) > 0:
            try:
                float(self.lcutoff_input.text())
            except ValueError:
                self.set_field_invalid_state(self.lcutoff_input)

    def min_max_checked(self, min_input, max_input, required):
        """Ensure Minimum and Maximum value pairs are valid and whether they are required"""
        valid = True
        # if min_input is invalid then its pair max_input should be in the invalid fields too
        self.set_field_valid_state(min_input)
        self.set_field_valid_state(max_input)

        min_value = min_input.text()
        max_value = max_input.text()
        # both min and max values need to filled in case of TIB
        if required and (min_value == "" or max_value == ""):
            valid = False
        else:
            valid = self.check_num_input(min_value, max_value)
        if not valid:
            self.set_field_invalid_state(min_input)
            self.set_field_invalid_state(max_input)

    def check_num_input(self, min_value, max_value):
        """Ensure numbers are:
        float, Minimum < Maximum and both exist at the same time"""
        # both min and max values need to filled in
        valid = True
        if (len(max_value) == 0 and len(min_value) != 0) or (len(max_value) != 0 and len(min_value) == 0):
            valid = False
        else:
            if len(min_value) != 0 and len(max_value) != 0:
                try:
                    maxnum = float(max_value)
                    minnum = float(min_value)
                    if maxnum < minnum:
                        valid = False
                except ValueError:
                    valid = False
        return valid

    def adt_dim_update(self):
        """Validate the additional dimension values"""
        sender = self.sender()
        self.set_field_valid_state(sender)
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state in (QtGui.QValidator.Intermediate, QtGui.QValidator.Invalid):
            self.set_field_invalid_state(sender)

    def get_table_values_dict(self):
        """Return table cells as a dictionary"""
        cell_values = []
        rows = self.table_view.rowCount()
        for row in range(rows):
            row_data = {}
            row_data["Bank"] = self.table_view.item(row, 0).text().replace(" ", "")
            row_data["Tube"] = self.table_view.item(row, 1).text().replace(" ", "")
            row_data["Pixel"] = self.table_view.item(row, 2).text().replace(" ", "")
            if not (row_data["Bank"] == "" and row_data["Tube"] == "" and row_data["Pixel"] == ""):
                cell_values.append(row_data)
        return cell_values

    def get_advanced_options_dict(self):
        """Return advanced options as a dictionary"""
        options_dict = {}
        options_dict["MaskInputs"] = self.get_table_values_dict()
        options_dict["E_min"] = None
        if self.emin_input.text():
            options_dict["E_min"] = self.emin_input.text()
        options_dict["E_max"] = None
        if self.emax_input.text():
            options_dict["E_max"] = self.emax_input.text()

        options_dict["ApplyFilterBadPulses"] = self.filter_check.isChecked()
        options_dict["BadPulsesThreshold"] = None
        if self.lcutoff_input.text():
            options_dict["BadPulsesThreshold"] = self.lcutoff_input.text()
        timewindow = ""
        if self.tib_default.isChecked():
            timewindow = "Default"
        elif self.tib_yes.isChecked():
            timewindow = f"{self.tib_min_input.text()}, {self.tib_max_input.text()}"
        else:
            timewindow = None

        options_dict["TimeIndepBackgroundWindow"] = timewindow
        options_dict["Goniometer"] = self.gonio_input.text()
        options_dict["AdditionalDimensions"] = None
        if self.adt_dim_input.text():
            options_dict["AdditionalDimensions"] = self.adt_dim_input.text()
        return options_dict

    def set_table_values(self, maskinputs):
        """Populate all table rows from list of rows"""
        for row, row_data in enumerate(maskinputs):
            # by default 3 rows are added in the table
            # a new row needs to be added
            if row >= 3:
                self.btn_add_row()
            if len(row_data.keys()) == 3:
                self.table_view.item(row, 0).setText(row_data["Bank"])
                self.table_view.item(row, 1).setText(row_data["Tube"])
                self.table_view.item(row, 2).setText(row_data["Pixel"])
            else:
                self.show_error_message("Invalid dictionary format: MaskInputs table")
                break

    def populate_advanced_options_from_dict(self, params):
        """Populate all fields from dictionary"""

        self.set_table_values(params.get("MaskInputs", ""))
        self.emin_input.setText(params.get("E_min", ""))
        self.emax_input.setText(params.get("E_max", ""))

        self.filter_check.setChecked(params.get("ApplyFilterBadPulses", False))

        # in case None is passed, field is ""
        self.lcutoff_input.setText(params.get("BadPulsesThreshold", ""))

        tib_option = params.get("TimeIndepBackgroundWindow", "Default")

        # NOTE: tib_option should not have been set to None, but it seems like
        #       something is trying to set it to None due to historical reasons,
        #       and this is a quick fix to avoid unnecessary errors.
        if tib_option is None:
            tib_option = ""

        if tib_option == "Default":
            self.tib_default.setChecked(True)
        elif tib_option == "":
            self.tib_no.setChecked(True)
        else:
            self.tib_yes.setChecked(True)
            tib_min, tib_max = tib_option.split(",")
            self.tib_min_input.setText(tib_min)
            self.tib_max_input.setText(tib_max)

        self.gonio_input.setText(params.get("Goniometer", ""))
        self.adt_dim_input.setText(params.get("AdditionalDimensions", ""))

    def btn_apply_submit(self):
        """Check everything is valid and close dialog"""

        if len(self.invalid_fields) == 0:
            self.parent.dict_advanced = self.get_advanced_options_dict()
            self.close()
        else:
            self.show_error_message("Invalid input(s). Please correct the marked fields.")

    def btn_cancel_action(self):
        """Cancel the sample dialog"""
        self.done(1)

    def btn_help_action(self):
        """Show the help for the sample dialog"""
        help_function(context="advanced")

    def show_error_message(self, msg):
        """Will show a error dialog with the given message"""
        self.error = QErrorMessage(self)
        self.error.showMessage(msg)
        self.error.exec_()
        self.error = None
