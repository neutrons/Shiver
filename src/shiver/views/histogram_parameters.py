"""PyQt QGroupBox for the histogram parameters"""
import numpy
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QGridLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QCheckBox,
    QDoubleSpinBox,
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


def translation(number, character):
    """Used in projection"""
    if number == 0:
        return "0"
    if number == 1:
        return character
    if number == -1:
        return "-" + character
    return str(number) + character


INVALID_QLINEEDIT = """
QLineEdit {
border-color: red;
border-style: outset;
border-width: 2px;
border-radius: 4px;
padding-left: -1px;
padding-right: -1px;
padding-top: 1px;
padding-bottom: 1px;
}
"""
INVALID_QTABLEWIDGET = """
QTableWidget {
border-color: red;
border-style: outset;
border-width: 2px;
border-radius: 4px;
padding-left: -1px;
padding-right: -1px;
padding-top: 1px;
padding-bottom: 1px;
}
"""
INVALID_QLISTWIDGET = """
QListWidget {
border-color: red;
border-style: outset;
border-width: 2px;
border-radius: 4px;
padding-left: -1px;
padding-right: -1px;
padding-top: 1px;
padding-bottom: 1px;
}
"""


# validator for projections 3-digit array format: [1,0,0] from mantid --> DimensionSelectorWidget.py
class V3DValidator(QtGui.QValidator):
    """Validates the projection values"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def validate(self, teststring, pos):
        """Validates the projections 3-digit array format: [1,0,0]"""
        parts = str(teststring).split(",")
        # invalid number of digits
        if len(parts) > 3:
            return return_valid(QtGui.QValidator.Invalid, teststring, pos)
        if len(parts) == 3:
            try:
                # valid case with 3 float numbers
                float(parts[0])
                float(parts[1])
                float(parts[2])
                return return_valid(QtGui.QValidator.Acceptable, teststring, pos)
            except ValueError:
                try:
                    # invalid case in progress of writing the array
                    float(parts[0] + "1")
                    float(parts[1] + "1")
                    float(parts[2] + "1")
                    return return_valid(QtGui.QValidator.Intermediate, teststring, pos)
                except ValueError:
                    return return_valid(QtGui.QValidator.Invalid, teststring, pos)
        return return_valid(QtGui.QValidator.Intermediate, teststring, pos)


class HistogramParameter(QGroupBox):
    """Histogram parameters widget"""

    plot_num = 1
    name_base = "Histogram"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram parameters")

        layout = QVBoxLayout()
        self.projections_valid_state = True
        self.projections = QWidget()
        playout = QFormLayout()
        self.v3d_validator = V3DValidator(self)
        self.basis = ["1,0,0", "0,1,0", "0,0,1"]

        self.name = QLineEdit(f"{self.name_base} {self.plot_num}")
        # checkbox to allow manual edit of the name field, disable the
        # name field if the checkbox is not checked
        self.name_checkbox = QCheckBox("Manual")
        self.name_checkbox.setChecked(True)
        self.name_checkbox.toggled.connect(self.name.setEnabled)
        plot_name_layout = QHBoxLayout()
        plot_name_layout.addWidget(self.name)
        plot_name_layout.addWidget(self.name_checkbox)
        playout.addRow("Name", plot_name_layout)

        self.projection_u = QLineEdit(self.basis[0])
        self.projection_u.setValidator(self.v3d_validator)
        playout.addRow("Projection u", self.projection_u)

        self.projection_v = QLineEdit(self.basis[1])
        self.projection_v.setValidator(self.v3d_validator)
        playout.addRow("Projection v", self.projection_v)

        self.projection_w = QLineEdit(self.basis[2])
        self.projection_w.setValidator(self.v3d_validator)
        playout.addRow("Projection w", self.projection_w)
        self.projections.setLayout(playout)

        layout.addWidget(self.projections)

        self.dimensions_count = QWidget()
        dclayout = QHBoxLayout()
        self.btn_dimensions = ["1D cut", "2D slice", "3D volume", "4D volume"]
        self.cut_1d = QRadioButton(self.btn_dimensions[0])

        dclayout.addWidget(self.cut_1d)
        self.cut_2d = QRadioButton(self.btn_dimensions[1])

        dclayout.addWidget(self.cut_2d)
        self.cut_3d = QRadioButton(self.btn_dimensions[2])

        dclayout.addWidget(self.cut_3d)

        self.cut_4d = QRadioButton(self.btn_dimensions[3])
        dclayout.addWidget(self.cut_4d)

        self.dimensions = Dimensions(self)
        self.dimensions_count.setLayout(dclayout)
        layout.addWidget(self.dimensions_count)
        layout.addWidget(self.dimensions)

        symmetry = QWidget()

        slayout = QFormLayout()
        self.symmetry_operations = QLineEdit()
        slayout.addRow("Symmetry operations", self.symmetry_operations)

        # smoothing can't exceed 1_000 and can't be negative
        self.smoothing = QDoubleSpinBox()
        self.smoothing.setRange(0, 1_000)
        slayout.addRow("Smoothing", self.smoothing)
        symmetry.setLayout(slayout)

        layout.addWidget(symmetry)

        layout.addStretch()

        self.histogram_btn = QPushButton("Histogram")
        layout.addWidget(self.histogram_btn)

        self.setLayout(layout)

        # on any projection change check the all are non-colinear
        self.projection_u.textEdited.connect(self.projection_updated)
        self.projection_v.textEdited.connect(self.projection_updated)
        self.projection_w.textEdited.connect(self.projection_updated)

        # validate number of steps based on number of dimensions
        self.cut_1d.toggled.connect(lambda: self.set_dimension(self.cut_1d))
        self.cut_2d.toggled.connect(lambda: self.set_dimension(self.cut_2d))
        self.cut_3d.toggled.connect(lambda: self.set_dimension(self.cut_3d))
        self.cut_4d.toggled.connect(lambda: self.set_dimension(self.cut_4d))

        # submit button
        self.histogram_callback = None

    def initialize_default(self):
        """initialize default values"""
        self.cut_1d.setChecked(True)

    def set_field_invalid_state(self, item):
        """if parent exists then call the corresponding function and update the color"""
        if self.parent():
            self.parent().set_field_invalid_state(item)
        item.setStyleSheet(INVALID_QLINEEDIT)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and its invalid style, if it was previously invalid
        and enable the corresponding button"""
        if self.parent():
            self.parent().set_field_valid_state(item)
        item.setStyleSheet("")

    def validate_symmentry_once(self):
        """validate symmetry once the current invalid text is updated. Note: the actual validation happens in models"""
        self.set_field_valid_state(self.symmetry_operations)
        self.symmetry_operations.disconnect()

    def update_plot_num(self):
        """Updates the plot number if name_checkbox is unchecked"""
        if not self.name_checkbox.isChecked():
            # extract the non-numeric part of the name
            name = self.name.text()
            name = name.rstrip("0123456789")
            # strip off underscores and spaces
            name = name.rstrip("_ ")
            # extract the numeric part of the name
            num = self.name.text()
            num = num[len(name) :]  # noqa: E203
            # strip off underscores and spaces
            num = num.lstrip("_ ")
            if num == "":
                # no numeric, start from 1
                num = 0
            else:
                num = int(num)

            self.plot_num = num + 1

            if self.name_base != name:
                self.name_base = name

            self.name.setText(f"{self.name_base} {self.plot_num}")

    @property
    def combo_dimx(self):
        """Returns the combo boxes for the dimensions"""
        return [
            self.dimensions.combo_dim1,
            self.dimensions.combo_dim2,
            self.dimensions.combo_dim3,
            self.dimensions.combo_dim4,
        ]

    @property
    def combo_minx(self):
        """Returns the min spin boxes for the dimensions"""
        return [
            self.dimensions.combo_min1,
            self.dimensions.combo_min2,
            self.dimensions.combo_min3,
            self.dimensions.combo_min4,
        ]

    @property
    def combo_maxx(self):
        """Returns the max spin boxes for the dimensions"""
        return [
            self.dimensions.combo_max1,
            self.dimensions.combo_max2,
            self.dimensions.combo_max3,
            self.dimensions.combo_max4,
        ]

    @property
    def combo_stepx(self):
        """Returns the step spin boxes for the dimensions"""
        return [
            self.dimensions.combo_step1,
            self.dimensions.combo_step2,
            self.dimensions.combo_step3,
            self.dimensions.combo_step4,
        ]

    @property
    def is_valid(self) -> bool:
        """Checks if the histogram parameters are valid

        Returns
        -------
            bool -- True if valid, False otherwise
        """
        # check if step values are valid
        step_valid_state = self.dimensions.steps_valid_state()

        # check if symmetry is valid
        # NOTE: the symmetry checking is done in histogram_callback and border colors/state are updapted, and the
        #       actual checking is done in histogram.model.
        #       the current design requires packing the data as a dictionary,
        #       so we pack it here.
        parameters = {}
        parameters["SymmetryOperations"] = self.symmetry_operations.text()
        self.set_field_valid_state(self.symmetry_operations)
        sym_valid_state = self.histogram_callback(parameters) if self.histogram_callback else False
        if not sym_valid_state:
            self.set_field_invalid_state(self.symmetry_operations)
            self.symmetry_operations.textEdited.connect(self.validate_symmentry_once)

        return (
            self.projections_valid_state
            and len(self.dimensions.min_max_invalid_states) == 0
            and step_valid_state
            and sym_valid_state
        )

    def projection_to_hkl(self, projection: str) -> str:
        """Converts the projection to H,K,L

        Arguments:
            projection {str} -- projection

        Returns:
            str -- H,K,L
        """
        chars = ["H", "K", "L"]
        vec = numpy.array(list(map(float, projection.split(","))))
        index_max = numpy.argmax(numpy.abs(vec))
        return "[" + ",".join([translation(x, chars[index_max]) for x in vec]) + "]"

    def gather_histogram_parameters(self) -> dict:
        """Gathers the histogram parameters

        Returns
        -------
            dict -- histogram parameters
        """
        parameters = {}

        if self.is_valid:
            # name
            parameters["Name"] = self.name.text()

            # projections
            parameters["QDimension0"] = self.projection_u.text()
            parameters["QDimension1"] = self.projection_v.text()
            parameters["QDimension2"] = self.projection_w.text()

            # build the label text for each
            ref_dict = {
                self.projection_to_hkl(self.projection_u.text()): "QDimension0",
                self.projection_to_hkl(self.projection_v.text()): "QDimension1",
                self.projection_to_hkl(self.projection_w.text()): "QDimension2",
                "DeltaE": "DeltaE",
            }

            # dimensions 1-4
            # NOTE: the index of each combo box corresponds to the projections items
            #     i.e. QDimension0, QDimension1, QDimension2, DeltaE
            for i in range(4):
                combo_dim = self.combo_dimx[i]
                combo_min = self.combo_minx[i]
                combo_max = self.combo_maxx[i]
                combo_step = self.combo_stepx[i]
                # parse each dimension combo box to update the parameter dictionary
                dim_name = ref_dict[combo_dim.currentText()]
                dim_min = combo_min.text()
                dim_max = combo_max.text()
                # if step visible, then it is a binning parameter
                if combo_step.isVisible():
                    dim_step = combo_step.text()
                else:
                    dim_step = ""
                # the binning property follows convention of MDNorm from Mantid
                # "": total integration
                # "step": total integration with step
                # "start, stop": integration between start and stop
                # "start, step, stop": integration between start and stop with step
                if dim_step != "" and dim_min == "" and dim_max == "":
                    dim_bins = f"{dim_step}"
                elif dim_min != "" and dim_max != "" and dim_step == "":
                    dim_bins = f"{dim_min},{dim_max}"
                elif dim_min != "" and dim_max != "" and dim_step != "":
                    dim_bins = f"{dim_min},{dim_step},{dim_max}"
                elif dim_min == "" and dim_max == "" and dim_step == "":
                    dim_bins = ""
                else:
                    # with proper validation on the GUI side, this should never happen
                    raise ValueError("Invalid binning parameters")

                # populate the dictionary
                parameters[f"Dimension{i}Name"] = dim_name
                parameters[f"Dimension{i}Binning"] = dim_bins

            parameters["SymmetryOperations"] = self.symmetry_operations.text()
            parameters["Smoothing"] = self.smoothing.text()

        return parameters

    def populate_histogram_parameters(self, parameters: dict):
        """Populates the histogram parameters from given dictionary."""
        # set name
        self.name.setText(parameters["OutputWorkspace"])

        # populate the projection section
        self.projection_u.setText(parameters["QDimension0"])
        self.projection_v.setText(parameters["QDimension1"])
        self.projection_w.setText(parameters["QDimension2"])

        # populate the dimensions section
        # step 0: build the search dictionary
        search_dict = {
            "QDimension0": self.projection_to_hkl(self.projection_u.text()),
            "QDimension1": self.projection_to_hkl(self.projection_v.text()),
            "QDimension2": self.projection_to_hkl(self.projection_w.text()),
            "DeltaE": "DeltaE",
        }
        dim_names = [search_dict[parameters[f"Dimension{i}Name"]] for i in range(4)]
        dim_bins = [parameters[f"Dimension{i}Binning"] for i in range(4)]
        # update all dimension combo boxes
        self.dimensions.combo_dimensions = list(dim_names)
        self.dimensions.update_combo()
        # update bin parameters
        cut_dim = 0
        for i, bin_val in enumerate(dim_bins):
            combo_min = self.combo_minx[i]
            combo_max = self.combo_maxx[i]
            combo_step = self.combo_stepx[i]
            if bin_val == "":
                # total integration
                combo_min.setText("")
                combo_max.setText("")
                combo_step.setText("")
            elif bin_val.count(",") == 0:
                # just step
                combo_min.setText("")
                combo_max.setText("")
                combo_step.setText(bin_val)
                cut_dim += 1
            elif bin_val.count(",") == 1:
                # integration between start and stop
                combo_min.setText(bin_val.split(",")[0])
                combo_max.setText(bin_val.split(",")[1])
                combo_step.setText("")
            elif bin_val.count(",") == 2:
                # integration between start and stop with step
                combo_min.setText(bin_val.split(",")[0])
                combo_max.setText(bin_val.split(",")[2])
                combo_step.setText(bin_val.split(",")[1])
                cut_dim += 1
            else:
                # this should never happen
                raise ValueError("Invalid binning parameters")
        # step 1: figure out the cut dimension based on the binning parameters
        if cut_dim == 4:
            self.cut_4d.setChecked(True)
        elif cut_dim == 3:
            self.cut_3d.setChecked(True)
        elif cut_dim == 2:
            self.cut_2d.setChecked(True)
        elif cut_dim == 1:
            self.cut_1d.setChecked(True)
        else:
            # this should never happen
            raise ValueError("Invalid cut dimension")

        # populate the symmetry section
        self.symmetry_operations.setText(parameters["SymmetryOperations"])
        self.smoothing.setValue(float(parameters["Smoothing"]))

    def connect_histogram_submit(self, callback):
        """callback for the histogram submit button"""
        self.histogram_callback = callback

    def projection_updated(self):
        """Validate the projection values"""
        sender = self.sender()
        validator = sender.validator()
        self.projections_valid_state = False
        state = validator.validate(sender.text(), 0)[0]

        if state == QtGui.QValidator.Acceptable:
            # if value is acceptable check all three projections
            self.validate_projection_values()
        else:
            # set invalid state
            self.set_field_invalid_state(sender)

    def validate_projection_values(self):
        """Validate the projection values on co-linear"""
        valid = False
        # examine whether the projections are all non-colinear
        if (
            self.projection_u.validator().validate(self.projection_u.text(), 0)[0] == QtGui.QValidator.Acceptable
            and self.projection_v.validator().validate(self.projection_v.text(), 0)[0] == QtGui.QValidator.Acceptable
            and self.projection_w.validator().validate(self.projection_w.text(), 0)[0] == QtGui.QValidator.Acceptable
        ):
            b_1 = numpy.fromstring(str(self.projection_u.text()), sep=",")
            b_2 = numpy.fromstring(str(self.projection_v.text()), sep=",")
            b_3 = numpy.fromstring(str(self.projection_w.text()), sep=",")
            if numpy.abs(numpy.inner(b_1, numpy.cross(b_2, b_3))) > 1e-5:
                valid = True
                self.projections_valid_state = True
                self.dimensions.update_dimension_names([b_1, b_2, b_3])

        if valid:
            self.set_field_valid_state(self.projection_u)
            self.set_field_valid_state(self.projection_v)
            self.set_field_valid_state(self.projection_w)
        else:
            self.set_field_invalid_state(self.projection_u)
            self.set_field_invalid_state(self.projection_v)
            self.set_field_invalid_state(self.projection_w)

    def set_dimension(self, btn):
        """Update parameter table based on mode.

        Based on the radio button step, allow the corresponding step values to be filled in;
        the rest become read-only

        Parameters
        ----------
            btn : QRadioButton
                radio button for the step
        """

        # validate all steps
        for step in self.dimensions.combo_step_boxes:
            self.set_field_valid_state(step)

        if btn.isChecked():
            # 1D case
            if "1D" in btn.text():
                self.dimensions.combo_step1.setVisible(True)
                self.dimensions.combo_step2.setVisible(False)
                self.dimensions.combo_step3.setVisible(False)
                self.dimensions.combo_step4.setVisible(False)
                self.dimensions.required_steps = [self.dimensions.combo_step1]
            # 2D case
            elif "2D" in btn.text():
                self.dimensions.combo_step1.setVisible(True)
                self.dimensions.combo_step2.setVisible(True)
                self.dimensions.combo_step3.setVisible(False)
                self.dimensions.combo_step4.setVisible(False)
                self.dimensions.required_steps = [self.dimensions.combo_step1, self.dimensions.combo_step2]
            # 3D case
            elif "3D" in btn.text():
                self.dimensions.combo_step1.setVisible(True)
                self.dimensions.combo_step2.setVisible(True)
                self.dimensions.combo_step3.setVisible(True)
                self.dimensions.combo_step4.setVisible(False)
                self.dimensions.required_steps = [
                    self.dimensions.combo_step1,
                    self.dimensions.combo_step2,
                    self.dimensions.combo_step3,
                ]
            # 4D case
            elif "4D" in btn.text():
                self.dimensions.combo_step1.setVisible(True)
                self.dimensions.combo_step2.setVisible(True)
                self.dimensions.combo_step3.setVisible(True)
                self.dimensions.combo_step4.setVisible(True)
                self.dimensions.required_steps = [
                    self.dimensions.combo_step1,
                    self.dimensions.combo_step2,
                    self.dimensions.combo_step3,
                    self.dimensions.combo_step4,
                ]
            else:
                # This should never happen
                raise ValueError("Unknown dimension")

            # finally, update the new required steps: validate/invalidate
            for step in self.dimensions.required_steps:
                if step.text() == "":
                    self.set_field_invalid_state(step)
                else:
                    self.set_field_valid_state(step)


class Dimensions(QWidget):
    """Widget for handling the selection of output dimensions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        layout.addWidget(QLabel("Dimensions"), 0, 0)
        layout.addWidget(QLabel("Minimum"), 0, 1)
        layout.addWidget(QLabel("Maximum"), 0, 2)
        layout.addWidget(QLabel("Step Size"), 0, 3)

        self.positive_double_validator = QtGui.QDoubleValidator(self)
        self.positive_double_validator.setBottom(1e-10)
        # standard decimal point-format for example: 1.2
        self.positive_double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.double_validator = QtGui.QDoubleValidator(self)
        # standard decimal point-format for example: 1.2
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        self.combo_dimensions = ["[H,0,0]", "[0,K,0]", "[0,0,L]", "DeltaE"]
        self.previous_dimension_value_indexes = [0, 1, 2, 3]

        # for the names
        # basis
        self.basis = ["1,0,0", "0,1,0", "0,0,1"]
        # default values
        # self.dimNames = ["[H,0,0]", "[0,K,0]", "[0,0,L]", "DeltaE"]

        self.dim_min = [-numpy.inf, -numpy.inf, -numpy.inf, -numpy.inf]
        self.dim_max = [numpy.inf, numpy.inf, numpy.inf, numpy.inf]
        self.dim_step = [0.05, 0.05, 0.05, 1]
        self.dim_index = [0, 1, 2, 3]

        # combo 1
        self.combo_dim1 = QComboBox()
        self.combo_dim1.addItems(self.combo_dimensions)
        self.combo_dim1.setCurrentIndex(self.previous_dimension_value_indexes[0])
        self.combo_min1 = QLineEdit()
        self.combo_min1.setValidator(self.double_validator)
        self.combo_max1 = QLineEdit()
        self.combo_max1.setValidator(self.double_validator)
        self.combo_step1 = QLineEdit()
        self.combo_step1.setValidator(self.positive_double_validator)

        layout.addWidget(self.combo_dim1, 1, 0)
        layout.addWidget(self.combo_min1, 1, 1)
        layout.addWidget(self.combo_max1, 1, 2)
        layout.addWidget(self.combo_step1, 1, 3)

        # combo 2
        self.combo_dim2 = QComboBox()
        self.combo_dim2.addItems(self.combo_dimensions)
        self.combo_dim2.setCurrentIndex(self.previous_dimension_value_indexes[1])
        self.combo_min2 = QLineEdit()
        self.combo_min2.setValidator(self.double_validator)
        self.combo_max2 = QLineEdit()
        self.combo_max2.setValidator(self.double_validator)
        self.combo_step2 = QLineEdit()
        self.combo_step2.setValidator(self.positive_double_validator)

        layout.addWidget(self.combo_dim2, 2, 0)
        layout.addWidget(self.combo_min2, 2, 1)
        layout.addWidget(self.combo_max2, 2, 2)
        layout.addWidget(self.combo_step2, 2, 3)

        # combo 3
        self.combo_dim3 = QComboBox()
        self.combo_dim3.addItems(self.combo_dimensions)
        self.combo_dim3.setCurrentIndex(self.previous_dimension_value_indexes[2])
        self.combo_min3 = QLineEdit()
        self.combo_min3.setValidator(self.double_validator)
        self.combo_max3 = QLineEdit()
        self.combo_max3.setValidator(self.double_validator)
        self.combo_step3 = QLineEdit()
        self.combo_step3.setValidator(self.positive_double_validator)

        layout.addWidget(self.combo_dim3, 3, 0)
        layout.addWidget(self.combo_min3, 3, 1)
        layout.addWidget(self.combo_max3, 3, 2)
        layout.addWidget(self.combo_step3, 3, 3)

        # combo 4
        self.combo_dim4 = QComboBox()
        self.combo_dim4.addItems(self.combo_dimensions)
        self.combo_dim4.setCurrentIndex(self.previous_dimension_value_indexes[3])
        self.combo_min4 = QLineEdit()
        self.combo_min4.setValidator(self.double_validator)
        self.combo_max4 = QLineEdit()
        self.combo_max4.setValidator(self.double_validator)
        self.combo_step4 = QLineEdit()
        self.combo_step4.setValidator(self.positive_double_validator)

        layout.addWidget(self.combo_dim4, 4, 0)
        layout.addWidget(self.combo_min4, 4, 1)
        layout.addWidget(self.combo_max4, 4, 2)
        layout.addWidget(self.combo_step4, 4, 3)

        self.setLayout(layout)

        # required steps background color
        self.combo_step1.textEdited.connect(self.combo_step)
        self.combo_step2.textEdited.connect(self.combo_step)
        self.combo_step3.textEdited.connect(self.combo_step)
        self.combo_step4.textEdited.connect(self.combo_step)

        # allow only unique dimension combination values across the dimension dropdowns
        self.combo_dim1.currentIndexChanged.connect(self.combo_changed)
        self.combo_dim2.currentIndexChanged.connect(self.combo_changed)
        self.combo_dim3.currentIndexChanged.connect(self.combo_changed)
        self.combo_dim4.currentIndexChanged.connect(self.combo_changed)

        # both min-max should be added; each min<max
        self.combo_min1.textEdited.connect(lambda: self.min_max_checked(self.combo_min1, self.combo_max1))
        self.combo_max1.textEdited.connect(lambda: self.min_max_checked(self.combo_min1, self.combo_max1))
        self.combo_min2.textEdited.connect(lambda: self.min_max_checked(self.combo_min2, self.combo_max2))
        self.combo_max2.textEdited.connect(lambda: self.min_max_checked(self.combo_min2, self.combo_max2))
        self.combo_min3.textEdited.connect(lambda: self.min_max_checked(self.combo_min3, self.combo_max3))
        self.combo_max3.textEdited.connect(lambda: self.min_max_checked(self.combo_min3, self.combo_max3))
        self.combo_min4.textEdited.connect(lambda: self.min_max_checked(self.combo_min4, self.combo_max4))
        self.combo_max4.textEdited.connect(lambda: self.min_max_checked(self.combo_min4, self.combo_max4))

        self.inhibit_signals = False

        # for min max valid states
        self.min_max_invalid_states = []

        # for required steps
        self.required_steps = []

    def set_field_invalid_state(self, item):
        """if parent exists then call the corresponding function and update the color"""
        if self.parent():
            self.parent().set_field_invalid_state(item)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and its invalid style, if it was previously invalid
        and enable the corresponding button"""
        if self.parent():
            self.parent().set_field_valid_state(item)

    def steps_valid_state(self):
        """Check whether required steps are filled in"""
        for step_field in self.required_steps:
            if step_field.text() == "":
                # update its state
                self.set_field_invalid_state(step_field)
                return False
        return True

    def combo_step(self):
        """Step border color and histogram button update"""
        step = self.sender()
        self.validate_step(step)

    def validate_step(self, step):
        """Step border color and histogram button update"""
        try:
            float(step.text())
            self.set_field_valid_state(step)
        except ValueError:
            self.set_field_invalid_state(step)

    @property
    def combo_dimension_boxes(self):
        """Return a list of combo boxes"""
        return [self.combo_dim1, self.combo_dim2, self.combo_dim3, self.combo_dim4]

    @property
    def combo_min_boxes(self):
        """Return a list of combo boxes"""
        return [self.combo_min1, self.combo_min2, self.combo_min3, self.combo_min4]

    @property
    def combo_max_boxes(self):
        """Return a list of combo boxes"""
        return [self.combo_max1, self.combo_max2, self.combo_max3, self.combo_max4]

    @property
    def combo_step_boxes(self):
        """Return a list of combo boxes"""
        return [self.combo_step1, self.combo_step2, self.combo_step3, self.combo_step4]

    def combo_changed(self, index):
        """Swap the combo box values when combo boxes are changed"""
        if not self.inhibit_signals:
            # find sender index and receiver index
            sender_index = self.combo_dimension_boxes.index(self.sender())
            receiver_index = index
            # cache values for min, max and step
            min_values = [x.text() for x in self.combo_min_boxes]
            max_values = [x.text() for x in self.combo_max_boxes]
            step_values = [x.text() for x in self.combo_step_boxes]

            # get steps, min and max values
            sender_combo_min = self.combo_min_boxes[sender_index]
            sender_combo_max = self.combo_max_boxes[sender_index]
            sender_combo_step = self.combo_step_boxes[sender_index]

            receiver_combo_min = self.combo_min_boxes[receiver_index]
            receiver_combo_max = self.combo_max_boxes[receiver_index]
            receiver_combo_step = self.combo_step_boxes[receiver_index]

            # swap values for combo boxes
            self.combo_dimensions[sender_index], self.combo_dimensions[receiver_index] = (
                self.combo_dimensions[receiver_index],
                self.combo_dimensions[sender_index],
            )
            self.update_combo()
            # swap values for min, max and step
            self.combo_min_boxes[sender_index].setText(min_values[receiver_index])
            self.combo_min_boxes[receiver_index].setText(min_values[sender_index])
            self.combo_max_boxes[sender_index].setText(max_values[receiver_index])
            self.combo_max_boxes[receiver_index].setText(max_values[sender_index])
            self.combo_step_boxes[sender_index].setText(step_values[receiver_index])
            self.combo_step_boxes[receiver_index].setText(step_values[sender_index])

            # update validation of min/max
            self.validate_min_max_checked(sender_combo_min, sender_combo_max, 1)
            self.validate_min_max_checked(receiver_combo_min, receiver_combo_max, 1)
            # update validation of required steps
            if sender_combo_step in self.required_steps:
                self.validate_step(sender_combo_step)
            if receiver_combo_step in self.required_steps:
                self.validate_step(receiver_combo_step)

    def min_max_checked(self, cmin, cmax):
        """Ensure Minimum and Maximum value pairs are:
        float numbers, Minimum < Maximum and both exist at the same time"""
        sender = self.sender()
        if sender == cmin:
            self.validate_min_max_checked(cmin, cmax, 1)
        else:
            self.validate_min_max_checked(cmin, cmax, 0)

    def validate_min_max_checked(self, cmin, cmax, sender_flag):
        """Validate Minimum and Maximum value pairs are:
        float numbers, Minimum < Maximum and both exist at the same time and update their state
        if sender_flag ==1 sender =cmin else sender =cmax"""

        valid = True
        if cmin in self.min_max_invalid_states:
            self.min_max_invalid_states.remove(cmin)
            self.min_max_invalid_states.remove(cmax)

        min_value = cmin.text()
        max_value = cmax.text()
        if sender_flag:
            # both min and max values need to filled in
            if (len(min_value) == 0 and len(max_value) != 0) or (len(min_value) != 0 and len(max_value) == 0):
                valid = False
            else:
                # needs to be number and less than max
                if len(min_value) != 0:
                    try:
                        tempvalue = float(min_value)
                        if tempvalue > float(max_value):
                            valid = False
                    except ValueError:
                        valid = False
        else:
            # both min and max values need to filled in
            if (len(max_value) == 0 and len(min_value) != 0) or (len(max_value) != 0 and len(min_value) == 0):
                valid = False
            else:
                # needs to be number and greater than min
                if len(max_value) != 0:
                    try:
                        tempvalue = float(max_value)
                        if tempvalue < float(min_value):
                            valid = False
                    except ValueError:
                        valid = False

        if not valid:
            self.min_max_invalid_states.append(cmin)
            self.min_max_invalid_states.append(cmax)
            self.set_field_invalid_state(cmin)
            self.set_field_invalid_state(cmax)
        else:
            self.set_field_valid_state(cmin)
            self.set_field_valid_state(cmax)

    # projection value-dimension value update functionality from mantid --> DimensionSelectorWidget.py
    def update_combo(self):
        """Update combo box dimension values"""
        self.inhibit_signals = True
        self.combo_dim1.clear()
        self.combo_dim2.clear()
        self.combo_dim3.clear()
        self.combo_dim4.clear()
        self.combo_dim1.addItems(self.combo_dimensions)
        self.combo_dim2.addItems(self.combo_dimensions)
        self.combo_dim3.addItems(self.combo_dimensions)
        self.combo_dim4.addItems(self.combo_dimensions)
        self.combo_dim1.setCurrentIndex(0)
        self.combo_dim2.setCurrentIndex(1)
        self.combo_dim3.setCurrentIndex(2)
        self.combo_dim4.setCurrentIndex(3)
        self.inhibit_signals = False

    def update_dimension_names(self, basis):
        """Update the combo box dimension selection items based on the projection values"""
        chars = ["H", "K", "L"]
        for i in range(3):
            index_max = numpy.argmax(numpy.abs(basis[i]))
            self.combo_dimensions[i] = "[" + ",".join([translation(x, chars[index_max]) for x in basis[i]]) + "]"
        self.combo_dimensions[3] = "DeltaE"
        self.update_combo()
        self.dim_min = [-numpy.inf, -numpy.inf, -numpy.inf, -numpy.inf]
        self.dim_max = [numpy.inf, numpy.inf, numpy.inf, numpy.inf]
        self.dim_step = [0.05, 0.05, 0.05, 1]
        self.dim_index = [0, 1, 2, 3]
