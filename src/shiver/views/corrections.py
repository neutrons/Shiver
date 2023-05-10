"""PyQt widget for the correction tab"""
# pylint: disable=no-name-in-module
from qtpy.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
)
from qtpy.QtCore import Qt
from mantid.kernel import Logger

logger = Logger("Shiver")


class Corrections(QWidget):
    """Correction widget"""

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.ws_name = name

        # checkbox group
        # detailed balance
        # NOTE: if workspace has history, enable the checkbox
        self.detailed_balance = QCheckBox("Detailed balance")
        self.detailed_balance.setToolTip(
            "Convert data to dynamic susceptibility (chi'')." "\nSee ApplyDetailedBalanceMD algorithm."
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

        # debye waller correction (disabled for now)
        self.debye_waller_correction = QCheckBox("Debye-Waller correction")
        self.debye_waller_correction.setEnabled(False)

        # magentic structure factor (disabled for now)
        self.magentic_structure_factor = QCheckBox("Magentic structure factor")
        self.magentic_structure_factor.setEnabled(False)

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
        correction_layout.addWidget(self.debye_waller_correction)
        correction_layout.addWidget(self.magentic_structure_factor)
        correction_layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
        correction_layout.addLayout(action_layout)

        # set the layout
        self.setLayout(correction_layout)
