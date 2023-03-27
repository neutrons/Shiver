"""PyQt widget for the correction tab"""
import logging
import webbrowser
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


class Corrections(QWidget):
    """Correction widget"""

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.ws_name = name

        # checkbox group
        # detailed balance
        self.detailed_balance = QCheckBox("Detailed balance")
        self.temperature = QLineEdit()
        self.temperature.setPlaceholderText("Please provide temperature (K) or sample log name")
        detailed_balance_layout = QHBoxLayout()
        detailed_balance_layout.addWidget(self.detailed_balance)
        detailed_balance_layout.addWidget(self.temperature)
        # hyspec polarizer transmission
        self.hyspec_polarizer_transmission = QCheckBox("Hyspec polarizer transmission")
        # debye waller correction (disabled for now)
        self.debye_waller_correction = QCheckBox("Debye-Waller correction")
        self.debye_waller_correction.setEnabled(False)
        # magentic structure factor (disabled for now)
        self.magentic_structure_factor = QCheckBox("Magentic structure factor")
        self.magentic_structure_factor.setEnabled(False)

        # action group
        # add a help button at the lower left corner
        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.help)
        self.help_button.setToolTip("Open the help page")
        self.help_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.help_button.setFixedWidth(100)
        self.help_button.setShortcut("F1")
        # add a apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply)
        self.apply_button.setToolTip("Apply the corrections")
        self.apply_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.apply_button.setFixedWidth(100)
        self.apply_button.setShortcut("Return")
        # add a cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setToolTip("Cancel the corrections")
        self.cancel_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.setShortcut("Esc")
        # config action group layout
        action_layout = QHBoxLayout()
        action_layout.addWidget(self.help_button)
        action_layout.addSpacerItem(QSpacerItem(150, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))
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

    def help(self):
        """Opens the help page"""
        webbrowser.open("https://docs.mantidproject.org")

    def apply(self):
        """Apply the corrections"""
        logging.info("apply corrections")

    def cancel(self):
        """Cancel the corrections"""
        logging.info("cancel corrections")
        self.deleteLater()
