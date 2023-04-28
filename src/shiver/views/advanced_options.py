"""PyQt QDialog for Sample Parameters"""
import re
import webbrowser

from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QLabel,
    QDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QErrorMessage,
    QCheckBox,
    QRadioButton,
)

from qtpy.QtCore import Qt


try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")


def return_valid(validity, teststring, pos):
    """Returns state during validation"""
    if QString == str:
        return (validity, teststring, pos)
    return (validity, pos)


class ADValidator(QtGui.QValidator):
    """Validates the additional dimensions value"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, teststring, pos):
        """Validates in 3-element comma-separated format: <string>,<number>,<number>"""

        # empty string is allowed
        if len(teststring.strip()) == 0:
            return return_valid(QtGui.QValidator.Acceptable, teststring, pos)

        elements = str(teststring.strip()).split(",")
        # invalid number of digits
        if len(elements) > 3:
            return return_valid(QtGui.QValidator.Invalid, teststring, pos)
        if len(elements) == 3 and len(str(elements[0].strip())) != 0:
            try:
                # valid case with 1 string 2 float numbers
                str(elements[0])
                float(elements[1])
                float(elements[2])
                return return_valid(QtGui.QValidator.Acceptable, teststring, pos)
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


class AdvancedDialog(QDialog):
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

        self.error = None
        # table data
        table_label = QLabel("Mask Bank, Tube, Pixel")
        table_label.setAlignment(Qt.AlignTop)
        layout.addWidget(table_label, 0, 0)

        self.table_view = QTableWidget()
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
        table_btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Row")
        table_btn_layout.addWidget(self.delete_btn)

        table_btns.setLayout(table_btn_layout)
        layout.addWidget(table_btns, 0, 2)

        e_widget = QWidget()
        e_layout = QGridLayout()
        e_layout.setContentsMargins(0, 0, 0, 0)
        # Emin - Emax
        emin_label = QLabel("Emin")
        e_layout.addWidget(emin_label, 0, 0)

        self.emin_input = QLineEdit()
        self.emin_input.setValidator(self.double_validator)
        self.emin_input.setFixedWidth(80)
        e_layout.addWidget(self.emin_input, 0, 1)

        # Emax
        emax_label = QLabel("Emax")
        e_layout.addWidget(emax_label, 0, 2)

        self.emax_input = QLineEdit()
        self.emax_input.setValidator(self.double_validator)
        self.emax_input.setFixedWidth(80)
        e_layout.addWidget(self.emax_input, 0, 3)

        e_widget.setLayout(e_layout)
        layout.addWidget(e_widget, 1, 0, 1, 2)

        # 2nd row
        # filter
        self.filter_check = QCheckBox("Apply filter bad pulses")
        e_layout.addWidget(self.filter_check, 1, 0, 1, 2)

        self.lcutoff_label = QLabel("LowerCutoff (%)")
        e_layout.addWidget(self.lcutoff_label, 1, 2)

        self.lcutoff_input_default = "95"
        self.lcutoff_input = QLineEdit(self.lcutoff_input_default)
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

        self.tib_default = QRadioButton("Instrument default")
        tib_layout.addWidget(self.tib_default)

        self.tib_yes = QRadioButton("Yes")
        tib_layout.addWidget(self.tib_yes)

        self.tib_no = QRadioButton("No")
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
        tibmm_layout.addWidget(self.tib_min_label)

        self.tib_min_input = QLineEdit()
        self.tib_min_input.setValidator(self.double_validator)
        self.tib_min_input.setFixedWidth(80)
        tibmm_layout.addWidget(self.tib_min_input)

        # TIB max
        self.tib_max_label = QLabel("TIB max")
        tibmm_layout.addWidget(self.tib_max_label)

        self.tib_max_input = QLineEdit()
        self.tib_max_input.setValidator(self.double_validator)
        self.tib_max_input.setFixedWidth(80)
        tibmm_layout.addWidget(self.tib_max_input)

        tibmm_widget.setLayout(tibmm_layout)
        layout.addWidget(tibmm_widget, 4, 0, 1, 2)

        # text inputs

        # Goniometer
        gonio_label = QLabel("Goniometer")
        layout.addWidget(gonio_label, 5, 0)

        self.gonio_input = QLineEdit()
        layout.addWidget(self.gonio_input, 5, 1)

        # Additional Dimensions
        adt_dim_label = QLabel("Additional Dimensions")
        layout.addWidget(adt_dim_label, 6, 0)

        self.adt_dim_input = QLineEdit()
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
        # self.lcutoff_input.textEdited.connect(self.lcutoff_color_update)

        # on emin/emax change
        self.emin_input.textEdited.connect(lambda: self.min_max_checked(self.emin_input, self.emax_input))
        self.emax_input.textEdited.connect(lambda: self.min_max_checked(self.emin_input, self.emax_input))
        # on tib min/max change
        self.tib_min_input.textEdited.connect(lambda: self.min_max_checked(self.tib_min_input, self.tib_max_input))
        self.tib_max_input.textEdited.connect(lambda: self.min_max_checked(self.tib_min_input, self.tib_max_input))

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
        color = "#ffffff"

        if self.sender().currentItem() in self.invalid_fields:
            self.invalid_fields.remove(self.sender().currentItem())
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
                        color = "#ff0000"
                        self.invalid_fields.append(self.sender().currentItem())
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
                            color = "#ff0000"
                            self.invalid_fields.append(self.sender().currentItem())
                            break
                        color = "#ff0000"
                        self.invalid_fields.append(self.sender().currentItem())
                        break
            self.table_view.currentItem().setBackground(QtGui.QColor(color))

            # set the selected item background color to red to indicate error
            if color == "#ff0000":
                self.table_view.setStyleSheet("QTableView::item:selected {background-color : #ff0000;}")
                # remove selected background color on the next click
                self.table_view.cellClicked.connect(self.remove_bg_color)

    def remove_bg_color(self):
        """Remove the selected item background color"""
        self.table_view.setStyleSheet("")
        self.table_view.cellClicked.disconnect()

    def tib_update(self):
        """Enable/Disable TIB min and max based on the apply tib radio buttons"""
        color = "#ffffff"
        if self.tib_min_input in self.invalid_fields:
            self.invalid_fields.remove(self.tib_min_input)
        if self.tib_max_input in self.invalid_fields:
            self.invalid_fields.remove(self.tib_max_input)

        if self.tib_yes.isChecked():
            self.tib_min_label.setVisible(True)
            self.tib_min_input.setVisible(True)
            self.tib_max_label.setVisible(True)
            self.tib_max_input.setVisible(True)
            if self.tib_min_input.text() == "" and self.tib_max_input.text() == "":
                color = "#ffaaaa"
                self.invalid_fields.append(self.tib_min_input)
                self.invalid_fields.append(self.tib_max_input)
        else:
            self.tib_min_label.setVisible(False)
            self.tib_min_input.setVisible(False)
            self.tib_max_label.setVisible(False)
            self.tib_max_input.setVisible(False)

        self.tib_min_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")
        self.tib_max_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")

    def lcutoff_update(self):
        """Enable/Disable LowerCutoff based on the filter check box"""
        color = "#ffffff"
        if self.filter_check.isChecked():
            self.lcutoff_label.setVisible(True)
            self.lcutoff_input.setVisible(True)
        else:
            self.lcutoff_label.setVisible(False)
            self.lcutoff_input.setVisible(False)

        if self.lcutoff_input.text() == "":
            self.lcutoff_input.setText(self.lcutoff_input_default)
        self.lcutoff_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")

    def lcutoff_color_update(self):
        """Update LowerCutoff background color based on the filter check box"""
        color = "#ffffff"
        if self.lcutoff_input in self.invalid_fields:
            self.invalid_fields.remove(self.lcutoff_input)
        if self.filter_check.isChecked() and self.lcutoff_input.text() == "":
            color = "#ff0000"
            self.invalid_fields.append(self.lcutoff_input)
        self.lcutoff_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")

    def min_max_checked(self, min_input, max_input):
        """Ensure Minimum and Maximum value pairs are:
        float numbers, Minimum < Maximum and both exist at the same time"""
        sender = self.sender()
        color = "#ffffff"

        # if min_input is invalid then its pair max_input should be in the invalid fields too
        if min_input in self.invalid_fields:
            self.invalid_fields.remove(min_input)
            self.invalid_fields.remove(max_input)

        min_value = min_input.text()
        max_value = max_input.text()
        if sender == min_input:
            # both min and max values need to filled in
            if (len(min_value) == 0 and len(max_value) != 0) or (len(min_value) != 0 and len(max_value) == 0):
                color = "#ff0000"
            else:
                # needs to be number and less than max
                if len(min_value) != 0:
                    try:
                        tempvalue = float(min_value)
                        if tempvalue > float(max_value):
                            color = "#ff0000"
                    except ValueError:
                        color = "#ff0000"
        if sender == max_input:
            # both min and max values need to filled in
            if (len(max_value) == 0 and len(min_value) != 0) or (len(max_value) != 0 and len(min_value) == 0):
                color = "#ff0000"
            else:
                # needs to be number and greater than min
                if len(max_value) != 0:
                    try:
                        tempvalue = float(max_value)
                        if tempvalue < float(min_value):
                            color = "#ff0000"
                    except ValueError:
                        color = "#ff0000"

        if color == "#ff0000":
            self.invalid_fields.append(min_input)
            self.invalid_fields.append(max_input)
        min_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")
        max_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")

    def adt_dim_update(self):
        """Validate the additional dimension values"""
        sender = self.sender()
        if sender in self.invalid_fields:
            self.invalid_fields.remove(sender)
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = "#ffffff"
        elif state == QtGui.QValidator.Intermediate:
            color = "#ffaaaa"
            self.invalid_fields.append(sender)
        else:
            color = "#ff0000"
            self.invalid_fields.append(sender)
        sender.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")

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
        options_dict["E_min"] = self.emin_input.text()
        options_dict["E_max"] = self.emax_input.text()
        options_dict["ApplyFilterBadPulses"] = self.filter_check.isChecked()
        options_dict["BadPulsesThreshold"] = self.lcutoff_input.text()
        timewindow = ""
        if self.tib_default.isChecked():
            timewindow = "Default"
        elif self.tib_yes.isChecked():
            timewindow = [self.tib_min_input.text(), self.tib_max_input.text()]
        else:
            timewindow = None

        options_dict["TimeIndepBackgroundWindow"] = timewindow
        options_dict["Goniometer"] = self.gonio_input.text()
        options_dict["AdditionalDimensions"] = self.adt_dim_input.text()
        return options_dict

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
        webbrowser.open("https://neutrons.github.io/Shiver/GUI/")

    def show_error_message(self, msg):
        """Will show a error dialog with the given message"""
        self.error = QErrorMessage(self)
        self.error.showMessage(msg)
        self.error.exec_()
        self.error = None
