"""PyQt QDialog for Sample Parameters"""
import webbrowser
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QLabel,
    QDialog,
    QErrorMessage,
    QRadioButton,
)


try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")


def return_valid(validity, teststring, pos):
    """Returns state during validation"""
    if QString == str:
        return (validity, teststring, pos)
    return (validity, pos)


class RatioValidator(QtGui.QValidator):
    """Validates the additional dimensions value"""

    def __init__(self, log_input, parent=None):
        super().__init__(parent)
        self.log_input = log_input

    def validate(self, teststring, pos):
        """Validates number or formula"""
        log_param = self.log_input.text()
        # number
        try:
            float(teststring)
            return return_valid(QtGui.QValidator.Acceptable, teststring, pos)
        except ValueError:
            # formula
            try:
                str(teststring)
                if teststring != "" and log_param in teststring:
                    return return_valid(QtGui.QValidator.Acceptable, teststring, pos)
                return return_valid(QtGui.QValidator.Intermediate, teststring, pos)
            except ValueError:
                return return_valid(QtGui.QValidator.Invalid, teststring, pos)


class PolarizedDialog(QDialog):
    """Polarized Options widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setWindowTitle("Polarized Options")
        self.parent = parent
        # keep track of the fields with invalid inputs
        self.invalid_fields = []

        self.error = None

        # Polarized labels
        self.state_label = QLabel("Polarized State")
        layout.addWidget(self.state_label, 0, 0)
        self.dir_label = QLabel("Polarized direction\nPlease select one below:")
        layout.addWidget(self.dir_label, 0, 2, 1, 2)

        size_policy = self.dir_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.dir_label.setSizePolicy(size_policy)

        # state
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

        # direction
        direction_widget = QWidget()
        size_policy = direction_widget.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        direction_widget.setSizePolicy(size_policy)

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

        # ratio
        self.ratio_label = QLabel("Flipping Ratio")
        layout.addWidget(self.ratio_label, 2, 0)
        self.ratio_input = QLineEdit()
        layout.addWidget(self.ratio_input, 2, 1)

        # ratio size policies
        size_policy = self.ratio_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.ratio_label.setSizePolicy(size_policy)

        size_policy = self.ratio_input.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.ratio_input.setSizePolicy(size_policy)

        # log
        self.log_label = QLabel("Sample log")
        layout.addWidget(self.log_label, 2, 2)
        self.log_input = QLineEdit()
        layout.addWidget(self.log_input, 2, 3)

        # log size policies
        size_policy = self.log_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.log_label.setSizePolicy(size_policy)

        size_policy = self.log_input.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.log_input.setSizePolicy(size_policy)

        # buttons
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setStyleSheet("margin-right:40px;padding:3px;")
        layout.addWidget(self.btn_apply, 3, 0)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("margin-left:40px;padding:3px;")
        layout.addWidget(self.btn_cancel, 3, 1)

        self.btn_help = QPushButton("Help")
        self.btn_help.setStyleSheet("margin-left:40px;padding:3px;")
        layout.addWidget(self.btn_help, 3, 3)

        # validators
        self.ratio_validator = RatioValidator(self.log_input, self)
        self.ratio_input.setValidator(self.ratio_validator)

        # on polarization state change
        self.state_unpolarized.toggled.connect(self.disable_params)
        self.state_spin.toggled.connect(self.enable_params)
        self.state_no_spin.toggled.connect(self.enable_params)

        # on flipping ratio change
        self.ratio_input.textEdited.connect(self.ratio_update)

        # on direction change
        self.dir_pz.toggled.connect(self.dir_update)
        self.dir_px.toggled.connect(self.dir_update)
        self.dir_py.toggled.connect(self.dir_update)

        # on log change
        self.log_input.textEdited.connect(self.log_update)

        # button actions
        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_help.clicked.connect(self.btn_help_action)

        # initialize
        self.state_unpolarized.setChecked(True)

    def disable_params(self):
        """Disable/hide direction, ratio and log parameters"""
        if self.state_unpolarized.isChecked():
            self.ratio_label.setVisible(False)
            self.ratio_input.setVisible(False)

            self.log_label.setVisible(False)
            self.log_input.setVisible(False)

            self.dir_label.setVisible(False)
            self.dir_pz.setVisible(False)
            self.dir_px.setVisible(False)
            self.dir_py.setVisible(False)

            # remove them from invalid_fields
            if self.ratio_input in self.invalid_fields:
                self.invalid_fields.remove(self.ratio_input)
            if self.log_input in self.invalid_fields:
                self.invalid_fields.remove(self.log_input)
            if self.dir_label in self.invalid_fields:
                self.invalid_fields.remove(self.dir_label)

    def enable_params(self):
        """Enable/show direction, ratio and log parameters"""
        if self.sender().isChecked():
            self.ratio_label.setVisible(True)
            self.ratio_input.setVisible(True)

            self.log_label.setVisible(True)
            self.log_input.setVisible(True)

            self.dir_label.setVisible(True)
            self.dir_pz.setVisible(True)
            self.dir_px.setVisible(True)
            self.dir_py.setVisible(True)

            # check and add them from invalid_fields
            if self.ratio_input.text() == "":
                self.invalid_fields.append(self.ratio_input)
                color = "#ff0000"
                self.ratio_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")
            if self.log_input.text() == "":
                self.invalid_fields.append(self.log_input)
                color = "#ff0000"
                self.log_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")
            if not self.dir_pz.isChecked() and not self.dir_px.isChecked() and not self.dir_py.isChecked():
                self.invalid_fields.append(self.dir_label)

    def dir_update(self):
        """Remove direction from invalid_fields"""
        if self.sender().isChecked():
            if self.dir_label in self.invalid_fields:
                self.invalid_fields.remove(self.dir_label)

    def log_update(self):
        """Check sample log and update ratio validation status"""
        self.log_validate()
        self.ratio_update()

    def log_validate(self):
        """Check whether sample log is in valid state"""
        color = "#ffffff"
        if self.log_input in self.invalid_fields:
            self.invalid_fields.remove(self.log_input)

        # check if it is mandatory field
        if self.state_spin.isChecked() or self.state_no_spin.isChecked():
            # check flipping ratio
            ratio = self.ratio_input.text()
            try:
                float(ratio)
            except ValueError:
                # if ratio is string-fornula then this needs to be non-empty
                if self.log_input.text() == "":
                    self.invalid_fields.append(self.log_input)
                    color = "#ff0000"
        self.log_input.setStyleSheet(f"QLineEdit {{ background-color: {color} }}")

    def ratio_update(self):
        """Validate the ratio value"""
        sender = self.ratio_input
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
        self.log_validate()

    def get_polarized_state(self):
        """Return polarized state fromstate and direction"""
        state = None
        if self.state_unpolarized.isChecked():
            return state
        if self.state_spin.isChecked():
            state = "SF"
        else:
            state = "NSF"

        if self.dir_pz.isChecked():
            state += "_Pz"
        elif self.dir_px.isChecked():
            state += "_Px"
        else:
            state += "_Py"
        return state

    def get_polarized_options_dict(self):
        """Return polarized options as a dictionary"""
        options_dict = {}

        options_dict["PolarizationState"] = self.get_polarized_state()
        if self.ratio_input.text():
            options_dict["FlippingRatio"] = self.ratio_input.text()
        else:
            options_dict["FlippingRatio"] = None
        options_dict["SampleLog"] = self.log_input.text()
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