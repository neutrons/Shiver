import numpy
from qtpy import QtGui

"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    # QListWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QGridLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QDoubleSpinBox,
    # QErrorMessage,
)

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")


def return_valid(validity, teststring, pos):
    if QString == str:
        return (validity, teststring, pos)
    else:
        return (validity, pos)


def translation(number, character):
    if number == 0:
        return "0"
    if number == 1:
        return character
    if number == -1:
        return "-" + character
    return str(number) + character


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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram parameters")

        layout = QVBoxLayout()
        self.projections_valid_state = True
        self.projections = QWidget()
        playout = QFormLayout()
        self.v3d_validator = V3DValidator(self)
        self.basis = ["1,0,0", "0,1,0", "0,0,1"]
        self.name = QLineEdit("Plot 1")
        playout.addRow("Name", self.name)

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

        self.dimensions = Dimensions()
        self.dimensions_count.setLayout(dclayout)
        layout.addWidget(self.dimensions_count)
        layout.addWidget(self.dimensions)

        symmetry = QWidget()

        slayout = QFormLayout()
        self.symmetry_operations = QLineEdit()
        slayout.addRow("Symmetry operations", self.symmetry_operations)

        self.smoothing = QDoubleSpinBox()
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
        self.cut_1d.setChecked(True)

        # submit button
        self.histogram_btn.clicked.connect(self.histogram_submit)
        self.histogram_callback = None

    def histogram_submit(self):
        """On Histogram submission button, collect histogram parameters in a dictionary"""
        step_valid_state = self.dimensions.steps_valid_state()
        if self.projections_valid_state and len(self.dimensions.min_max_invalid_states) == 0 and step_valid_state:
            parameters = {}

            # name
            parameters["Name"] = self.name.text()

            # projections
            parameters["ProjectionU"] = self.projection_u.text()
            parameters["ProjectionV"] = self.projection_v.text()
            parameters["ProjectionW"] = self.projection_w.text()

            # dimensions 1-4
            parameters["Dimension1"] = self.dimensions.combo_dim1.currentText()
            parameters["Dimension1Min"] = self.dimensions.combo_min1.text()
            parameters["Dimension1Max"] = self.dimensions.combo_max1.text()
            parameters["Dimension1Step"] = self.dimensions.combo_step1.text()
            parameters["Dimension2"] = self.dimensions.combo_dim2.currentText()
            parameters["Dimension2Min"] = self.dimensions.combo_min2.text()
            parameters["Dimension2Max"] = self.dimensions.combo_max2.text()
            parameters["Dimension2Step"] = self.dimensions.combo_step2.text()
            parameters["Dimension3"] = self.dimensions.combo_dim3.currentText()
            parameters["Dimension3Min"] = self.dimensions.combo_min3.text()
            parameters["Dimension3Max"] = self.dimensions.combo_max3.text()
            parameters["Dimension3Step"] = self.dimensions.combo_step3.text()
            parameters["Dimension4"] = self.dimensions.combo_dim4.currentText()
            parameters["Dimension4Min"] = self.dimensions.combo_min4.text()
            parameters["Dimension4Max"] = self.dimensions.combo_max4.text()
            parameters["Dimension4Step"] = self.dimensions.combo_step4.text()

            parameters["Symmetry"] = self.symmetry_operations.text()
            parameters["Smoothing"] = self.smoothing.text()

            self.histogram_callback(parameters)
        else:
            print("Invalid")

    def connect_histogram_submit(self, callback):
        self.histogram_callback = callback

    def projection_updated(self):
        """Validate the projection values"""
        sender = self.sender()
        validator = sender.validator()
        self.projections_valid_state = False
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = "#ffffff"
        elif state == QtGui.QValidator.Intermediate:
            color = "#ffaaaa"
        else:
            color = "#ff0000"
        sender.setStyleSheet("QLineEdit { background-color: %s }" % color)
        if state == QtGui.QValidator.Acceptable:
            # if value is acceptable check all three projections
            self.validateprojection_values()

    def validateprojection_values(self):
        """Validate the projection values on co-linear"""
        color = "#ff0000"
        # examine whether the projections are all non-colinear
        if (
            self.projection_u.validator().validate(self.projection_u.text(), 0)[0] == QtGui.QValidator.Acceptable
            and self.projection_v.validator().validate(self.projection_v.text(), 0)[0] == QtGui.QValidator.Acceptable
            and self.projection_w.validator().validate(self.projection_w.text(), 0)[0] == QtGui.QValidator.Acceptable
        ):
            b1 = numpy.fromstring(str(self.projection_u.text()), sep=",")
            b2 = numpy.fromstring(str(self.projection_v.text()), sep=",")
            b3 = numpy.fromstring(str(self.projection_w.text()), sep=",")
            if numpy.abs(numpy.inner(b1, numpy.cross(b2, b3))) > 1e-5:
                color = "#ffffff"
                self.projections_valid_state = True
                self.dimensions.update_dimension_names([b1, b2, b3])
        self.projection_u.setStyleSheet("QLineEdit { background-color: %s }" % color)
        self.projection_v.setStyleSheet("QLineEdit { background-color: %s }" % color)
        self.projection_w.setStyleSheet("QLineEdit { background-color: %s }" % color)

    def set_dimension(self, btn):
        """Based on the radio button step, allow the corresponding step values to be filled in;
        the rest become read-only"""

        # initialize colors and readOnly fields
        color1 = color2 = color3 = color4 = "#ffffff"

        if self.dimensions.combo_step1.text() == "":
            color1 = "#ffaaaa"
        if self.dimensions.combo_step2.text() == "":
            color2 = "#ffaaaa"
            self.dimensions.combo_step2.setReadOnly(False)
        if self.dimensions.combo_step3.text() == "":
            color3 = "#ffaaaa"
            self.dimensions.combo_step3.setReadOnly(False)
        if self.dimensions.combo_step4.text() == "":
            color4 = "#ffaaaa"
            self.dimensions.combo_step4.setReadOnly(False)

        self.required_steps = [self.dimensions.combo_step1]
        if btn.isChecked():
            # if text exists in the steps that cannot be filled in,
            # it is cleared and banckground color is changed
            if btn.text() == self.btn_dimensions[0]:
                color2 = "#ffffff"
                self.dimensions.combo_step2.setText("")
                self.dimensions.combo_step2.setReadOnly(True)
                color3 = "#ffffff"
                self.dimensions.combo_step3.setText("")
                self.dimensions.combo_step3.setReadOnly(True)
                color4 = "#ffffff"
                self.dimensions.combo_step4.setText("")
                self.dimensions.combo_step4.setReadOnly(True)
            elif btn.text() == self.btn_dimensions[1]:
                color3 = "#ffffff"
                self.dimensions.combo_step3.setText("")
                self.dimensions.combo_step3.setReadOnly(True)
                color4 = "#ffffff"
                self.dimensions.combo_step4.setText("")
                self.dimensions.combo_step4.setReadOnly(True)
                self.required_steps.append(self.dimensions.combo_step2)
            elif btn.text() == self.btn_dimensions[2]:
                color4 = "#ffffff"
                self.dimensions.combo_step4.setText("")
                self.dimensions.combo_step4.setReadOnly(True)
                self.required_steps.append(self.dimensions.combo_step2)
                self.required_steps.append(self.dimensions.combo_step3)
            else:
                self.required_steps.append(self.dimensions.combo_step2)
                self.required_steps.append(self.dimensions.combo_step3)
                self.required_steps.append(self.dimensions.combo_step4)

        self.dimensions.combo_step1.setStyleSheet("QLineEdit { background-color: %s }" % color1)
        self.dimensions.combo_step2.setStyleSheet("QLineEdit { background-color: %s }" % color2)
        self.dimensions.combo_step3.setStyleSheet("QLineEdit { background-color: %s }" % color3)
        self.dimensions.combo_step4.setStyleSheet("QLineEdit { background-color: %s }" % color4)


class Dimensions(QWidget):
    """Widget for handling the selection of output dimensions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        layout.addWidget(QLabel("Dimensions"), 0, 0)
        layout.addWidget(QLabel("Minimum"), 0, 1)
        layout.addWidget(QLabel("Maximum"), 0, 2)
        layout.addWidget(QLabel("Step"), 0, 3)

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

        # for min max valid states
        self.min_max_invalid_states = []

        # for required steos
        self.required_steps = [self.combo_step1]
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

    def steps_valid_state(self):
        for step_field in self.required_steps:
            if step_field.text() == "":
                return False
        return True

    def combo_step(self):
        step = self.sender().text()
        color = "#ffffff"
        try:
            temp_value = float(step)
        except ValueError:
            color = "#ff0000"

        self.sender().setStyleSheet("QLineEdit { background-color: %s }" % color)

    def combo_changed(self, index):
        """Ensure dimension values are unique among each other"""
        # find the combo with the duplicate value
        combo_dimension_boxes = [self.combo_dim1, self.combo_dim2, self.combo_dim3, self.combo_dim4]
        current_index = combo_dimension_boxes.index(self.sender())
        combo_dimension_boxes.remove(self.sender())
        combo_dimension_values = [x.currentText() for x in combo_dimension_boxes]

        # if selected text in the rest box values
        selected_text = self.sender().currentText()
        if selected_text in combo_dimension_values:
            # swap with the previous value of the current box
            duplicate_index = combo_dimension_values.index(selected_text)
            combo_dimension_boxes[duplicate_index].setCurrentIndex(self.previous_dimension_value_indexes[current_index])
        self.previous_dimension_value_indexes[current_index] = index

    def min_max_checked(self, cmin, cmax):
        """Ensure Minimum and Maximum value pairs are:
        float numbers, Minimum < Maximum and both exist at the same time"""
        color = "#ffffff"
        if cmin in self.min_max_invalid_states:
            self.min_max_invalid_states.remove(cmin)
            self.min_max_invalid_states.remove(cmax)
        sender = self.sender()

        min_value = cmin.text()
        max_value = cmax.text()
        if sender == cmin:
            # both min and max values need to filled in
            if (len(min_value) == 0 and len(max_value) != 0) or (len(min_value) != 0 and len(max_value) == 0):
                color = "#ff0000"
            else:
                # needs to be number and less than max
                if len(min_value) != 0:
                    try:
                        tempvalue = float(min_value)
                        if tempvalue > float(max_value):
                            color = "#ff0000"
                    except ValueError:
                        color = "#ff0000"

        if sender == cmax:
            # both min and max values need to filled in
            if (len(max_value) == 0 and len(min_value) != 0) or (len(max_value) != 0 and len(min_value) == 0):
                color = "#ff0000"
            else:
                # needs to be number and greater than min
                if len(max_value) != 0:
                    try:
                        tempvalue = float(max_value)
                        if tempvalue < float(min_value):
                            color = "#ff0000"
                    except ValueError:
                        color = "#ff0000"

        cmin.setStyleSheet("QLineEdit { background-color: %s }" % color)
        cmax.setStyleSheet("QLineEdit { background-color: %s }" % color)
        if color == "#ff0000":
            self.min_max_invalid_states.append(cmin)
            self.min_max_invalid_states.append(cmax)

    # projection value-dimension value update functionality from mantid --> DimensionSelectorWidget.py
    def update_combo(self):
        """Update combo box dimension values"""
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
