"""PyQt QDialog for Sample Parameters"""
import webbrowser
from qtpy import QtGui
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QGridLayout,
    QLabel,
    QDialog,
    QTableWidget,
    QHeaderView,
    QFileDialog,
    QErrorMessage,
    QTableWidget,
    QCheckBox,
    QRadioButton
)

from qtpy.QtCore import Qt, QSize, Signal


try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")



class AdvancedDialog(QDialog):
    """Advanced Options widget"""

    def __init__(self, parent=None):
        super().__init__(parent)


        layout = QGridLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
        self.setWindowTitle("Advanced Options")
        self.setMinimumSize(QSize(500, 400))


        #table data
        #table_data = QWidget()
        #table_layout = QHBoxLayout()
        #table_layout.setSpacing(40)

        table_label = QLabel("Mask Bank, Tube, Pixel")
        table_label.setAlignment(Qt.AlignTop)
        layout.addWidget(table_label,0,0)
        
        self.table_view = QTableWidget()
        # hide the header bars

        self.table_view.verticalHeader().hide()

        self.table_view.setRowCount(3)
        self.table_view.setColumnCount(3)

        self.table_view.resizeRowsToContents()
        self.table_view.resizeColumnsToContents()


        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setHorizontalHeaderLabels(["Bank", "Tube", "Pixel"])
        self.initialize_cells()
        
        layout.addWidget(self.table_view,0,1)

        #table_data.setLayout(table_layout)
     
        table_btns = QWidget()
        table_btn_layout = QVBoxLayout()
        table_btn_layout.setAlignment(Qt.AlignTop)
                
        self.add_btn = QPushButton("Add Row")
        #self.add_btn.setAlignment(Qt.AlignTop)        
        table_btn_layout.addWidget(self.add_btn)

        self.delete_btn = QPushButton("Delete Row")
        #self.delete_btn.setAlignment(Qt.AlignTop)                
        table_btn_layout.addWidget(self.delete_btn)
        
        table_btns.setLayout(table_btn_layout)
        layout.addWidget(table_btns,0,2)
        
        #layout.addWidget(table_data)

        e_widget = QWidget()
        e_layout = QGridLayout()
        e_layout.setContentsMargins(0, 0, 0, 0)
        # Emin - Emax
        emin_label = QLabel("Emin")
        e_layout.addWidget(emin_label,0,0)

        self.emin_input = QLineEdit()
        self.emin_input.setFixedWidth(80)
        e_layout.addWidget(self.emin_input,0,1)

        #e_layout.addStretch(1)
        # Emax
        emax_label = QLabel("Emax")
        e_layout.addWidget(emax_label,0,2)

        self.emax_input = QLineEdit()
        self.emax_input.setFixedWidth(80)
        #self.emax_input.setStyleSheet("margin-left:20px;")        
        e_layout.addWidget(self.emax_input,0,3)

        #e_layout.setContentsMargins(0, 10, 30, 10)
        e_widget.setLayout(e_layout)
        layout.addWidget(e_widget,1,0,1, 2)
 
        #2nd row
        #fl_widget = QWidget()
        #fl_layout = QHBoxLayout()
 
        #filter
        self.filter_check = QCheckBox("Filter bad pulses")
        e_layout.addWidget(self.filter_check,1,0,1,2)  
        
        lcutoff_label = QLabel("LowerCutoff")
        e_layout.addWidget(lcutoff_label,1,2)

        self.lcutoff_input = QLineEdit()
        self.lcutoff_input.setFixedWidth(80)
        e_layout.addWidget(self.lcutoff_input,1,3)
             
        #fl_widget.setLayout(fl_layout)        
        #layout.addWidget(fl_widget,2,0,1, 3)
        

        #3rd row
        tib_widget = QWidget()
        tib_layout = QHBoxLayout()
        tib_layout.setContentsMargins(0, 0, 0, 0)
        
        #Apply TIB
        tib_label = QLabel("Apply TIB")
        tib_layout.addWidget(tib_label)  
        
        self.tib_yes = QRadioButton("Yes")
        tib_layout.addWidget(self.tib_yes)

        self.tib_no = QRadioButton("No")
        tib_layout.addWidget(self.tib_no)

        self.tib_default = QRadioButton("Instrument default")
        tib_layout.addWidget(self.tib_default)

        tib_widget.setLayout(tib_layout)        
        layout.addWidget(tib_widget,3,0,1, 2)        

        #4th row
        tibmm_widget = QWidget()
        tibmm_layout = QHBoxLayout()
        tibmm_layout.setContentsMargins(0, 0, 0, 0)        
        tibmm_layout.addStretch(1)
                
        # TIB min- max
        tib_min_label = QLabel("TIB min")
        tibmm_layout.addWidget(tib_min_label)

        self.tib_min_input = QLineEdit()
        self.tib_min_input.setFixedWidth(80)
        tibmm_layout.addWidget(self.tib_min_input)

        # TIB max
        tib_max_label = QLabel("TIB max")
        tibmm_layout.addWidget(tib_max_label)

        self.tib_max_input = QLineEdit()
        self.tib_max_input.setFixedWidth(80)
        tibmm_layout.addWidget(self.tib_max_input)

        #tibmm_layout.setContentsMargins(30, 10, 30, 10)
        tibmm_widget.setLayout(tibmm_layout)
        
        layout.addWidget(tibmm_widget,4,0,1, 2)

        #text inputs
        
        #Goniometer
        gonio_label = QLabel("Goniometer")
        layout.addWidget(gonio_label,5,0)     
        
        self.gonio_input = QLineEdit()
        layout.addWidget(self.gonio_input,5,1)   

        #Temperature
        temp_label = QLabel("Temperature")
        layout.addWidget(temp_label,6,0)     
        
        self.temp_input = QLineEdit()
        layout.addWidget(self.temp_input,6,1) 
        
        #Additional Dimensions
        adt_dim_label = QLabel("Additional Dimensions")
        layout.addWidget(adt_dim_label,7,0)     
        
        self.adt_dim_input = QLineEdit()
        layout.addWidget(self.adt_dim_input,7,1) 

        # final buttons
        #form_btns = QWidget()
        #form_btn_layout = QHBoxLayout()

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setStyleSheet("margin-right:30px;padding:2px;")
        layout.addWidget(self.btn_apply,8,0)
        

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("margin-right:120px;padding:2px;")    
        layout.addWidget(self.btn_cancel,8,1)
        #form_btn_layout.addStretch(1)
                
        self.btn_help = QPushButton("Help")
        #self.btn_help.setStyleSheet("margin-left:20px;margin-right:20px;padding:2px;")
        layout.addWidget(self.btn_help,8,2)

        #form_btns.setLayout(form_btn_layout)
        #layout.addWidget(form_btns,8,0,1,2)

        # on emin/emax change
        #self.emin_input.textEdited.connect(self.e_updated)
        #self.emax_input.textEdited.connect(self.e_updated)        

    def initialize_cells(self):
        """initialize table cells"""
        self.double_validator = QtGui.QDoubleValidator(self)
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        cell_items = []
        for row in range(3):
            for column in range(3):
                cell_item = QLineEdit()  # str(ub_matrix[row][column])
                cell_item.setValidator(self.double_validator)

                self.table_view.setCellWidget(row, column, cell_item)
                cell_items.append(cell_item)
        # emit connection
        #for cell_item in cell_items:
        #    cell_item.textEdited.connect(self.validate_cell_value)
        #    cell_item.editingFinished.connect(self.check_items_and_update_lattice)
        
    def get_advanced_options_dict(self):
        """Return advanced options as a dictionary"""    
        
        
        
        
        
                
