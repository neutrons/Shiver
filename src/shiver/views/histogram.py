"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QListWidget,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QGridLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QDoubleSpinBox,
)

from qtpy import QtCore, QtGui
import numpy

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")


def returnValid(validity, teststring, pos):
    if QString == str:
        return (validity, teststring, pos)
    else:
        return (validity, pos)

#validator for projections 3-digit array format: [1,0,0] from mantid --> DimensionSelectorWidget.py
class V3DValidator(QtGui.QValidator):
    def __init__(self, dummy_parent):
        super(V3DValidator, self).__init__()

    def validate(self, teststring, pos):
        parts = str(teststring).split(",")
        #invalid number of digits
        if len(parts) > 3:
            return returnValid(QtGui.QValidator.Invalid, teststring, pos)
        if len(parts) == 3:
            try:
                #valid case with 3 float numbers
                float(parts[0])
                float(parts[1])
                float(parts[2])
                return returnValid(QtGui.QValidator.Acceptable, teststring, pos)
            except ValueError:
                try:
                    #invalid case in progress of writting the array
                    float(parts[0] + "1")
                    float(parts[1] + "1")
                    float(parts[2] + "1")
                    return returnValid(QtGui.QValidator.Intermediate, teststring, pos)
                except ValueError:
                    return returnValid(QtGui.QValidator.Invalid, teststring, pos)
        return returnValid(QtGui.QValidator.Intermediate, teststring, pos)



class Histogram(QWidget):
    """Histogram widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.buttons = Buttons(self)
        self.input_workspaces = InputWorkspaces(self)
        self.histogram_parameters = HistogramParameter(self)
        self.histogram_workspaces = HistogramWorkspaces(self)

        layout = QHBoxLayout()
        layout.addWidget(self.buttons)
        layout.addWidget(self.input_workspaces)
        layout.addWidget(self.histogram_parameters)
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)


class Buttons(QWidget):
    """Buttons for Loading"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.load_dataset = QPushButton("Load dataset")
        self.gen_dataset = QPushButton("Generate dataset")
        self.load_mde = QPushButton("Load MDE")
        self.load_norm = QPushButton("Load normalization")

        layout = QVBoxLayout()
        layout.addWidget(self.load_dataset)
        layout.addWidget(self.gen_dataset)
        layout.addWidget(self.load_mde)
        layout.addWidget(self.load_norm)
        layout.addStretch()
        self.setLayout(layout)


class InputWorkspaces(QGroupBox):
    """MDE and Normalization workspace widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Input data in memory")

        self.mde_workspaces = QListWidget()
        self.norm_workspaces = QListWidget()

        layout = QHBoxLayout()
        layout.addWidget(self.mde_workspaces)
        layout.addWidget(self.norm_workspaces)
        self.setLayout(layout)


class HistogramParameter(QGroupBox):
    """Histogram parameters widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram parameters")

        layout = QVBoxLayout()

        projections = QWidget()
        playout = QFormLayout()
        self.V3DValidator = V3DValidator(self)
        self.basis = ["1,0,0", "0,1,0", "0,0,1"]
        self.name = QLineEdit("Plot 1")
        playout.addRow("Name", self.name)
        
        self.projection_u = QLineEdit(self.basis[0])
        self.projection_u.setValidator(self.V3DValidator)
        playout.addRow("Projection u", self.projection_u)

        self.projection_v = QLineEdit(self.basis[1]) 
        self.projection_v.setValidator(self.V3DValidator)       
        playout.addRow("Projection v", self.projection_v)

        self.projection_w = QLineEdit(self.basis[2]) 
        self.projection_w.setValidator(self.V3DValidator)                              
        playout.addRow("Projection w", self.projection_w)
        projections.setLayout(playout)

        layout.addWidget(projections)

        dimensions_count = QWidget()
        dclayout = QHBoxLayout()
        self.btn_dimensions = ["1D cut","2D slice","3D volume","4D volume"]
        self.cut_1d = QRadioButton(self.btn_dimensions[0])

        dclayout.addWidget(self.cut_1d)
        self.cut_2d = QRadioButton(self.btn_dimensions[1])

        dclayout.addWidget(self.cut_2d)
        self.cut_3d = QRadioButton(self.btn_dimensions[2])     

        dclayout.addWidget(self.cut_3d)
        
        self.cut_4d = QRadioButton(self.btn_dimensions[3])
        dclayout.addWidget(self.cut_4d)
        
        self.dimesions = Dimensions()
        dimensions_count.setLayout(dclayout)
        layout.addWidget(dimensions_count)
        layout.addWidget(self.dimesions)

        symmetry = QWidget()

        slayout = QFormLayout()
        slayout.addRow("Symmetry operations", QLineEdit())
        slayout.addRow("Smoothing", QDoubleSpinBox())
        symmetry.setLayout(slayout)

        layout.addWidget(symmetry)

        layout.addStretch()

        layout.addWidget(QPushButton("Histogram"))

        self.setLayout(layout)

        #on any projection change check the all are non-colinear
        self.projection_u.textEdited.connect(self.projection_updated)
        self.projection_v.textEdited.connect(self.projection_updated)
        self.projection_w.textEdited.connect(self.projection_updated) 

        #validate number of steps based on number of dimensions
        self.cut_1d.toggled.connect(lambda:self.set_dimension(self.cut_1d))
        self.cut_2d.toggled.connect(lambda:self.set_dimension(self.cut_2d))
        self.cut_3d.toggled.connect(lambda:self.set_dimension(self.cut_3d))           
        self.cut_4d.toggled.connect(lambda:self.set_dimension(self.cut_4d))
        self.cut_1d.setChecked(True)
        

    def projection_updated(self):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(),0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = "#ffffff"
        elif state == QtGui.QValidator.Intermediate:
            color = "#ffaaaa"
        else:
            color = "#ff0000"
        sender.setStyleSheet("QLineEdit { background-color: %s }" % color)
        if state == QtGui.QValidator.Acceptable:
            #if value is acceptable check all three projections
            self.validateprojection_values()

    def validateprojection_values(self):
        color = "#ff0000"
        #examine whether the projections are all non-colinear
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
        self.projection_u.setStyleSheet("QLineEdit { background-color: %s }" % color)
        self.projection_v.setStyleSheet("QLineEdit { background-color: %s }" % color)
        self.projection_w.setStyleSheet("QLineEdit { background-color: %s }" % color)

    def set_dimension(self, btn):
        color1 = color2 = color3 = color4 = "#ffffff"
        if (btn.isChecked()):
            # if text exists in the steps that cannot be filled in, it is cleared to remove user confusion and set is backgroun reddish
            if (btn.text() == self.btn_dimensions[0]):
                color2 = "#ffaaaa"
                self.dimesions.combo_step2.setText("")
                color3 = "#ffaaaa"
                self.dimesions.combo_step3.setText("")
                color4 = "#ffaaaa"
                self.dimesions.combo_step4.setText("")
            elif (btn.text() == self.btn_dimensions[1]):
                color3 = "#ffaaaa"
                self.dimesions.combo_step3.setText("")
                color4 = "#ffaaaa"
                self.dimesions.combo_step4.setText("")
            elif (btn.text() == self.btn_dimensions[2]):
                color4 = "#ffaaaa"
                self.dimesions.combo_step4.setText("")
        
        self.dimesions.combo_step1.setStyleSheet("QLineEdit { background-color: %s }" % color1)
        self.dimesions.combo_step2.setStyleSheet("QLineEdit { background-color: %s }" % color2)
        self.dimesions.combo_step3.setStyleSheet("QLineEdit { background-color: %s }" % color3)
        self.dimesions.combo_step4.setStyleSheet("QLineEdit { background-color: %s }" % color4)        
    

class Dimensions(QWidget):
    """Widget for handling the selection of output dimensions"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout()
        layout.addWidget(QLabel("Dimensions"), 0, 0)
        layout.addWidget(QLabel("Minimum"), 0, 1)
        layout.addWidget(QLabel("Maximum"), 0, 2)
        layout.addWidget(QLabel("Step"), 0, 3)
 
        self.positiveDoubleValidator = QtGui.QDoubleValidator(self)
        self.positiveDoubleValidator.setBottom(1e-10)
        #standard decimal point-format for example: 1.2
        self.positiveDoubleValidator.setNotation(QtGui.QDoubleValidator.StandardNotation) 
        
        self.combo_dimensions = ["[H,0,0]", "[0,K,0]", "[0,0,L]", "DeltaE"]
        self.previous_dimension_value_indexes = [0,1,2,3]
        
        #combo 1
        self.combo_dim1 = QComboBox()
        self.combo_dim1.addItems(self.combo_dimensions)
        self.combo_min1 = QLineEdit()
        self.combo_max1 = QLineEdit()
        self.combo_step1 = QLineEdit()
        self.combo_step1.setValidator(self.positiveDoubleValidator)
        
        layout.addWidget(self.combo_dim1, 1, 0)
        layout.addWidget(self.combo_min1, 1, 1)
        layout.addWidget(self.combo_max1, 1, 2)
        layout.addWidget(self.combo_step1, 1, 3)

        #combo 2
        self.combo_dim2 = QComboBox()
        self.combo_dim2.addItems(self.combo_dimensions)
        self.combo_dim2.setCurrentIndex(self.previous_dimension_value_indexes[1])
        self.combo_min2 = QLineEdit()
        self.combo_max2 = QLineEdit()
        self.combo_step2 = QLineEdit()
        self.combo_step2.setValidator(self.positiveDoubleValidator)
                
        layout.addWidget(self.combo_dim2, 2, 0)
        layout.addWidget(self.combo_min2, 2, 1)
        layout.addWidget(self.combo_max2, 2, 2)
        layout.addWidget(self.combo_step2, 2, 3)

        #combo 3
        self.combo_dim3 = QComboBox()
        self.combo_dim3.addItems(self.combo_dimensions)
        self.combo_dim3.setCurrentIndex(self.previous_dimension_value_indexes[2])
        self.combo_min3 = QLineEdit()
        self.combo_max3 = QLineEdit()
        self.combo_step3 = QLineEdit()
        self.combo_step3.setValidator(self.positiveDoubleValidator)
                        
        layout.addWidget(self.combo_dim3, 3, 0)
        layout.addWidget(self.combo_min3, 3, 1)
        layout.addWidget(self.combo_max3, 3, 2)
        layout.addWidget(self.combo_step3, 3, 3)        

        #combo 4
        self.combo_dim4 = QComboBox()
        self.combo_dim4.addItems(self.combo_dimensions)
        self.combo_dim4.setCurrentIndex(self.previous_dimension_value_indexes[3])
        self.combo_min4 = QLineEdit()
        self.combo_max4 = QLineEdit()
        self.combo_step4 = QLineEdit()
        self.combo_step4.setValidator(self.positiveDoubleValidator)
                        
        layout.addWidget(self.combo_dim4, 4, 0)
        layout.addWidget(self.combo_min4, 4, 1)
        layout.addWidget(self.combo_max4, 4, 2)
        layout.addWidget(self.combo_step4, 4, 3)                

        self.setLayout(layout)             

class HistogramWorkspaces(QGroupBox):
    """Histogram workspaces widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram data in memory")

        self.histogram_workspaces = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)
