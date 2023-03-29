"""PyQt widget for the correction tab"""
# pylint: disable=no-name-in-module
import time
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
from mantid.kernel import Logger
from mantid.simpleapi import mtd
from shiver.models.corrections import CorrectionsModel

logger = Logger("Shiver")


class Corrections(QWidget):
    """Correction widget"""

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
        self.model = CorrectionsModel()
        self.ws_name = name

        # retrieve the algorithm history
        algorithm_histories_name = [
            hist_item.name() for hist_item in mtd[self.ws_name].getHistory().getAlgorithmHistories()
        ]

        # NOTE: keep a pointer of the parent(WorkspaceTables) to
        #       allow switching back to main view when this tab
        #       is closed.
        self.workspace_tables = parent

        # checkbox group
        # detailed balance
        # NOTE: if workspace has history, enable the checkbox
        self.detailed_balance = QCheckBox("Detailed balance")
        self.temperature = QLineEdit()
        self.temperature.setPlaceholderText("Please provide temperature (K) or a sample log name, e.g. SampleTemp")
        detailed_balance_layout = QHBoxLayout()
        detailed_balance_layout.addWidget(self.detailed_balance)
        detailed_balance_layout.addWidget(self.temperature)
        if "ApplyDetailedBalanceMD" in algorithm_histories_name:
            self.detailed_balance.setChecked(True)
            # retrieve the temperature from the history
            for history_item in mtd[self.ws_name].getHistory().getAlgorithmHistories():
                if history_item.name() == "ApplyDetailedBalanceMD":
                    for prop_item in history_item.getProperties():
                        if prop_item.name() == "Temperature":
                            self.temperature.setText(prop_item.value())
        # hyspec polarizer transmission
        # NOTE: if workspace has history, enable the checkbox
        self.hyspec_polarizer_transmission = QCheckBox("Hyspec polarizer transmission")
        if "DgsScatteredTransmissionCorrectionMD" in algorithm_histories_name:
            self.hyspec_polarizer_transmission.setChecked(True)
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
        webbrowser.open("https://neutrons.github.io/Shiver/")

    def apply(self):
        """Apply the corrections"""
        # NOTE: add return value to assist unit testing
        logger.information("apply corrections")
        output_ws = f"{self.ws_name}_correction"
        # detailed balance
        if self.detailed_balance.isChecked():
            self.model.apply_detailed_balance(
                self.ws_name,
                self.temperature.text(),
                output_ws,
            )
        # hyspec polarizer transmission
        if self.hyspec_polarizer_transmission.isChecked():
            input_ws = output_ws if self.detailed_balance.isChecked() else self.ws_name
            # NOTE: because previous alg is executed asynchronously, we need to wait
            #       until the previous alg is finished before executing the next one.
            count = 0
            while not mtd.doesExist(input_ws):
                time.sleep(1)
                count += 1
                if count > 20:
                    logger.error("Failed to apply detailed balance correction, skipping.")
                    input_ws = self.ws_name
                    break
            self.model.apply_scattered_transmission_correction(
                input_ws,
                output_ws,
            )
        # debye waller correction
        # magentic structure factor
        self.workspace_tables.switch_to_main()
        self.deleteLater()

    def cancel(self):
        """Cancel the corrections"""
        logger.information("cancel corrections")
        self.workspace_tables.switch_to_main()
        self.deleteLater()
