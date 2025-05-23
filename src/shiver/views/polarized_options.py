"""PyQt QDialog for Sample Parameters"""

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
from qtpy.QtCore import Qt

from shiver.models.help import help_function
from .invalid_styles import INVALID_QLINEEDIT


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


class PolarizedView(QWidget):
    """View for Sample Parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialog = None
        self.parent = parent
        self.parameters = {}
        self.apply_submit_callback = None
        self.get_polarized_options_callback = None

    def start_dialog(self, disable_psda=False):
        """initialize and start dialog"""
        self.dialog = PolarizedDialog(parent=self, disable_psda=disable_psda)
        self.dialog.setAttribute(Qt.WA_DeleteOnClose)
        return self.dialog

    def get_error_message(self, msg):
        """received the error message from model"""
        self.dialog.show_error_message(msg)

    def connect_apply_submit(self, callback):
        """connect to save the polarization logs for workspace"""
        self.apply_submit_callback = callback

    def connect_populate_polarized_options(self, callback):
        """connect to get the polarization logs for workspace"""
        self.get_polarized_options_callback = callback

    def set_parameter_dict(self):
        """Set all polarized parameters as a dictionary in current and parent view"""
        self.parameters = self.dialog.get_polarized_options_dict()
        if self.parent:
            self.parent.dict_polarized = self.parameters


class PolarizedDialog(QDialog):
    """Polarized Options widget"""

    def __init__(self, parent=None, disable_psda=False):
        super().__init__(parent)
        # psda readonly flag
        self.disable_psda = disable_psda
        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setWindowTitle("Polarization Options")
        self.parent = parent
        # keep track of the fields with invalid inputs
        self.invalid_fields = []
        self.double_validator = QtGui.QDoubleValidator(self)
        # standard decimal point-format for example: 1.2
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.error = None

        state_tooltip = "Polarization state."
        direction_tooltip = "Polarization direction - for SF or NSF polarization states."
        # Polarized labels
        self.state_label = QLabel("Polarization State")
        self.state_label.setToolTip(state_tooltip)
        layout.addWidget(self.state_label, 0, 0)
        self.dir_label = QLabel("Polarization direction\nPlease select one below:")
        self.dir_label.setToolTip(direction_tooltip)
        layout.addWidget(self.dir_label, 0, 2, 1, 2)

        size_policy = self.dir_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.dir_label.setSizePolicy(size_policy)

        # state
        state_widget = QWidget()
        state_layout = QVBoxLayout()
        state_layout.setContentsMargins(0, 0, 0, 0)

        self.state_unpolarized = QRadioButton("Unpolarized")
        self.state_unpolarized.setToolTip(state_tooltip)
        state_layout.addWidget(self.state_unpolarized)

        self.state_spin = QRadioButton("Spin flip")
        self.state_spin.setToolTip(state_tooltip)
        state_layout.addWidget(self.state_spin)

        self.state_no_spin = QRadioButton("Non spin flip")
        self.state_no_spin.setToolTip(state_tooltip)
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
        self.dir_pz.setToolTip(direction_tooltip)
        self.dir_pz.setChecked(True)
        direction_layout.addWidget(self.dir_pz)

        self.dir_px = QRadioButton("Px")
        self.dir_px.setToolTip(direction_tooltip)
        direction_layout.addWidget(self.dir_px)

        self.dir_py = QRadioButton("Py")
        self.dir_py.setToolTip(direction_tooltip)
        direction_layout.addWidget(self.dir_py)

        direction_widget.setLayout(direction_layout)
        layout.addWidget(direction_widget, 1, 2)

        fr_tooltip = (
            "Flipping ratio. Can be either a number, or an expression involving a sample log."
            "\nIf an expressionis used, the sample log name must be present as well."
            "\nFor example, '6.5+2.8*cos((omega+3.7)*pi/180)'."
        )
        # ratio
        self.ratio_label = QLabel("Flipping Ratio")
        self.ratio_label.setToolTip(fr_tooltip)
        layout.addWidget(self.ratio_label, 2, 0)
        self.ratio_input = QLineEdit()
        self.ratio_input.setToolTip(fr_tooltip)
        layout.addWidget(self.ratio_input, 2, 1)

        # ratio size policies
        size_policy = self.ratio_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.ratio_label.setSizePolicy(size_policy)

        size_policy = self.ratio_input.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.ratio_input.setSizePolicy(size_policy)

        # log
        self.log_label = QLabel("Flipping Ratio Sample log")
        self.log_label.setToolTip(fr_tooltip)
        layout.addWidget(self.log_label, 2, 2)
        self.log_input = QLineEdit()
        self.log_input.setToolTip(fr_tooltip)
        layout.addWidget(self.log_input, 2, 3)

        # log size policies
        size_policy = self.log_label.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.log_label.setSizePolicy(size_policy)

        size_policy = self.log_input.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.log_input.setSizePolicy(size_policy)

        self.psda_label = QLabel("PSDA")
        layout.addWidget(self.psda_label, 3, 0)
        self.psda_input = QLineEdit()
        self.psda_input.setToolTip(
            "Polarization supermirror deflection angle - will override the value in the raw data."
        )
        self.psda_input.setValidator(self.double_validator)
        self.psda_input.setDisabled(disable_psda)
        layout.addWidget(self.psda_input, 3, 1)

        # buttons
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setStyleSheet("margin-right:40px;padding:3px;")
        layout.addWidget(self.btn_apply, 4, 0)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("margin-left:40px;padding:3px;")
        layout.addWidget(self.btn_cancel, 4, 1)

        self.btn_help = QPushButton("Help")
        self.btn_help.setStyleSheet("margin-left:40px;padding:3px;")
        layout.addWidget(self.btn_help, 4, 3)

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

        # on psda change
        self.psda_input.textEdited.connect(self.psda_update)

        # button actions
        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_help.clicked.connect(self.btn_help_action)

        # initialize
        self.state_unpolarized.setChecked(True)

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
            self.set_field_valid_state(self.ratio_input)
            self.set_field_valid_state(self.log_input)
            self.set_field_valid_state(self.dir_label)

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

            # check and add them as invalid_fields
            self.log_update()
            if not self.dir_pz.isChecked() and not self.dir_px.isChecked() and not self.dir_py.isChecked():
                self.set_field_invalid_state(self.dir_label)

    def dir_update(self):
        """Remove direction from invalid_fields"""
        if self.sender().isChecked():
            self.set_field_valid_state(self.dir_label)

    def log_update(self):
        """Check sample log and update ratio validation status"""
        self.log_validate()
        self.ratio_update()

    def log_validate(self):
        """Check whether sample log is in valid state"""
        self.set_field_valid_state(self.log_input)

        # check if it is mandatory field
        if self.state_spin.isChecked() or self.state_no_spin.isChecked():
            # check flipping ratio
            ratio = self.ratio_input.text()
            try:
                float(ratio)
            except ValueError:
                # if ratio is string-formula then this needs to be non-empty
                if self.log_input.text() == "":
                    self.set_field_invalid_state(self.log_input)

    def ratio_update(self):
        """Validate the ratio value"""
        sender = self.ratio_input
        self.set_field_valid_state(sender)

        # check if it is mandatory field
        if self.state_spin.isChecked() or self.state_no_spin.isChecked():
            validator = sender.validator()
            state = validator.validate(sender.text(), 0)[0]
            if state in (QtGui.QValidator.Intermediate, QtGui.QValidator.Invalid):
                self.set_field_invalid_state(sender)
        self.log_validate()

    def psda_update(self):
        """Validate the psda value"""
        sender = self.psda_input
        self.set_field_valid_state(sender)

        if sender.text() != "":
            try:
                value = float(sender.text())
                if value < -5 or value > 5:
                    self.set_field_invalid_state(sender)
            except ValueError:
                self.set_field_invalid_state(sender)

    def get_polarized_state(self):
        """Return polarized state"""
        state = None
        if self.state_unpolarized.isChecked():
            state = "UNP"
        elif self.state_spin.isChecked():
            state = "SF"
        else:
            state = "NSF"
        return state

    def get_polarized_direction(self):
        """Return polarized direction"""
        state = None
        if self.dir_pz.isChecked():
            state = "Pz"
        elif self.dir_px.isChecked():
            state = "Px"
        else:
            state = "Py"
        return state

    def get_polarized_options_dict(self):
        """Return polarized options as a dictionary"""
        options_dict = {}

        options_dict["PolarizationState"] = self.get_polarized_state()
        options_dict["PolarizationDirection"] = self.get_polarized_direction()

        if self.ratio_input.text():
            options_dict["FlippingRatio"] = self.ratio_input.text()
        else:
            options_dict["FlippingRatio"] = None
        if self.psda_input.text():
            options_dict["PSDA"] = self.psda_input.text()
        else:
            options_dict["PSDA"] = None
        options_dict["FlippingRatioSampleLog"] = self.log_input.text()
        return options_dict

    def set_polarized_state_dir(self, params):
        """Set state and direction from polarized state"""
        if params["PolarizationState"] == "UNP" or params["PolarizationState"] is None:
            self.state_unpolarized.setChecked(True)
        elif params["PolarizationState"] == "SF":
            self.state_spin.setChecked(True)
        else:
            self.state_no_spin.setChecked(True)

        # polarization direction is an optional parameter
        if (
            "PolarizationDirection" not in params
            or params["PolarizationDirection"] == "Pz"
            or params["PolarizationDirection"] is None
        ):
            self.dir_pz.setChecked(True)
        elif params["PolarizationDirection"] == "Px":
            self.dir_px.setChecked(True)
        else:
            self.dir_py.setChecked(True)

    def populate_pol_options_from_dict(self, params):
        """Populate all fields from dictionary"""
        # check dictionary format
        expected_keys = [
            "PolarizationState",
            # "PolarizationDirection",
            "FlippingRatio",
            "FlippingRatioSampleLog",
            "PSDA",
        ]
        for param in expected_keys:
            if param not in params.keys():
                self.show_error_message(f"Invalid dinctionary format. Missing: {param}")
                return

        self.set_polarized_state_dir(params)
        if params["FlippingRatio"] is not None:
            self.ratio_input.setText(params["FlippingRatio"])
        self.log_input.setText(params["FlippingRatioSampleLog"])
        if params["PSDA"] is not None:
            self.psda_input.setText(str(params["PSDA"]))
        self.log_update()

    def populate_polarized_options(self):
        """Populate all fields from workspace"""
        params = {}
        if self.parent.get_polarized_options_callback:
            params = self.parent.get_polarized_options_callback()
        if len(params) > 0:
            self.set_polarized_state_dir(params)
            if params["FlippingRatio"] is not None:
                self.ratio_input.setText(params["FlippingRatio"])
            self.log_input.setText(params["FlippingRatioSampleLog"])
            if params["PSDA"] is not None:
                self.psda_input.setText(str(params["PSDA"]))
            self.log_update()

    def btn_apply_submit(self):
        """Check everything is valid and close dialog"""
        if len(self.invalid_fields) == 0:
            dict_polarized = self.get_polarized_options_dict()
            # update the grand/parent view
            if self.parent:
                self.parent.set_parameter_dict()
            # save them in the workspace
            if self.parent.apply_submit_callback:
                self.parent.apply_submit_callback(dict_polarized)
            self.close()
        else:
            self.show_error_message("Invalid input(s). Please correct the marked fields.")

    def btn_cancel_action(self):
        """Cancel the sample dialog"""
        self.done(1)

    def btn_help_action(self):
        """Show the help for the sample dialog"""
        help_function(context="polarization")

    def show_error_message(self, msg):
        """Will show a error dialog with the given message"""
        self.error = QErrorMessage(self)
        self.error.showMessage(msg)
        self.error.exec_()
        self.error = None
