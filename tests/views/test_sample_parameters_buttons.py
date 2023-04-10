"""UI tests for Sample Parameters dialog: buttons"""
import functools
from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import (
    QDialog,
    QWidget
)
from mantid.simpleapi import (
    mtd,
    LoadMD,
)
from shiver.views.sample import SampleView, LatticeParametersWidget, SampleDialog
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel

import os
import re


def test_apply_button(qtbot,tmp_path):
    """Test for pressing apply button"""
    
    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    filename = tmp_path / "test.nxs"
    filename.write_text("data")
    
    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)
    

    dialog = sample.start_dialog(name)
    dialog.show()
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)    

    
    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '4.44000'
    assert dialog.lattice_parameters.latt_b.text() == '4.44000'
    assert dialog.lattice_parameters.latt_c.text() == '4.44000'

    assert dialog.lattice_parameters.alpha.text() == '90.00000'
    assert dialog.lattice_parameters.beta.text() == '90.00000'
    assert dialog.lattice_parameters.gamma.text() == '90.00000'
    
    assert dialog.lattice_parameters.latt_ux.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uy.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uz.text() == '4.44000'

    assert dialog.lattice_parameters.latt_vx.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vy.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vz.text() == '-0.00000'
        
    #check UB matrix
    ub_matrix_data = [
        ["0.15926", "0.15926", "0.00000"],
        ["-0.15926","0.15926","0.00000"],
        ["0.00000","-0.00000","0.22523"],
    ]
    
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]
            
    dialog.close() 
 
  
def test_sample_parameters_updates_and_load_button(qtbot):
    """Test for updating lattice parameters, UB matrix and then push load button"""    
    
    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    
    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog(name)
    dialog.show()
    dialog.populate_sample_parameters()
    
    #update lattice parameter
    dialog.lattice_parameters.latt_ux.clear()
    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "54")

    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '4.44000'
    assert dialog.lattice_parameters.latt_b.text() == '4.44000'
    assert dialog.lattice_parameters.latt_c.text() == '4.44000'

    assert dialog.lattice_parameters.alpha.text() == '90.00000'
    assert dialog.lattice_parameters.beta.text() == '90.00000'
    assert dialog.lattice_parameters.gamma.text() == '90.00000'
    
    assert dialog.lattice_parameters.latt_ux.text() == '54'
    assert dialog.lattice_parameters.latt_uy.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uz.text() == '4.44000'

    assert dialog.lattice_parameters.latt_vx.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vy.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vz.text() == '-0.00000'
        
    #check UB matrix
    ub_matrix_data = [
        ["0.00151", "0.22447", "-0.01833"],
        ["-0.01839","0.01839","0.22372"],
        ["0.22447","0.00000","0.01846"],
    ]
    #check UB matrix
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]
        
        
    #update UB matrix
    ub_matrix_data[1][1] = "-0.10000"
    dialog.tableWidget.cellWidget(1, 1).clear()
    qtbot.keyClicks(dialog.tableWidget.cellWidget(1, 1), ub_matrix_data[1][1])
    dialog.tableWidget.cellWidget(row, column).editingFinished.emit()

    #check UB matrix
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '4.44443'
    assert dialog.lattice_parameters.latt_b.text() == '4.63920'
    assert dialog.lattice_parameters.latt_c.text() == '5.05774'

    assert dialog.lattice_parameters.alpha.text() == '61.38455'
    assert dialog.lattice_parameters.beta.text() == '91.23222'
    assert dialog.lattice_parameters.gamma.text() == '92.56976'
    
    assert dialog.lattice_parameters.latt_ux.text() == '4.42503'
    assert dialog.lattice_parameters.latt_uy.text() == '-0.00007'
    assert dialog.lattice_parameters.latt_uz.text() == '0.36371'

    assert dialog.lattice_parameters.latt_vx.text() == '-0.16882'
    assert dialog.lattice_parameters.latt_vy.text() == '4.62371'
    assert dialog.lattice_parameters.latt_vz.text() == '2.05286'     
        
        
        
    #push the Load button
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)    
    qtbot.wait(1000)
    
    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '4.44000'
    assert dialog.lattice_parameters.latt_b.text() == '4.44000'
    assert dialog.lattice_parameters.latt_c.text() == '4.44000'

    assert dialog.lattice_parameters.alpha.text() == '90.00000'
    assert dialog.lattice_parameters.beta.text() == '90.00000'
    assert dialog.lattice_parameters.gamma.text() == '90.00000'
    
    assert dialog.lattice_parameters.latt_ux.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uy.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uz.text() == '4.44000'

    assert dialog.lattice_parameters.latt_vx.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vy.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vz.text() == '-0.00000'
        
    #check UB matrix
    ub_matrix_data = [
        ["0.15926", "0.15926", "0.00000"],
        ["-0.15926","0.15926","0.00000"],
        ["0.00000","-0.00000","0.22523"],
    ]
    
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]
            
    dialog.close()


def test_sample_parameters_updates_invalid_and_load_button(qtbot):
    """Test for updating lattice parameters, UB matrix and then push load button"""    
    
    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    
    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog(name)
    dialog.show()
    
    ub_matrix = [
        [0, 0, 0.000],
        [0.0,1,0.000],
        [0.000,0.5774,1.1547],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.tableWidget.cellWidget(row, column), str(ub_matrix[row][column]))
            dialog.tableWidget.cellWidget(column, row).editingFinished.emit()        

    
    #check background color
    color_search = re.compile("QLineEdit { background-color: (.*) }")
    for row in range(3):
        for column in range(3):
            css_style_cell = dialog.tableWidget.cellWidget(row, column).styleSheet()
            bg_color_cell = color_search.search(css_style_cell).group(1)
            assert bg_color_cell == "#ff0000"

    #push the Load button
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)    
    
    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '4.44000'
    assert dialog.lattice_parameters.latt_b.text() == '4.44000'
    assert dialog.lattice_parameters.latt_c.text() == '4.44000'

    assert dialog.lattice_parameters.alpha.text() == '90.00000'
    assert dialog.lattice_parameters.beta.text() == '90.00000'
    assert dialog.lattice_parameters.gamma.text() == '90.00000'
    
    assert dialog.lattice_parameters.latt_ux.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uy.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uz.text() == '4.44000'

    assert dialog.lattice_parameters.latt_vx.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vy.text() == '3.13955'
    assert dialog.lattice_parameters.latt_vz.text() == '-0.00000'
        
    #check UB matrix
    ub_matrix_data = [
        ["0.15926", "0.15926", "0.00000"],
        ["-0.15926","0.15926","0.00000"],
        ["0.00000","-0.00000","0.22523"],
    ]
    
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]
 
    for row in range(3):
        for column in range(3):
            css_style_cell = dialog.tableWidget.cellWidget(row, column).styleSheet()
            bg_color_cell = color_search.search(css_style_cell).group(1)
            assert bg_color_cell == "#ffffff"

    dialog.close()


def test_nexus_button(qtbot):
    """Test for pushing the Nexus button"""    
    #HEHERE In progress
    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    nexus_sample_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../data/raw/HYS_371495.nxs.h5" #isaw_ub.mat
    )

    nexus_path = str(os.path.abspath(nexus_sample_file))
    completed = False
        
    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog(name)
    dialog.show()
    dialog.populate_sample_parameters()
    
    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed
              
        # get a reference to the dialog and handle it here
        file_dialog = dialog.btn_nexus.findChild(QtWidgets.QFileDialog)
        # get a File Name field
        line_edit = dialog.btn_nexus.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True 

    def dialog_completed():
        nonlocal completed    
        assert completed == True
        
    # click on load normalization
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(nexus_path)))
    #push the Nexus button
    qtbot.mouseClick(dialog.btn_nexus, QtCore.Qt.LeftButton)  

    qtbot.waitUntil(dialog_completed, timeout=5000)
    
    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '3.59982'
    assert dialog.lattice_parameters.latt_b.text() == '3.59919'
    assert dialog.lattice_parameters.latt_c.text() == '5.68864'

    assert dialog.lattice_parameters.alpha.text() == '89.99979'
    assert dialog.lattice_parameters.beta.text() == '90.01047'
    assert dialog.lattice_parameters.gamma.text() == '119.99615'
    
    assert dialog.lattice_parameters.latt_ux.text() == '0.06670'
    assert dialog.lattice_parameters.latt_uy.text() == '-0.16580'
    assert dialog.lattice_parameters.latt_uz.text() == '5.68253'

    assert dialog.lattice_parameters.latt_vx.text() == '2.84609'
    assert dialog.lattice_parameters.latt_vy.text() == '0.48566'
    assert dialog.lattice_parameters.latt_vz.text() == '0.06355'
        
    #check UB matrix
    ub_matrix_data = [
        ["0.31780", "0.19640", "0.00200"],
        ["-0.04340","0.25330","0.00790"],
        ["-0.00160","-0.01360","0.17560"],
    ]
    
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    
    dialog.close()

def test_isaw_button(qtbot):
    """Test for pushing the Isaw button"""    

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    nexus_sample_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "../data/raw/ls5637.mat" #isaw_ub.mat
    )

    nexus_path = str(os.path.abspath(nexus_sample_file))
    completed = False
        
    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog(name)
    dialog.show()
    dialog.populate_sample_parameters()
    
    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed
              
        # get a reference to the dialog and handle it here
        file_dialog = dialog.btn_isaw.findChild(QtWidgets.QFileDialog)
        # get a File Name field
        line_edit = dialog.btn_isaw.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True 

    def dialog_completed():
        nonlocal completed    
        assert completed == True
        
    # click on load normalization
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(nexus_path)))
    #push the Nexus button
    qtbot.mouseClick(dialog.btn_isaw, QtCore.Qt.LeftButton)  

    qtbot.waitUntil(dialog_completed, timeout=5000)
    
    #check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == '4.74399'
    assert dialog.lattice_parameters.latt_b.text() == '4.74850'
    assert dialog.lattice_parameters.latt_c.text() == '5.12352'

    assert dialog.lattice_parameters.alpha.text() == '62.39176'
    assert dialog.lattice_parameters.beta.text() == '62.39641'
    assert dialog.lattice_parameters.gamma.text() == '59.95937'
    
    assert dialog.lattice_parameters.latt_ux.text() == '-1.67586'
    assert dialog.lattice_parameters.latt_uy.text() == '-3.66099'
    assert dialog.lattice_parameters.latt_uz.text() == '-4.53080'

    assert dialog.lattice_parameters.latt_vx.text() == '2.38488'
    assert dialog.lattice_parameters.latt_vy.text() == '2.97840'
    assert dialog.lattice_parameters.latt_vz.text() == '-1.44883'
        
    #check UB matrix
    ub_matrix_data = [
        ["0.11068", "0.16311", "-0.17273"],
        ["0.22270","-0.15677","0.04430"],
        ["0.05817","-0.11802","-0.14687"],
    ]
    
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    
    dialog.close()
    
    
def test_help_button(qtbot):
    """Test for pushing the help button"""    

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog(name)
    dialog.show()
    dialog.populate_sample_parameters()
    
    #push the Help button
    qtbot.mouseClick(dialog.btn_help, QtCore.Qt.LeftButton)  

    dialog.close()    
