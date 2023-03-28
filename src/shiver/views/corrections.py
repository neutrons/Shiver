"""PyQt widget for the correction tab"""
# pylint: disable=no-name-in-module
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
from mantid.simpleapi import (
    mtd,
    ApplyDetailedBalanceMD,
    DgsScatteredTransmissionCorrectionMD,
)


class Corrections(QWidget):
    """Correction widget"""

    def __init__(self, parent=None, name=None):
        super().__init__(parent)
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
        logging.info("apply corrections")
        output_ws = f"{self.ws_name}_correction"
        # detailed balance
        if self.detailed_balance.isChecked():
            try:
                ApplyDetailedBalanceMD(
                    InputWorkspace=self.ws_name,
                    Temperature=self.temperature.text(),
                    OutputWorkspace=output_ws,
                )
            except RuntimeError as err:
                logging.error(err)
                # NOTE: early return here to give user a chance to fix the temperature
                #      before the next correction.
                return err
        # hyspec polarizer transmission
        # NOTE: see for more details
        # https://docs.mantidproject.org/nightly/algorithms/DgsScatteredTransmissionCorrectionMD-v1.html
        if self.hyspec_polarizer_transmission.isChecked():
            input_ws = output_ws if self.detailed_balance.isChecked() else self.ws_name
            DgsScatteredTransmissionCorrectionMD(
                InputWorkspace=input_ws,
                ExponentFactor=1.0 / 11.0,  # NOTE: this is a magic number
                OutputWorkspace=output_ws,
            )
        # debye waller correction
        # magentic structure factor
        self.workspace_tables.switch_to_main()
        self.deleteLater()
        return None

    def cancel(self):
        """Cancel the corrections"""
        logging.info("cancel corrections")
        self.workspace_tables.switch_to_main()
        self.deleteLater()
