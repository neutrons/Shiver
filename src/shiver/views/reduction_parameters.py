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

from shiver.views.polarized_options import PolarizedView
from shiver.presenters.polarized import PolarizedPresenter
from shiver.models.polarized import PolarizedModel

from .advanced_options import AdvancedDialog
from .invalid_styles import INVALID_QLINEEDIT


class ReductionParameters(QGroupBox):
    """Generate reduction parameter widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.advanced_apply_callback = None
        self.setTitle("Reduction Parameters")
        layout = QGridLayout()
        self.setLayout(layout)

        # empty parameters
        self.workspace_name = None
        # validators
        self.double_validator = QtGui.QDoubleValidator(self)
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.positive_double_validator = QtGui.QDoubleValidator(self)
        self.positive_double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        self.positive_double_validator.setBottom(0.0)

        # mask
        layout.addWidget(QLabel("Mask"), 0, 0)

        self.mask_path = QLineEdit()
        self.mask_path.setToolTip("Name of the NeXus file containing the mask.")
        layout.addWidget(self.mask_path, 0, 1, 1, 2)

        self.mask_browse = QPushButton("Browse")
        self.mask_browse.setToolTip("Browse to the NeXus file containing the mask.")
        self.mask_browse.clicked.connect(self._mask_browse)
        layout.addWidget(self.mask_browse, 0, 3)

        # normalization
        layout.addWidget(QLabel("Normalization"), 1, 0)

        self.norm_path = QLineEdit()
        self.norm_path.setToolTip("Name of the NeXus file containing the incoherent scattering for normalization.")
        layout.addWidget(self.norm_path, 1, 1, 1, 2)

        self.norm_browse = QPushButton("Browse")
        self.norm_browse.setToolTip("Browse to the NeXus file containing the incoherent scattering for normalization.")
        self.norm_browse.clicked.connect(self._norm_browse)
        layout.addWidget(self.norm_browse, 1, 3)

        self.input_widget = QWidget()
        input_layout = QHBoxLayout()

        # Ei
        ei_label = QLabel("Ei")
        ei_label.setToolTip("Incident energy (will override the value in the file).")
        input_layout.addWidget(ei_label)

        self.ei_input = QLineEdit()
        self.ei_input.setToolTip("Incident energy (will override the value in the file).")
        self.ei_input.setFixedWidth(60)
        input_layout.addWidget(self.ei_input)

        # T0
        t0_label = QLabel("T0")
        t0_label.setToolTip("Time offset (will override the value calculated from the file).")
        t0_label.setStyleSheet("margin-left:20px;")
        input_layout.addWidget(t0_label)

        self.t0_input = QLineEdit()
        self.t0_input.setToolTip("Time offset (will override the value calculated from the file).")
        self.t0_input.setFixedWidth(60)
        input_layout.addWidget(self.t0_input)

        input_layout.setContentsMargins(0, 10, 0, 10)
        self.input_widget.setLayout(input_layout)
        layout.addWidget(self.input_widget, 3, 0, 1, 4)

        self.sample_btn = QPushButton("Sample Options")
        self.sample_btn.setToolTip("Set the lattice parameters and orientation (UB matrix).")
        self.sample_btn.clicked.connect(self.set_sample_btn)

        layout.addWidget(self.sample_btn, 4, 0)

        self.adv_btn = QPushButton("Advanced Options")
        self.adv_btn.setToolTip("Advanced options for data processing.")
        self.adv_btn.clicked.connect(self.set_adv_btn)
        layout.addWidget(self.adv_btn, 4, 3)

        self.pol_btn = QPushButton("Polarization Options")
        self.pol_btn.setToolTip("Advanced options for polarized data processing.")
        self.pol_btn.clicked.connect(self.set_pol_btn)
        layout.addWidget(self.pol_btn, 5, 0)

        self.polarization_label = QLabel("Unpolarized Data")
        self.polarization_label.setToolTip("Type of polarization.")
        layout.addWidget(self.polarization_label, 5, 1)

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

    def connect_advanced_apply_callback(self, callback):
        """connect the callback for apply btn"""
        self.advanced_apply_callback = callback

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
            self,
            "Select one or more files to open",
            filter=QString("Processed Nexus file (*.nxs);;All Files (*)"),
            options=QFileDialog.DontUseNativeDialog,
        )
        if not filename:
            return
        self.mask_path.setText(filename)

    def _norm_browse(self):
        """Open the file dialog and update the path"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select one or more files to open",
            filter=QString("Processed Nexus file (*.nxs);;All Files (*)"),
            options=QFileDialog.DontUseNativeDialog,
        )
        if not filename:
            return
        self.norm_path.setText(filename)

    def set_sample_btn(self):
        """Open the dialog to set sample parameters"""
        sample = SampleView(self)
        sample_model = SampleModel(self.workspace_name)
        SamplePresenter(sample, sample_model)

        # open the dialog
        dialog = sample.start_dialog()
        self.active_dialog = dialog
        # populate the dialog
        if len(self.dict_sample) > 0:
            # from dictionary, if a non-empty dictionary exists
            dialog.populate_sample_parameters_from_dict(self.dict_sample)
        else:
            # from workspace
            dialog.populate_sample_parameters()
        dialog.exec_()
        self.active_dialog = None

    def set_adv_btn(self):
        """Open the dialog to set advanced options"""
        dialog = AdvancedDialog(self)
        self.active_dialog = dialog
        # populate the dialog
        if self.dict_advanced:
            dialog.populate_advanced_options_from_dict(self.dict_advanced)
        dialog.exec_()
        self.advanced_apply_callback(self.dict_advanced)
        self.active_dialog = None

    def set_pol_btn(self):
        """Open the dialog to set polarization options"""

        polarized_view = PolarizedView(self)
        polarized_model = PolarizedModel(self.workspace_name)
        PolarizedPresenter(polarized_view, polarized_model)

        dialog = polarized_view.start_dialog()
        self.active_dialog = dialog

        # populate the dialog
        if len(self.dict_polarized) > 0:
            # from dictionary, if a non-empty dictionary exists
            dialog.populate_pol_options_from_dict(self.dict_polarized)
        else:
            # from workspace
            dialog.populate_polarized_options()
        dialog.exec_()
        self.update_polarization_label()
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
        if not params:
            return

        # sanitize the dictionary
        self.ei_input.setText(str(params.get("Ei", "")))
        self.t0_input.setText(str(params.get("T0", "")))
        self.mask_path.setText(str(params.get("MaskingDataFile", "")))
        self.norm_path.setText(str(params.get("NormalizationDataFile", "")))

        if "AdvancedOptions" in params.keys():
            params["AdvancedOptions"]["AdditionalDimensions"] = params["AdvancedOptions"].get(
                "AdditionalDimensions", ""
            )

        self.dict_advanced = params.get("AdvancedOptions", {})
        self.dict_sample = params.get("SampleParameters", {})
        self.dict_polarized = params.get("PolarizedOptions", {})

        # get workspace name
        self.workspace_name = params.get("mde_name")
        # update polarization label
        self.update_polarization_label()

    def update_polarization_label(self):
        """It updates the label with the plarization state and direction"""
        display_pol_state = self.dict_polarized.get("PolarizationState")
        if display_pol_state in ["SF", "NSF"]:
            display_pol_state += "_" + self.dict_polarized.get("PolarizationDirection")
        else:
            display_pol_state = "Unpolarized Data"
        self.polarization_label.setText(display_pol_state)
