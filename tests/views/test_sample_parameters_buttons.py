"""UI tests for Sample Parameters dialog: buttons"""
import functools
from qtpy import QtCore, QtWidgets
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
    qtbot.wait(5000)
    #    # This is to handle modal dialogs
    #    def handle_dialog(filename):
    #        print("I am here")
    #        # get a reference to the dialog and handle it here
    #        file_dialog = dialog.load_btns.findChild(QtWidgets.QFileDialog)
    #        qtbot.wait(8000)
    #        # get a File Name field
    #        line_edit = dialog.load_btns.findChild(QtWidgets.QLineEdit)
    #        # Type in file to load and press enter
    #        qtbot.keyClicks(line_edit, filename)
    #        qtbot.wait(8000)
    #        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)


    # click on load normalization
    #QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(filename)))
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

 
#python unittest mock qfileDialog in



