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

from qtpy.QtCore import Qt, QRect

class SampleParameters(QDialog):
    """Histogram parameters widget"""

    def __init__(self,name, parent=None):
        super().__init__(parent)
        self.name = name
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(f"UB setup")
        
        #inputs
        self.lattice_parameters = LatticeParametersWidget()
        layout.addWidget(self.lattice_parameters)
        
        #loading buttons
        self.load_btns = QWidget()
        btn_layout = QHBoxLayout()
        #(first entry) from DAS logs
        self.btn_load = QPushButton("Load UB")
        btn_layout.addWidget(self.btn_load)
 
        self.btn_nexus = QPushButton("Load Nexus")
        btn_layout.addWidget(self.btn_nexus)
 
        self.btn_isaw = QPushButton("Load ISAW")
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
        
        #resize the table to fit in the available space
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()


        #self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #self.tableWidget.horizontalHeader().setDefaultSectionSize(60)
        #self.tableWidget.verticalHeader().setDefaultSectionSize(60)
        
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)
        

        #populate the table
        self.ub_matrix = [
            [0.01, 0, 0],
            [0, 0.01, 0],
            [0, 0, 0.01]
        ]
        #for row in range(3):
        #    self.tableWidget.setRowHeight(row,60)
        #for column in range(3):
        #    self.tableWidget.setColumnWidth(column,60) 
        
        for row in range(3):
            for column in range(3):
                self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.ub_matrix[row][column])))


        #self.tableWidget.verticalHeader().setStretchLastSection(False)
        #self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.resizeRowsToContents()
        #self.tableWidget.verticalHeader().setStretchLastSection(True)

        
        #self.tableWidget.horizontalHeader().setStretchLastSection(False)
        #self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.resizeColumnsToContents()        
        #self.tableWidget.horizontalHeader().setStretchLastSection(True)
        #self.tableWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        ub_matrix_layout.addWidget(self.tableWidget,0,1,1,2)
        
        
        self.ub_matrix_field.setLayout(ub_matrix_layout)
        layout.addWidget(self.ub_matrix_field)
 
        #final buttons
        self.form_btns = QWidget()
        form_btn_layout = QHBoxLayout()  

        self.btn_apply = QPushButton("Apply")
        form_btn_layout.setSpacing(30)     

        form_btn_layout.addWidget(self.btn_apply)
        self.btn_cancel = QPushButton("Cancel")
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
        
        if not self.exec_():
            return
        
    def btn_load_submit(self, s):
        print("btn_load_submit", s)

    def btn_nexus_submit(self, s):
        print("btn_nexus_submit", s)
        
    def btn_isaw_submit(self, s):
        print("btn_isaw_submit", s)        

    #def button_clicked(self, s):
    #    print("click", s)
        
    #def button_clicked(self, s):
    #    print("click", s)
        
class LatticeParametersWidget(QWidget):
    """Histogram parameters widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        grid = QGridLayout() 
        self.setWindowTitle("Lattice parameters") 
        self.setLayout(grid)
        
        #1 row: a, b, c
        grid.addWidget(QLabel("a"), 0, 0)
        self.a = QLineEdit()
        grid.addWidget(self.a, 0, 1)
        
        grid.addWidget(QLabel("b"), 0, 2)
        self.b = QLineEdit()
        grid.addWidget(self.b, 0, 3)
        
        grid.addWidget(QLabel("c"), 0, 4)
        self.c = QLineEdit()
        grid.addWidget(self.c, 0, 5)
        
        #2 row: alpha, beta, gamma
        grid.addWidget(QLabel("alpha"), 1, 0)
        self.alpha = QLineEdit()
        grid.addWidget(self.alpha, 1, 1)
        
        grid.addWidget(QLabel("beta"), 1, 2)
        self.beta = QLineEdit()
        grid.addWidget(self.beta, 1, 3)
        
        grid.addWidget(QLabel("gamma"), 1, 4)
        self.gamma = QLineEdit()
        grid.addWidget(self.gamma, 1, 5)
 
 
         #3 row: ux, uy, uz
        grid.addWidget(QLabel("ux"), 2, 0)
        self.ux = QLineEdit()
        grid.addWidget(self.ux, 2, 1)
        
        grid.addWidget(QLabel("uy"), 2, 2)
        self.uy = QLineEdit()
        grid.addWidget(self.uy, 2, 3)
        
        grid.addWidget(QLabel("uz"), 2, 4)
        self.uz = QLineEdit()
        grid.addWidget(self.uz, 2, 5)
        
        #4 row: vx, vy, vz
        grid.addWidget(QLabel("vx"), 3, 0)
        self.vx = QLineEdit()
        grid.addWidget(self.vx, 3, 1)
        
        grid.addWidget(QLabel("vy"), 3, 2)
        self.vy = QLineEdit()
        grid.addWidget(self.vy, 3, 3)
        
        grid.addWidget(QLabel("vz"), 3, 4)
        self.vz = QLineEdit()
        grid.addWidget(self.vz, 3, 5)
      
