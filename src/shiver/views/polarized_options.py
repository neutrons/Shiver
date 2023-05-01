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


class PolarizedDialog(QDialog):
    """Polarized Options widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setWindowTitle("Polarized Options")
        self.parent = parent
        # validators
        self.double_validator = QtGui.QDoubleValidator(self)
        # standard decimal point-format for example: 1.2
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.ad_validator = ADValidator(self)
        # keep track of the fields with invalid inputs
        self.invalid_fields = []

        self.error = None

        # Polarized labels
        layout.addWidget(QLabel("Polarized State"), 0, 0)
        layout.addWidget(QLabel("Polarized direction"), 0, 2)
        
        #state
        state_widget = QWidget()
        state_layout = QVBoxLayout()
        state_layout.setContentsMargins(0, 0, 0, 0)

        self.state_unpolarized = QRadioButton("Unpolarized")
        state_layout.addWidget(self.state_unpolarized)

        self.state_spin = QRadioButton("Spin flip")
        state_layout.addWidget(self.state_spin)

        self.state_no_spin = QRadioButton("Non spin flip")
        state_layout.addWidget(self.state_no_spin)

        state_widget.setLayout(state_layout)
        layout.addWidget(state_widget, 1, 0)
        
        #direction
        direction_widget = QWidget()
        direction_layout = QVBoxLayout()
        direction_layout.setContentsMargins(10, 0, 10, 0)

        self.dir_pz = QRadioButton("Pz (vertical)")
        direction_layout.addWidget(self.dir_pz)

        self.dir_px = QRadioButton("Px")
        direction_layout.addWidget(self.dir_px)

        self.dir_py = QRadioButton("Py")
        direction_layout.addWidget(self.dir_py)

        direction_widget.setLayout(direction_layout)
        layout.addWidget(direction_widget, 1, 2)

        #ratio
        layout.addWidget(QLabel("Flipping Ratio"), 2, 0)
        self.ratio = QLineEdit()
        layout.addWidget(self.ratio, 2, 1)

        #log
        layout.addWidget(QLabel("Sample log"), 2, 2)
        self.log = QLineEdit()
        layout.addWidget(self.log, 2, 3)
        
        # buttons
        self.btn_apply = QPushButton("Apply")
        #self.btn_apply.setStyleSheet("margin-right:30px;padding:3px;")
        layout.addWidget(self.btn_apply, 3, 0)

        self.btn_cancel = QPushButton("Cancel")
        #self.btn_cancel.setStyleSheet("margin-right:130px;padding:3px;")
        layout.addWidget(self.btn_cancel, 3, 1)

        self.btn_help = QPushButton("Help")
        layout.addWidget(self.btn_help, 3, 3)


        # on additional dimensions change
        #self.adt_dim_input.textEdited.connect(self.adt_dim_update)

        # button actions
        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_help.clicked.connect(self.btn_help_action)




    def adt_dim_update(self):
        """Validate the projection values"""
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



    def get_polarized_options_dict(self):
        """Return polarized options as a dictionary"""
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
            self.parent.dict_polarized = self.get_polarized_options_dict()
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
