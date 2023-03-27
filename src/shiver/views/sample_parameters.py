"""PyQt QDialog for the sample parameters"""
import numpy
from qtpy import QtGui
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
    QDialog,
    QDialogButtonBox,
    QInputDialog,
    QTableWidget, 
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy
    # QErrorMessage,
)

from qtpy.QtCore import Qt, QRect, QSize

class SampleParameters(QDialog):
    """Histogram parameters widget"""

    def __init__(self,name, parent=None):
        super().__init__(parent)
        self.name = name
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(f"UB setup")
        self.setMinimumSize(QSize(400, 400));
        #inputs
        self.lattice_parameters = LatticeParametersWidget()
        layout.addWidget(self.lattice_parameters)
        
        #loading buttons
        self.load_btns = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)     
        #(first entry) from DAS logs
        self.btn_load = QPushButton("Load UB")
        self.btn_load.setFixedSize(QSize(100, 20));
        btn_layout.addWidget(self.btn_load)
 
        self.btn_nexus = QPushButton("Load Nexus")
        self.btn_nexus.setFixedSize(QSize(100, 20));
        btn_layout.addWidget(self.btn_nexus)
 
        self.btn_isaw = QPushButton("Load ISAW")
        self.btn_isaw.setFixedSize(QSize(100, 20));        
        btn_layout.addWidget(self.btn_isaw)
        self.load_btns.setLayout(btn_layout)
        layout.addWidget(self.load_btns)
        
        #UB matrix
        self.ub_matrix_field = QWidget()
        ub_matrix_layout = QGridLayout()

        self.ub_matrix_label = QLabel("UB matrix")
        #self.ub_matrix_label.setAlignment(Qt.AlignVCenter)
        self.ub_matrix_label.setAlignment(Qt.AlignHCenter)        
        ub_matrix_layout.addWidget(self.ub_matrix_label, 0, 0,2,1)
        #ub_matrix_layout.addWidget(QLabel(" x"), 0, 3)
        self.tableWidget = QTableWidget()
        
        #hide the header bars
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()

        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)
        

        #populate the table
        #defauls from https://docs.mantidproject.org/nightly/algorithms/SetUB-v1.html
        self.ub_matrix = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        
        for row in range(3):
            for column in range(3):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.ub_matrix[row][column])))

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()        

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        ub_matrix_layout.addWidget(self.tableWidget,0,1,1,2)
        
        
        self.ub_matrix_field.setLayout(ub_matrix_layout)
        layout.addWidget(self.ub_matrix_field)
 
        #final buttons
        self.form_btns = QWidget()
        form_btn_layout = QHBoxLayout()  
        #form_btn_layout.setSpacing(20)     

        self.btn_help = QPushButton("Help")
        form_btn_layout.addWidget(self.btn_help)
        self.btn_help.setFixedSize(QSize(100, 20));
        

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setFixedSize(QSize(80, 20));
        form_btn_layout.addWidget(self.btn_apply)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedSize(QSize(80, 20));
        form_btn_layout.addWidget(self.btn_cancel)
        
        self.form_btns.setLayout(form_btn_layout)
        layout.addWidget(self.form_btns)
        
        #button actions
        self.btn_load.clicked.connect(self.btn_load_submit)
        self.btn_load_callback = None

        self.btn_nexus.clicked.connect(self.btn_nexus_submit)
        self.btn_nexus_callback = None        

        self.btn_isaw.clicked.connect(self.btn_isaw_submit)
        self.btn_isaw_callback = None  
        
        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_apply_callback = None        

        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_cancel_callback = None          

        self.btn_help.clicked.connect(self.btn_help_action)
        self.btn_help_callback = None           
        
        if not self.exec_():
            return
        
    def btn_load_submit(self, s):
        print("btn_load_submit", s)

    def btn_nexus_submit(self, s):
        print("btn_nexus_submit", s)
        
    def btn_isaw_submit(self, s):
        print("btn_isaw_submit", s)        

    def btn_apply_submit(self, s):
        #check everything is valid and then call the ub mandit algorithm
        print("btn_apply_submit", s)
        
    def btn_cancel_action(self, s):
        print("btn_cancel_action", s)
        self.close()
        
    def btn_help_action(self, s):
        print("btn_help_action", s)        
        
        
class LatticeParametersWidget(QWidget):
    """Histogram parameters widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout() 
        self.setWindowTitle("Lattice parameters") 
        
        #default values from https://docs.mantidproject.org/nightly/algorithms/SetUB-v1.html
        self.latt_a_value = "1"
        self.latt_b_value = "1"
        self.latt_c_value = "1"
        self.latt_alpha_value = "90"
        self.latt_beta_value = "90"
        self.latt_gamma_value = "90"
        self.latt_ux_value = "1"
        self.latt_uy_value = "0"
        self.latt_uz_value = "0"
        self.latt_vx_value = "0"
        self.latt_vy_value = "1"
        self.latt_vz_value = "0"
        
        #validators
        self.length_validator = QtGui.QDoubleValidator(0.1, 1000.0, 5, self)
        self.angle_validator = QtGui.QDoubleValidator(5.0, 175.0, 5, self)
        self.double_validator = QtGui.QDoubleValidator(self)
        
        #1 row: a, b, c
        grid.addWidget(QLabel("a"), 0, 0)
        self.latt_a = QLineEdit(self.latt_a_value)
        self.latt_a.setValidator(self.length_validator)
        grid.addWidget(self.latt_a, 0, 1)
        
        grid.addWidget(QLabel("b"), 0, 2)
        self.latt_b = QLineEdit(self.latt_b_value)
        self.latt_b.setValidator(self.length_validator)
        grid.addWidget(self.latt_b, 0, 3)
        
        grid.addWidget(QLabel("c"), 0, 4)
        self.latt_c = QLineEdit(self.latt_c_value)
        self.latt_c.setValidator(self.length_validator)        
        grid.addWidget(self.latt_c, 0, 5)
        
        #2 row: alpha, beta, gamma
        grid.addWidget(QLabel("alpha"), 1, 0)
        self.alpha = QLineEdit(self.latt_alpha_value)
        self.alpha.setValidator(self.angle_validator)
        grid.addWidget(self.alpha, 1, 1)
        
        grid.addWidget(QLabel("beta"), 1, 2)
        self.beta = QLineEdit(self.latt_beta_value)
        self.beta.setValidator(self.angle_validator)        
        grid.addWidget(self.beta, 1, 3)
        
        grid.addWidget(QLabel("gamma"), 1, 4)
        self.gamma = QLineEdit(self.latt_gamma_value)
        self.gamma.setValidator(self.angle_validator)        
        grid.addWidget(self.gamma, 1, 5)
 
 
         #3 row: ux, uy, uz
        grid.addWidget(QLabel("ux"), 2, 0)
        self.latt_ux = QLineEdit(self.latt_ux_value)
        self.latt_ux.setValidator(self.double_validator)        
        grid.addWidget(self.latt_ux, 2, 1)
        
        grid.addWidget(QLabel("uy"), 2, 2)
        self.latt_uy = QLineEdit(self.latt_uy_value)
        self.latt_uy.setValidator(self.double_validator)                
        grid.addWidget(self.latt_uy, 2, 3)
        
        grid.addWidget(QLabel("uz"), 2, 4)
        self.latt_uz = QLineEdit(self.latt_uz_value)
        self.latt_uz.setValidator(self.double_validator)                
        grid.addWidget(self.latt_uz, 2, 5)
        
        #4 row: vx, vy, vz
        grid.addWidget(QLabel("vx"), 3, 0)
        self.latt_vx = QLineEdit(self.latt_vx_value)
        self.latt_vx.setValidator(self.double_validator)                
        grid.addWidget(self.latt_vx, 3, 1)
        
        grid.addWidget(QLabel("vy"), 3, 2)
        self.latt_vy = QLineEdit(self.latt_vy_value)
        self.latt_vy.setValidator(self.double_validator)        
        grid.addWidget(self.latt_vy, 3, 3)
        
        grid.addWidget(QLabel("vz"), 3, 4)
        self.latt_vz = QLineEdit(self.latt_vz_value)
        self.latt_vz.setValidator(self.double_validator)                
        grid.addWidget(self.latt_vz, 3, 5)
        
        self.setLayout(grid)
        
        #on update connection events
        self.latt_a.textEdited.connect(self.check_and_update_matrix)
        self.latt_b.textEdited.connect(self.check_and_update_matrix)
        self.latt_c.textEdited.connect(self.check_and_update_matrix)
        self.alpha.textEdited.connect(self.check_and_update_matrix)
        self.beta.textEdited.connect(self.check_and_update_matrix)
        self.gamma.textEdited.connect(self.check_and_update_matrix)
        self.latt_ux.textEdited.connect(self.check_and_update_matrix)        
        self.latt_uy.textEdited.connect(self.check_and_update_matrix)        
        self.latt_uz.textEdited.connect(self.check_and_update_matrix)            
        self.latt_vx.textEdited.connect(self.check_and_update_matrix)        
        self.latt_vy.textEdited.connect(self.check_and_update_matrix)        
        self.latt_vz.textEdited.connect(self.check_and_update_matrix)          
 
 
    def check_and_update_matrix(self):
        """validates parameters and updates the UB matrix"""
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = "#ffffff"
        else:
            color = "#ff0000"
        sender.setStyleSheet("QLineEdit { background-color: %s }" % color)
        

        
        #validate rest
        #if everyone is valid update matrix
        
            
                  
