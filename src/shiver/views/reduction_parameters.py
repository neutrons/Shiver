"""PyQt widget for the Reduction Parameters section"""
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
)

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")

from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel

from .advanced_options import AdvancedDialog
from .polarized_options import PolarizedDialog
from .histogram_parameters import INVALID_QLINEEDIT


class ReductionParameters(QGroupBox):
    """Generate reduction parameter widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Reduction Parameters")
        layout = QGridLayout()
        self.setLayout(layout)

        # validators
        self.double_validator = QtGui.QDoubleValidator(self)
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.positive_double_validator = QtGui.QDoubleValidator(self)
        self.positive_double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.positive_double_validator.setBottom(0.0)

        # mask
        layout.addWidget(QLabel("Mask"), 0, 0)

        self.mask_path = QLineEdit()
        layout.addWidget(self.mask_path, 0, 1, 1, 2)

        self.mask_browse = QPushButton("Browse")
        self.mask_browse.clicked.connect(self._mask_browse)
        layout.addWidget(self.mask_browse, 0, 3)

        # normalization
        layout.addWidget(QLabel("Normalization"), 1, 0)

        self.norm_path = QLineEdit()
        layout.addWidget(self.norm_path, 1, 1, 1, 2)

        self.norm_browse = QPushButton("Browse")
        self.norm_browse.clicked.connect(self._norm_browse)
        layout.addWidget(self.norm_browse, 1, 3)

        self.input_widget = QWidget()
        input_layout = QHBoxLayout()

        # Ei
        ei_label = QLabel("Ei")
        input_layout.addWidget(ei_label)

        self.ei_input = QLineEdit()
        self.ei_input.setFixedWidth(60)
        input_layout.addWidget(self.ei_input)

        # T0
        t0_label = QLabel("T0")
        t0_label.setStyleSheet("margin-left:20px;")
        input_layout.addWidget(t0_label)

        self.t0_input = QLineEdit()
        self.t0_input.setFixedWidth(60)
        input_layout.addWidget(self.t0_input)

        input_layout.setContentsMargins(0, 10, 0, 10)
        self.input_widget.setLayout(input_layout)
        layout.addWidget(self.input_widget, 2, 0, 1, 4)

        self.sample_btn = QPushButton("Sample Options")
        self.sample_btn.clicked.connect(self.set_sample_btn)

        layout.addWidget(self.sample_btn, 3, 0)

        self.adv_btn = QPushButton("Advanced Options")
        self.adv_btn.clicked.connect(self.set_adv_btn)
        layout.addWidget(self.adv_btn, 3, 3)

        self.pol_btn = QPushButton("Polarization Options")
        self.pol_btn.clicked.connect(self.set_pol_btn)
        layout.addWidget(self.pol_btn, 4, 0)

        self.polarization_label = QLabel("Unpolarized Data")
        layout.addWidget(self.polarization_label, 4, 1)

        # set validators
        self.ei_input.setValidator(self.positive_double_validator)
        self.t0_input.setValidator(self.double_validator)
        self.t0_input.textEdited.connect(self.validate_t0)
        # initialize dictionaries
        self.dict_advanced = {}
        self.dict_polarized = {}
        self.dict_sample = {}

        # keep track of the active dialog
        self.active_dialog = None

    def set_field_invalid_state(self, item):
        """if parent exists then call the corresponding function"""
        if self.parent():
            self.parent().set_field_invalid_state(item)
        item.setStyleSheet(INVALID_QLINEEDIT)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and its invalid style, if it was previously invalid
        and enable the corresponding button"""
        if self.parent():
            self.parent().set_field_valid_state(item)
        item.setStyleSheet("")

    def validate_t0(self):
        """validate t0 input"""
        self.set_field_valid_state(self.t0_input)
        if len(self.t0_input.text()) > 0:
            try:
                float(self.t0_input.text())
            except ValueError:
                self.set_field_invalid_state(self.t0_input)

    def _mask_browse(self):
        """Open the file dialog and update the path"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", filter=QString("Processed Nexus file (*.nxs);;All Files (*)")
        )
        if not filename:
            return
        self.mask_path.setText(filename)

    def _norm_browse(self):
        """Open the file dialog and update the path"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", filter=QString("Processed Nexus file (*.nxs);;All Files (*)")
        )
        if not filename:
            return
        self.norm_path.setText(filename)

    def set_sample_btn(self):
        """Open the dialog to set sample parameters"""
        sample = SampleView()
        sample_model = SampleModel()
        SamplePresenter(sample, sample_model)

        # open the dialog
        dialog = sample.start_dialog()
        self.active_dialog = dialog
        # populate the dialog
        if self.dict_sample:
            dialog.populate_sample_parameters_from_dict(self.dict_sample)
        else:
            dialog.populate_sample_parameters()
        dialog.exec_()
        self.dict_sample = sample.get_sample_parameters_dict()
        self.active_dialog = None

    def set_adv_btn(self):
        """Open the dialog to set advanced options"""
        dialog = AdvancedDialog(self)
        self.active_dialog = dialog
        # populate the dialog
        if self.dict_advanced:
            dialog.populate_advanced_options_from_dict(self.dict_advanced)
        dialog.exec_()
        self.active_dialog = None

    def set_pol_btn(self):
        """Open the dialog to set polarization options"""
        dialog = PolarizedDialog(self)
        self.active_dialog = dialog
        # populate the dialog
        if self.dict_polarized:
            dialog.populate_pol_options_from_dict(self.dict_polarized)
        dialog.exec_()
        if self.dict_polarized and self.dict_polarized["PolarizationState"] is not None:
            self.polarization_label.setText(self.dict_polarized["PolarizationState"])
        else:
            self.polarization_label.setText("Unpolarized Data")
        self.active_dialog = None

    def get_reduction_params_dict(self):
        """Return all reduction parameters as a dictionary"""
        data = {
            "MaskingDataFile": None,
            "NormalizationDataFile": None,
            "Ei": None,
            "T0": None,
            "AdvancedOptions": {},
            "SampleParameters": {},
            "PolarizedOptions": {},
        }
        if self.mask_path.text():
            data["MaskingDataFile"] = self.mask_path.text()

        if self.norm_path.text():
            data["NormalizationDataFile"] = self.norm_path.text()

        if self.ei_input.text():
            data["Ei"] = self.ei_input.text()

        if self.t0_input.text():
            data["T0"] = self.t0_input.text()

        data["AdvancedOptions"] = self.dict_advanced
        data["SampleParameters"] = self.dict_sample
        data["PolarizedOptions"] = self.dict_polarized
        return data

    def populate_red_params_from_dict(self, params):
        """Populate all fields and inner dialogs from dictionary"""
        expected_keys = [
            "MaskingDataFile",
            "NormalizationDataFile",
            "Ei",
            "T0",
            "AdvancedOptions",
            "SampleParameters",
            "PolarizedOptions",
        ]

        for param in expected_keys:
            if param not in params.keys():
                self.show_error_message(f"Invalid dinctionary format. Missing: {param}")
                return

        self.dict_advanced = params["AdvancedOptions"]
        self.dict_sample = params["SampleParameters"]
        self.dict_polarized = params["PolarizedOptions"]

        if params["Ei"] is not None:
            self.ei_input.setText(str(params["Ei"]))
        if params["T0"] is not None:
            self.t0_input.setText(str(params["T0"]))
        if params["MaskingDataFile"] is not None:
            self.mask_path.setText(params["MaskingDataFile"])
        if params["NormalizationDataFile"] is not None:
            self.norm_path.setText(params["NormalizationDataFile"])
