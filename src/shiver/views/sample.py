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
    QErrorMessage,
)

from qtpy.QtCore import Qt, QRect, QSize, Signal
import webbrowser

try:
    from qtpy.QtCore import QString
except ImportError:
    QString = type("")

# https://github.com/mantidproject/mantid/tree/main/qt/python/mantidqtinterfaces/mantidqtinterfaces/DGSPlanner


class SampleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialog = None
        # button callbacks
        self.btn_apply_callback = None
        self.btn_load_callback = None
        self.btn_nexus_callback = None
        self.btn_isaw_callback = None
        self.btn_help_callback = None

        # self.matrix_data_callback = None
        self.matrix_state_callback = None
        self.lattice_state_callback = None
        self.sample_data_callback = None
        self.lattice_UB_data_callback = None
        self.lattice_data_UB_callback = None

    def start_dialog(self, name):
        self.dialog = SampleDialog(name, parent=self)
        return self.dialog

    def connect_lattice_UB_data(self, callback):
        """callback for the matrix data"""
        self.lattice_UB_data_callback = callback

    def connect_UB_data_lattice(self, callback):
        """callback for the matrix data"""
        self.lattice_data_UB_callback = callback

    def connect_sample_data(self, callback):
        """callback for the matrix data"""
        self.sample_data_callback = callback


    def connect_matrix_state(self, callback):
        """callback for the matrix data"""
        self.matrix_state_callback = callback
 
    def connect_lattice_state(self, callback):
        """callback for the matrix data"""
        self.lattice_state_callback = callback
            
    # def connect_matrix_data(self, callback):
    #    """callback for the matrix data"""
    #    self.matrix_data_callback = callback

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

    changed = Signal(dict)

    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self.parent = parent  # define parent
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle(f"UB setup")
        self.setMinimumSize(QSize(630, 400))

        # inputs
        self.lattice_parameters = LatticeParametersWidget(name, parent, self)
        layout.addWidget(self.lattice_parameters)

        # loading buttons
        self.load_btns = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)
        # (first entry) from DAS logs
        self.btn_load = QPushButton("Load UB")
        self.btn_load.setFixedSize(QSize(100, 20))
        btn_layout.addWidget(self.btn_load)

        self.btn_nexus = QPushButton("Load Processed Nexus")
        self.btn_nexus.setFixedSize(QSize(160, 20))
        btn_layout.addWidget(self.btn_nexus)

        self.btn_isaw = QPushButton("Load ISAW")
        self.btn_isaw.setFixedSize(QSize(100, 20))
        btn_layout.addWidget(self.btn_isaw)
        self.load_btns.setLayout(btn_layout)
        layout.addWidget(self.load_btns)

        # for initialization
        # UB matrix
        self.ub_matrix_field = QWidget()
        self.tableWidget = QTableWidget()
        self.ub_matrix_layout = QGridLayout()

        self.ub_matrix_label = QLabel("UB matrix")
        self.ub_matrix_label.setAlignment(Qt.AlignHCenter)
        self.ub_matrix_layout.addWidget(self.ub_matrix_label, 0, 0, 2, 1)

        # hide the header bars
        self.tableWidget.horizontalHeader().hide()
        self.tableWidget.verticalHeader().hide()

        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(3)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()

        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.initialize_matrix()
        self.ub_matrix_layout.addWidget(self.tableWidget, 0, 1, 1, 2)

        self.ub_matrix_field.setLayout(self.ub_matrix_layout)
        layout.addWidget(self.ub_matrix_field)

        # final buttons
        self.form_btns = QWidget()
        form_btn_layout = QHBoxLayout()

        self.btn_help = QPushButton("Help")
        form_btn_layout.addWidget(self.btn_help)
        self.btn_help.setFixedSize(QSize(100, 20))
        form_btn_layout.addStretch(1)

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setFixedSize(QSize(80, 20))
        form_btn_layout.addWidget(self.btn_apply)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setFixedSize(QSize(80, 20))
        form_btn_layout.addWidget(self.btn_cancel)

        self.form_btns.setLayout(form_btn_layout)
        layout.addWidget(self.form_btns)

        # button actions
        self.btn_load.clicked.connect(self.btn_load_submit)
        self.btn_nexus.clicked.connect(self.btn_nexus_submit)
        self.btn_isaw.clicked.connect(self.btn_isaw_submit)
        self.btn_apply.clicked.connect(self.btn_apply_submit)
        self.btn_cancel.clicked.connect(self.btn_cancel_action)
        self.btn_help.clicked.connect(self.btn_help_action)

        self.changed.connect(self.lattice_parameters.set_lattice_parameters)

        # state cell values
        self.cell_state_valid = True

    def populate_sample_parameters(self):
        print("dsfsdf hehrere")
        params = self.parent.sample_data_callback()
        self.lattice_parameters.set_default_parameters(params)
        self.update_matrix(params)
        # populate the matrix table
        # self.set_matrix_data()

    def show_error_message(self, msg):
        """Will show a error dialog with the given message"""
        error = QErrorMessage(self)
        error.showMessage(msg)
        error.exec_()

    def trigger_update_lattice(self, lattice):
        self.changed.emit(lattice)

    # def set_matrix_data(self):
    #    # populate the table
    #    # if it exists else same defaults as SetUB
    #    ub_matrix = self.parent.matrix_data_callback()
    #    self.update_matrix(ub_matrix)

    def initialize_matrix(self):
        self.double_validator = QtGui.QDoubleValidator(self)
        self.double_validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        cell_items = []
        for row in range(3):
            for column in range(3):
                cell_item = QLineEdit()  # str(ub_matrix[row][column])
                cell_item.setValidator(self.double_validator)

                self.tableWidget.setCellWidget(row, column, cell_item)
                cell_items.append(cell_item)
        # emit connection
        for cell_item in cell_items:
            cell_item.textEdited.connect(self.validate_cell_value)
            cell_item.editingFinished.connect(self.check_items_and_update_lattice)

    def validate_cell_value(self):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        print("len(sender.text()", len(sender.text()))
        if len(sender.text()) != 0 and state == QtGui.QValidator.Acceptable:
            color = "#ffffff"
            self.cell_state_valid = True
        else:
            color = "#ff0000"
            self.cell_state_valid = False
        sender.setStyleSheet("QLineEdit { background-color: %s }" % color)

    def update_matrix(self, dict_ub_matrix):
        cell_items = []
        ub_matrix = dict_ub_matrix["ub_matrix"]
        print("update matrix")
        print(ub_matrix)
        for row in range(3):
            for column in range(3):
                self.tableWidget.cellWidget(row, column).setText(str(format(float(ub_matrix[row][column]), ".5f")))

    def check_items_and_update_lattice(self):
        print("check_items_and_update_lattice")
        tcolor = "#ff0000"
        if self.ub_matrix_state():
            # if matrix cells are valid, update the lattice parameters
            print("self.get_matrix_values_as_string()", self.get_matrix_values_as_2D_list())
            lattice = self.parent.lattice_data_UB_callback(self.get_matrix_values_as_2D_list())
            if lattice:
                print("Matrix valid; update lattice", lattice)
                self.trigger_update_lattice(lattice)
                tcolor = "#ffffff"
                self.update_all_background_color(tcolor)
        for row in range(3):
            for column in range(3):
                self.tableWidget.cellWidget(row, column).setStyleSheet("QLineEdit { background-color: %s }" % tcolor)

    def get_matrix_values_as_string(self):
        matrix_list = []
        for row in range(3):
            for column in range(3):
                matrix_list.append(self.tableWidget.cellWidget(row, column).text())
        matrix_string = ",".join(matrix_list)
        return matrix_string

    def get_matrix_values_as_2D_list(self):
        matrix_list = []
        for row in range(3):
            column_list = []
            for column in range(3):
                column_list.append(float(self.tableWidget.cellWidget(row, column).text()))
            matrix_list.append(column_list)
        return matrix_list

    def ub_matrix_state(self):
        for row in range(3):
            for column in range(3):
                param = self.tableWidget.cellWidget(row, column)
                validator = param.validator()
                state = validator.validate(param.text(), 0)[0]
                if len(param.text()) == 0 or state != QtGui.QValidator.Acceptable:
                    return False
        return self.parent.matrix_state_callback(self.get_matrix_values_as_2D_list())

    def btn_load_submit(self):
        print("load")
        color = "#ffffff"
        self.populate_sample_parameters()
        self.update_all_background_color(color)
        # self.set_matrix_data()
        # self.lattice_parameters.set_default_parameters()

    def btn_nexus_submit(self):
        color = "#ffffff"
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", filter=QString("Nexus file (*.nxs.h5);;All Files (*)")
        )
        if not filename:
            return
        if filename and self.parent.btn_nexus_callback:
            return_data = self.parent.btn_nexus_callback(filename)
            if return_data:
                self.lattice_parameters.set_lattice_parameters(return_data)
                self.update_matrix(return_data)
                self.update_all_background_color(color)
                print("return dta")

    def btn_isaw_submit(self):
        color = "#ffffff"
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open ISAW UB file", filter=QString("Mat file (*.mat);;All Files (*)")
        )
        if not filename:
            return
        if filename and self.parent.btn_isaw_callback:
            return_data = self.parent.btn_isaw_callback(filename)
            if return_data:
                print("return dta", return_data)
                self.lattice_parameters.set_lattice_parameters(return_data)
                self.update_matrix(return_data)
                self.update_all_background_color(color)

    def btn_apply_submit(self):
        # check everything is valid and then call the ub mandit algorithm
        parameters = {}
        if self.ub_matrix_state() and self.lattice_parameters.lattice_state():
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

    def matrix_update_all_background_color(self,color):
        for row in range(3):
            for column in range(3):
                self.tableWidget.cellWidget(row, column).setStyleSheet("QLineEdit { background-color: %s }" % color)  

    def update_all_background_color(self,color):
        self.matrix_update_all_background_color(color)     
        self.lattice_parameters.update_all_background_color(color)
        
        
class LatticeParametersWidget(QWidget):
    """Lattice parameters widget"""

    changed = Signal(dict)

    def __init__(self, name, widget_parent, parent=None):
        super().__init__(parent)
        grid = QGridLayout()
        self.setWindowTitle("Lattice parameters")
        self.widget_parent = widget_parent
        self.parent = parent
        # self.matrix_widget = matrix_widget

        # validators
        self.length_validator = QtGui.QDoubleValidator(0.1, 1000.0, 5, self)
        self.angle_validator = QtGui.QDoubleValidator(5.0, 175.0, 5, self)
        self.double_validator = QtGui.QDoubleValidator(self)

        # 1 row: a, b, c
        grid.addWidget(QLabel("a"), 0, 0)
        self.latt_a = QLineEdit()
        self.latt_a.setValidator(self.length_validator)
        grid.addWidget(self.latt_a, 0, 1)

        grid.addWidget(QLabel("b"), 0, 2)
        self.latt_b = QLineEdit()
        self.latt_b.setValidator(self.length_validator)
        grid.addWidget(self.latt_b, 0, 3)

        grid.addWidget(QLabel("c"), 0, 4)
        self.latt_c = QLineEdit()
        self.latt_c.setValidator(self.length_validator)
        grid.addWidget(self.latt_c, 0, 5)

        # 2 row: alpha, beta, gamma
        grid.addWidget(QLabel("alpha"), 1, 0)
        self.alpha = QLineEdit()
        self.alpha.setValidator(self.angle_validator)
        grid.addWidget(self.alpha, 1, 1)

        grid.addWidget(QLabel("beta"), 1, 2)
        self.beta = QLineEdit()
        self.beta.setValidator(self.angle_validator)
        grid.addWidget(self.beta, 1, 3)

        grid.addWidget(QLabel("gamma"), 1, 4)
        self.gamma = QLineEdit()
        self.gamma.setValidator(self.angle_validator)
        grid.addWidget(self.gamma, 1, 5)

        # 3 row: ux, uy, uz
        grid.addWidget(QLabel("ux"), 2, 0)
        self.latt_ux = QLineEdit()
        self.latt_ux.setValidator(self.double_validator)
        grid.addWidget(self.latt_ux, 2, 1)

        grid.addWidget(QLabel("uy"), 2, 2)
        self.latt_uy = QLineEdit()
        self.latt_uy.setValidator(self.double_validator)
        grid.addWidget(self.latt_uy, 2, 3)

        grid.addWidget(QLabel("uz"), 2, 4)
        self.latt_uz = QLineEdit()
        self.latt_uz.setValidator(self.double_validator)
        grid.addWidget(self.latt_uz, 2, 5)

        # 4 row: vx, vy, vz
        grid.addWidget(QLabel("vx"), 3, 0)
        self.latt_vx = QLineEdit()
        self.latt_vx.setValidator(self.double_validator)
        grid.addWidget(self.latt_vx, 3, 1)

        grid.addWidget(QLabel("vy"), 3, 2)
        self.latt_vy = QLineEdit()
        self.latt_vy.setValidator(self.double_validator)
        grid.addWidget(self.latt_vy, 3, 3)

        grid.addWidget(QLabel("vz"), 3, 4)
        self.latt_vz = QLineEdit()
        self.latt_vz.setValidator(self.double_validator)
        grid.addWidget(self.latt_vz, 3, 5)

        self.setLayout(grid)

        # on update connection events
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

        self.changed.connect(self.parent.update_matrix)

    def set_default_parameters(self, params):
        # populate the table

        print("latt set_default_parameters", params)
        # set default values and update UB matrix
        self.set_lattice_parameters(params)

    def set_lattice_parameters(self, params):
        self.latt_a.setText(str(format(params["latt_a"], ".5f")))
        self.latt_b.setText(str(format(params["latt_b"], ".5f")))
        self.latt_c.setText(str(format(params["latt_c"], ".5f")))
        self.alpha.setText(str(format(params["latt_alpha"], ".5f")))
        self.beta.setText(str(format(params["latt_beta"], ".5f")))
        self.gamma.setText(str(format(params["latt_gamma"], ".5f")))
        self.latt_ux.setText(str(format(params["latt_ux"], ".5f")))
        self.latt_uy.setText(str(format(params["latt_uy"], ".5f")))
        self.latt_uz.setText(str(format(params["latt_uz"], ".5f")))
        self.latt_vx.setText(str(format(params["latt_vx"], ".5f")))
        self.latt_vy.setText(str(format(params["latt_vy"], ".5f")))
        self.latt_vz.setText(str(format(params["latt_vz"], ".5f")))

    def trigger_update_matrix(self, ub_matrix):
        self.changed.emit(ub_matrix)

    def get_lattice_parameters(self):
        params = {}

        params["latt_a"] = float(self.latt_a.text())
        params["latt_b"] = float(self.latt_b.text())
        params["latt_c"] = float(self.latt_c.text())

        params["latt_alpha"] = float(self.alpha.text())
        params["latt_beta"] = float(self.beta.text())
        params["latt_gamma"] = float(self.gamma.text())

        params["latt_ux"] = float(self.latt_ux.text())
        params["latt_uy"] = float(self.latt_uy.text())
        params["latt_uz"] = float(self.latt_uz.text())
        params["latt_vx"] = float(self.latt_vx.text())
        params["latt_vy"] = float(self.latt_vy.text())
        params["latt_vz"] = float(self.latt_vz.text())
        return params       

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
        if self.lattice_state():
            # if everyone is valid update matrix
            params = self.get_lattice_parameters()
            print("hehrehrere")
            # update the matrix
            ub_matrix = self.widget_parent.lattice_UB_data_callback(params)
            if len(ub_matrix) != 0:
                tcolor = "#ffffff"
                self.parent.update_all_background_color(tcolor)
                self.trigger_update_matrix({"ub_matrix": ub_matrix})

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
            self.latt_vz,
        ]

        for param in lattice_parameters:
            validator = param.validator()
            state = validator.validate(param.text(), 0)[0]
            if state != QtGui.QValidator.Acceptable:
                return False
        return self.widget_parent.lattice_state_callback(self.get_lattice_parameters())
        
    def update_all_background_color(self,color):
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
            self.latt_vz,
        ]

        for param in lattice_parameters:   
            param.setStyleSheet("QLineEdit { background-color: %s }" % color) 
        
        
