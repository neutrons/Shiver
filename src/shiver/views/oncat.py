"""PyQt widget for the OnCat widget in General tab."""
from qtpy.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QComboBox,
)


class Oncat(QGroupBox):
    """ONCat widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Oncat options")

        # layout for options
        self.oncat_options_layout = QGridLayout()
        # dropdown list for instrument
        self.instrument_label = QLabel("Instrument")
        self.instrument = QComboBox()
        self.instrument_items = ["HYSPEC"]
        self.instrument.addItems(self.instrument_items)
        self.oncat_options_layout.addWidget(self.instrument_label, 0, 0)
        self.oncat_options_layout.addWidget(self.instrument, 0, 1)
        # dropdown list for IPTS
        self.ipts_label = QLabel("IPTS")
        self.ipts = QComboBox()
        self.ipts_items = ["IPTS-12345"]
        self.ipts.addItems(self.ipts_items)
        self.oncat_options_layout.addWidget(self.ipts_label, 1, 0)
        self.oncat_options_layout.addWidget(self.ipts, 1, 1)
        # dropdown list for dataset
        self.dataset_label = QLabel("Select dataset")
        self.dataset = QComboBox()
        self.dataset_items = ["temperature_2"]
        self.dataset.addItems(self.dataset_items)
        self.oncat_options_layout.addWidget(self.dataset_label, 2, 0)
        self.oncat_options_layout.addWidget(self.dataset, 2, 1)
        # dropdown list for angle integration target
        self.angle_target_label = QLabel("Angle integra")
        self.angle_target = QComboBox()
        self.angle_target_items = ["None", "temperature_1", "temperature_2"]
        self.angle_target.addItems(self.angle_target_items)
        self.oncat_options_layout.addWidget(self.angle_target_label, 3, 0)
        self.oncat_options_layout.addWidget(self.angle_target, 3, 1)

        # help button
        self.help_button = QPushButton("Help")
        self.help_button.setFixedWidth(100)
        self.help_button.setToolTip("Help")
        self.help_button.setShortcut("F1")
        self.oncat_options_layout.addWidget(self.help_button, 4, 0)

        # connect to OnCat button
        self.oncat_button = QPushButton("&Connect to OnCat")
        self.oncat_button.setFixedWidth(300)
        self.oncat_button.setToolTip("Connect to OnCat (requires login credentials)")
        self.oncat_options_layout.addWidget(self.oncat_button, 4, 1)

        # set layout
        self.setLayout(self.oncat_options_layout)

        # connect signals and slots
        self.help_button.clicked.connect(self.help)
        self.oncat_button.clicked.connect(self.connect_to_oncat)

        # error message callback
        self.error_message = None

    def connect_to_oncat(self):
        """Connect to OnCat"""
        print("Connect to OnCat")

    def help(self):
        """Help"""
        print("Help")

    def connect_error_callback(self, callback):
        """Connect error message callback"""
        self.error_message = callback

    def as_dict(self) -> dict:
        """Return widget state as dictionary"""
        return {
            "instrument": self.instrument.currentText(),
            "ipts": self.ipts.currentText(),
            "dataset": self.dataset.currentText(),
            "angle_target": self.angle_target.currentText(),
        }
    
    def populate_from_dict(self, state: dict):
        """Populate widget from dictionary"""
        self.instrument.setCurrentText(state["instrument"])
        self.ipts.setCurrentText(state["ipts"])
        self.dataset.setCurrentText(state["dataset"])
        self.angle_target.setCurrentText(state["angle_target"])
