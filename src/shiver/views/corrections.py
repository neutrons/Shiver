"""PyQt widget for the correction tab"""

# pylint: disable=no-name-in-module
# pylint: disable=invalid-name
from qtpy.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
)
from qtpy.QtCore import Qt
from qtpy.QtGui import QDoubleValidator
from .invalid_styles import INVALID_QLINEEDIT, INVALID_QCHECKBOX


class Corrections(QWidget):
    """Correction widget"""

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.ws_name = name

        # invalid fields
        self.invalid_fields = []

        # checkbox group
        # detailed balance
        # NOTE: if workspace has history, enable the checkbox
        self.detailed_balance = QCheckBox("Detailed balance")
        self.detailed_balance.setToolTip(
            "Convert data to dynamic susceptibility (chi'').\nSee ApplyDetailedBalanceMD algorithm."
        )
        self.temperature = QLineEdit()
        self.temperature.setToolTip("Temperature (K) or sample log name.")
        self.temperature.setPlaceholderText("Please provide temperature (K) or a sample log name, e.g. SampleTemp")
        detailed_balance_layout = QHBoxLayout()
        detailed_balance_layout.addWidget(self.detailed_balance)
        detailed_balance_layout.addWidget(self.temperature)

        # hyspec polarizer transmission
        # NOTE: if workspace has history, enable the checkbox
        self.hyspec_polarizer_transmission = QCheckBox("Hyspec polarizer transmission")
        self.hyspec_polarizer_transmission.setToolTip(
            "Correct for the scattered beam transmission through the HYSPEC"
            "polarizer.\n See DgsScatteredTransmissionCorrectionMD algorithm."
        )

        self.u2_validator = QDoubleValidator(bottom=0, parent=self)
        self.u2_validator.setNotation(QDoubleValidator.StandardNotation)

        # debye waller correction (disabled for now)
        self.debye_waller_correction = QCheckBox("Debye-Waller Correction")
        self.debye_waller_correction.setToolTip(
            "Apply Debye-Waller correction to the data.\nSee Debye-WallerFactorCorrectionMD algorithm."
        )
        self.u2 = QLineEdit()
        self.u2.setToolTip("Mean squared displacement.")
        self.u2.setPlaceholderText("Please provide mean squared displacement value u^2")
        self.u2.setValidator(self.u2_validator)
        debye_waller_layout = QHBoxLayout()
        debye_waller_layout.addWidget(self.debye_waller_correction)
        debye_waller_layout.addWidget(self.u2)

        # magentic structure factor (disabled for now)
        self.magnetic_structure_factor = QCheckBox("Magnetic structure factor")
        self.magnetic_structure_factor.setToolTip(
            "Correct for the magnetic structure factor.\nSee MagneticFormFactorCorrectionMD algorithm."
        )
        self.ion_name = QComboBox()
        magnetic_structure_layout = QHBoxLayout()
        magnetic_structure_layout.addWidget(self.magnetic_structure_factor)
        magnetic_structure_layout.addWidget(self.ion_name)
        magnetic_structure_layout.addStretch()

        # action group
        # add a apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.setToolTip("Apply the corrections.")
        self.apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.apply_button.setFixedWidth(100)
        self.apply_button.setShortcut("Return")
        self.apply_button.setObjectName("apply_button")
        # add a cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel the corrections.")
        self.cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.setShortcut("Esc")
        self.cancel_button.setObjectName("cancel_button")
        # config action group layout
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.apply_button)
        action_layout.addWidget(self.cancel_button)
        action_layout.setAlignment(Qt.AlignLeft)

        # config the layout
        correction_layout = QVBoxLayout()
        correction_layout.addLayout(detailed_balance_layout)
        correction_layout.addWidget(self.hyspec_polarizer_transmission)
        correction_layout.addLayout(debye_waller_layout)
        correction_layout.addLayout(magnetic_structure_layout)
        correction_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        correction_layout.addLayout(action_layout)

        # set the layout
        self.setLayout(correction_layout)

        # validation
        self.detailed_balance.toggled.connect(self.balance_temp_validate)
        self.temperature.textChanged.connect(self.balance_temp_validate)
        self.debye_waller_correction.toggled.connect(self.debye_waller_u2_validate)
        self.u2.textChanged.connect(self.debye_waller_u2_validate)

    def set_field_invalid_state(self, item, invalid_style):
        """include the item in the field_error list and disable the corresponding button"""
        if item not in self.invalid_fields:
            self.invalid_fields.append(item)
        item.setStyleSheet(invalid_style)
        self.apply_button.setEnabled(False)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and enable the corresponding button"""
        if item in self.invalid_fields:
            self.invalid_fields.remove(item)
        if len(self.invalid_fields) == 0:
            self.apply_button.setEnabled(True)
        item.setStyleSheet("")

    def balance_temp_validate(self):
        """Validate balance: validate balance and temperature combination"""
        self.set_field_valid_state(self.detailed_balance)
        self.set_field_valid_state(self.temperature)
        if (self.detailed_balance.isChecked() and len(self.temperature.text()) == 0) or (
            not self.detailed_balance.isChecked() and len(self.temperature.text()) > 0
        ):
            self.set_field_invalid_state(self.detailed_balance, INVALID_QCHECKBOX)
            self.set_field_invalid_state(self.temperature, INVALID_QLINEEDIT)

    def debye_waller_u2_validate(self):
        """Validate u2: validate Debye Waller Correction and u^2 combination"""
        self.set_field_valid_state(self.debye_waller_correction)
        self.set_field_valid_state(self.u2)
        if (self.debye_waller_correction.isChecked() and len(self.u2.text()) == 0) or (  # pylint: disable = R0916
            not self.debye_waller_correction.isChecked() and len(self.u2.text()) > 0
        ):
            self.set_field_invalid_state(self.debye_waller_correction, INVALID_QCHECKBOX)
            self.set_field_invalid_state(self.u2, INVALID_QLINEEDIT)
