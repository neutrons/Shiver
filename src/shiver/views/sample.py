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
    QSizePolicy,
    QFileDialog,
    QErrorMessage
)
from mantid.simpleapi import mtd
from mantid.geometry import OrientedLattice
from qtpy.QtCore import Qt, QRect, QSize
import webbrowser

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")
    
#https://github.com/mantidproject/mantid/tree/main/qt/python/mantidqtinterfaces/mantidqtinterfaces/DGSPlanner
    

class SampleView(QWidget):    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialog = None
        #button callbacks
        self.btn_apply_callback = None
        self.btn_load_callback = None
        self.btn_nexus_callback = None 
        self.btn_isaw_callback = None         
        self.btn_help_callback = None
        
        self.matrix_data_callback = None
        self.lattice_data_callback =  None

    def start_dialog(self,name):
        self.dialog = SampleDialog(name,parent = self)
        self.dialog.exec_()

    def connect_lattice_data(self, callback):
        """callback for the matrix data"""
        self.lattice_data_callback = callback
        
    def connect_matrix_data(self, callback):
        """callback for the matrix data"""
        self.matrix_data_callback = callback    
    
    def connect_apply_submit(self, callback):
        """callback for the apply submit button"""
        self.btn_apply_callback = callback    
        
    def connect_load_submit(self, callback):
        """callback for the loaf submit button"""
        self.btn_load_callback = callback    

    def connect_nexus_submit(self, callback):
        """callback for the nexus submit button"""
        self.btn_nexus_callback = callback    
        
    def connect_isaw_submit(self, callback):
        """callback for the isaw submit button"""
        self.btn_isaw_callback = callback    
 
    def get_error_message(self, msg):
        """received the error message from model"""
        self.dialog.show_error_message(msg)
       

class SampleDialog(QDialog):
    """Histogram parameters widget"""

    def __init__(self,name, parent=None):
        super().__init__(parent)
        self.name = name
        self.parent = parent #define parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(f"UB setup")
        self.setMinimumSize(QSize(630, 400));

        #for initialization
        #UB matrix
        self.ub_matrix_field = QWidget()
        #inputs
        self.lattice_parameters = LatticeParametersWidget(name,parent,self.ub_matrix_field)
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
               
        ub_matrix_layout = QGridLayout()

        self.ub_matrix_label = QLabel("UB matrix")
        self.ub_matrix_label.setAlignment(Qt.AlignHCenter)        
        ub_matrix_layout.addWidget(self.ub_matrix_label, 0, 0,2,1)

        self.tableWidget = QTableWidget()
        
        #hide the header bars
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()

        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()        

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #populate the matrix table
        self.set_matrix_data()
        
        
        ub_matrix_layout.addWidget(self.tableWidget,0,1,1,2)
        
        self.ub_matrix_field.setLayout(ub_matrix_layout)
        layout.addWidget(self.ub_matrix_field)
 
        #final buttons
        self.form_btns = QWidget()
        form_btn_layout = QHBoxLayout()

        self.btn_help = QPushButton("Help")
        form_btn_layout.addWidget(self.btn_help)
        self.btn_help.setFixedSize(QSize(100, 20));
        form_btn_layout.addStretch(1)

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
        self.btn_nexus.clicked.connect(self.btn_nexus_submit)
        self.btn_isaw.clicked.connect(self.btn_isaw_submit)        
        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_help.clicked.connect(self.btn_help_action)

    def show_error_message(self, msg):
        """Will show a error dialog with the given message"""
        error = QErrorMessage(self)
        error.showMessage(msg)
        error.exec_()

    def set_matrix_data(self):
        #populate the table
        #if it exists else same defaults as SetUB
        ub_matrix = self.parent.matrix_data_callback()
        self.initialize_matrix(ub_matrix)
                
    def initialize_matrix(self,matrix_string):
        matrix = matrix_string.split(",")
        ub_matrix = [
            matrix[0:3],
            matrix[3:6],
            matrix[6::]
        ]
        self.double_validator = QtGui.QDoubleValidator(self)
        cell_items = []
        for row in range(3):
            for column in range(3):
                cell_item = QLineEdit(str(ub_matrix[row][column]))
                cell_item.setValidator(self.double_validator)
                #emmit
                self.tableWidget.setCellWidget(row,column,cell_item) 
                cell_items.append(cell_item)
        #emmit connection        
        for cell_item in cell_items:
            cell_item.textEdited.connect(self.check_items_and_update_lattice)                   
 
    def check_items_and_update_lattice(self):    
        print("check_items_and_update_lattice")
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        print("len(sender.text()", len(sender.text()))
        if ( len(sender.text()) !=0 and state == QtGui.QValidator.Acceptable):
            color = "#ffffff"
        else:
            color = "#ff0000"
        sender.setStyleSheet("QLineEdit { background-color: %s }" % color)
        
        if(self.ub_matrix_state()):
            #if matrix cells are valid, update the lattice parameters
            #TODO            
            print("Matrix valid; update lattice")
        
    def get_matrix_values_as_string(self):
        matrix_list = []
        for row in range(3):
            for column in range(3):    
                matrix_list.append(self.tableWidget.cellWidget(row,column).text())
        matrix_string = ",".join(matrix_list)
        return matrix_string
        
    def ub_matrix_state(self):
        for row in range(3):
            for column in range(3):
                param = self.tableWidget.cellWidget(row, column)
                validator = param.validator()
                state = validator.validate(param.text(), 0)[0]
                if (len(param.text()) ==0 or state != QtGui.QValidator.Acceptable):
                    return False
        return True
        
    def btn_load_submit(self):
        #TODO Ask about the DAT logs?
        parameters = {"test":"tt"}   
        print("btn_load_submit")
        self.parent.btn_load_callback(parameters)

    def btn_nexus_submit(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", filter=QString("Nexus file (*.nxs.h5);;All Files (*)")
        )
        if not filename:
            return
        if filename and self.parent.btn_nexus_callback:
            return_data = self.parent.btn_nexus_callback(filename)
            if (return_data):
                self.lattice_parameters.set_lattice_parameters(return_data)
            
    def btn_isaw_submit(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open ISAW UB file", filter=QString("Mat file (*.mat);;All Files (*)")
        )
        if not filename:
            return
        if filename and self.parent.btn_isaw_callback:
            return_data = self.parent.btn_isaw_callback(filename)  
            if (return_data):
                self.lattice_parameters.set_lattice_parameters(return_data)            

    def btn_apply_submit(self):
        #check everything is valid and then call the ub mandit algorithm
        parameters = {}
        if (self.ub_matrix_state() and self.lattice_parameters.lattice_state()):
            parameters["name"] = self.name
            parameters["latt_a"] = self.lattice_parameters.latt_a.text()
            parameters["latt_b"] = self.lattice_parameters.latt_b.text()
            parameters["latt_c"] = self.lattice_parameters.latt_c.text()
            parameters["alpha"] = self.lattice_parameters.alpha.text()
            parameters["beta"] = self.lattice_parameters.beta.text()
            parameters["gamma"] = self.lattice_parameters.gamma.text()
            parameters["latt_ux"] = self.lattice_parameters.latt_ux.text()
            parameters["latt_uy"] = self.lattice_parameters.latt_uy.text()
            parameters["latt_uz"] = self.lattice_parameters.latt_uz.text()
            parameters["latt_vx"] = self.lattice_parameters.latt_vx.text()
            parameters["latt_vy"] = self.lattice_parameters.latt_vy.text()
            parameters["latt_vz"] = self.lattice_parameters.latt_vz.text()
            parameters["matrix_ub"] = self.get_matrix_values_as_string()
            self.parent.btn_apply_callback(parameters)
            self.close()
        else:
            self.show_error_message("Invalid parameters and/or matrix.")


    def btn_cancel_action(self):
        """Cancel the sample dialog"""
        self.close()
        
    def btn_help_action(self):
        """Show the help for the sample dialog"""
        webbrowser.open("https://neutrons.github.io/Shiver/")       
        
        
class LatticeParametersWidget(QWidget):
    """Histogram parameters widget"""

    def __init__(self, name,widget_parent,ub_matrix_field, parent=None):
        super().__init__(parent)
        grid = QGridLayout() 
        self.setWindowTitle("Lattice parameters") 
        self.widget_parent = widget_parent
        self.ub_matrix_field = ub_matrix_field
        self.get_default_parameters()
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
 
    def get_default_parameters(self):
        #populate the table
        ol = self.widget_parent.lattice_data_callback()
        #default values
        self.latt_a_value = str(format(ol.a(), ".5f")) if (ol) else "0.0"
        self.latt_b_value = str(format(ol.b(), ".5f")) if (ol) else "0.0"
        self.latt_c_value = str(format(ol.c(), ".5f")) if (ol) else "0.0"
        self.latt_alpha_value = str(format(ol.alpha(), ".5f")) if (ol) else "0.0"
        self.latt_beta_value = str(format(ol.beta(), ".5f")) if (ol) else "0.0"
        self.latt_gamma_value = str(format(ol.gamma(), ".5f")) if (ol) else "0.0"
        self.latt_ux_value = str(format(ol.getuVector()[0], ".5f")) if (ol) else "0.0"
        self.latt_uy_value = str(format(ol.getuVector()[1], ".5f")) if (ol) else "0.0"
        self.latt_uz_value = str(format(ol.getuVector()[2], ".5f")) if (ol) else "0.0"
        self.latt_vx_value = str(format(ol.getvVector()[0], ".5f")) if (ol) else "0.0"
        self.latt_vy_value = str(format(ol.getvVector()[1], ".5f")) if (ol) else "0.0"
        self.latt_vz_value = str(format(ol.getvVector()[2], ".5f")) if (ol) else "0.0"


 
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
        if (self.lattice_state()):
             #if everyone is valid update matrix
            latt_a = float(self.latt_a.text())
            latt_b = float(self.latt_b.text())
            latt_c = float(self.latt_c.text()) 
 
            latt_alpha = float(self.alpha.text())
            latt_beta = float(self.beta.text())
            latt_gamma = float(self.gamma.text())           
             
            latt_ux = float(self.latt_ux.text())
            latt_uy = float(self.latt_uy.text())
            latt_uz = float(self.latt_uz.text())
            latt_vx = float(self.latt_vx.text())
            latt_vy = float(self.latt_vy.text())
            latt_vz = float(self.latt_vz.text())
            #TODO u and v cannot be colinear ; see projections crossproduct of u and v
            uvec = numpy.array([latt_ux, latt_uy, latt_uz])
            vvec = numpy.array([latt_vx, latt_vy, latt_vz])
            if numpy.linalg.norm(numpy.cross(uvec, vvec)) < 1e-5:
                return
            ol = OrientedLattice(latt_a, latt_b, latt_c, latt_alpha, latt_beta, latt_gamma)
            ol.setUFromVectors(uvec, vvec)
            print("ol",ol,ol.getuVector(), ol.getvVector())
            #TODO update the matrix
            #self.ub_matrix_field.
            print(ol.getUB())
 
    def lattice_state(self):
        """checks all parameters; returns true if they are all in acceptable state"""    
        lattice_parameters = [
            self.latt_a,
            self.latt_b,
            self.latt_c,
            self.alpha,
            self.beta,
            self.gamma,
            self.latt_ux,
            self.latt_uy,
            self.latt_uz,
            self.latt_vx,
            self.latt_vy,
            self.latt_vz       
        ]
        
        for param in lattice_parameters:
            validator = param.validator()
            state = validator.validate(param.text(), 0)[0]
            if state != QtGui.QValidator.Acceptable:
                return False
        return True

    def set_lattice_parameters(self, ol):
        self.latt_a.setText(str(format(ol.a(), ".5f")))
        self.latt_b.setText(str(format(ol.b(), ".5f")))
        self.latt_c.setText(str(format(ol.c(), ".5f")))
        self.alpha.setText(str(format(ol.alpha(), ".5f")))
        self.beta.setText(str(format(ol.beta(), ".5f")))
        self.gamma.setText(str(format(ol.gamma(), ".5f")))
        self.latt_ux.setText(str(format(ol.getuVector()[0], ".5f")))
        self.latt_uy.setText(str(format(ol.getuVector()[1], ".5f")))
        self.latt_uz.setText(str(format(ol.getuVector()[2], ".5f")))
        self.latt_vx.setText(str(format(ol.getvVector()[0], ".5f")))
        self.latt_vy.setText(str(format(ol.getvVector()[1], ".5f")))
        self.latt_vz.setText(str(format(ol.getvVector()[2], ".5f")))
        #TODO update the matrix
