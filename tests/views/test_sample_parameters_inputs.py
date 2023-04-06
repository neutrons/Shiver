"""UI tests for Sample Parameters dialog: input values"""
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


def test_lattice_parameters_valid_input(qtbot):
    """Test for adding valid inputs in lattice parameters"""
    
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
    
    # set parameters
    qtbot.keyClicks(dialog.lattice_parameters.latt_a, "14.15262")
    qtbot.keyClicks(dialog.lattice_parameters.latt_b, "19.29034")
    qtbot.keyClicks(dialog.lattice_parameters.latt_c, "8.58130")

    qtbot.keyClicks(dialog.lattice_parameters.alpha, "90.00000")
    qtbot.keyClicks(dialog.lattice_parameters.beta, "105.07377")
    qtbot.keyClicks(dialog.lattice_parameters.gamma, "89.99999")

    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "10.63154")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uy, "11.95967")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uz, "0.20051")

    qtbot.keyClicks(dialog.lattice_parameters.latt_vx, "-8.69201")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vy, "15.09003")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vz, "0.50648")

    color_search = re.compile("QLineEdit { background-color: (.*) }")

    css_style_latt_a = dialog.lattice_parameters.latt_a.styleSheet()
    css_style_latt_b = dialog.lattice_parameters.latt_b.styleSheet()
    css_style_latt_c = dialog.lattice_parameters.latt_c.styleSheet()

    css_style_latt_alpha = dialog.lattice_parameters.alpha.styleSheet()
    css_style_latt_beta = dialog.lattice_parameters.beta.styleSheet()
    css_style_latt_gamma = dialog.lattice_parameters.gamma.styleSheet()

    css_style_latt_ux = dialog.lattice_parameters.latt_ux.styleSheet()
    css_style_latt_uy = dialog.lattice_parameters.latt_uy.styleSheet()
    css_style_latt_uz = dialog.lattice_parameters.latt_uz.styleSheet()

    css_style_latt_vx = dialog.lattice_parameters.latt_vx.styleSheet()
    css_style_latt_vy = dialog.lattice_parameters.latt_vy.styleSheet()
    css_style_latt_vz = dialog.lattice_parameters.latt_vz.styleSheet()
    
    bg_color_latt_a = color_search.search(css_style_latt_a).group(1)
    bg_color_latt_b = color_search.search(css_style_latt_b).group(1)
    bg_color_latt_c = color_search.search(css_style_latt_c).group(1)
    
    bg_color_alpha = color_search.search(css_style_latt_alpha).group(1)
    bg_color_beta = color_search.search(css_style_latt_beta).group(1)
    bg_color_gamma = color_search.search(css_style_latt_gamma).group(1)
    
    bg_color_latt_ux = color_search.search(css_style_latt_ux).group(1)
    bg_color_latt_uy = color_search.search(css_style_latt_uy).group(1)
    bg_color_latt_uz = color_search.search(css_style_latt_uz).group(1)

    bg_color_latt_vx = color_search.search(css_style_latt_vx).group(1)
    bg_color_latt_vy = color_search.search(css_style_latt_vy).group(1)
    bg_color_latt_vz = color_search.search(css_style_latt_vz).group(1)

    assert bg_color_latt_a == "#ffffff"
    assert bg_color_latt_b == "#ffffff"
    assert bg_color_latt_c == "#ffffff"

    assert bg_color_alpha == "#ffffff"
    assert bg_color_beta == "#ffffff"
    assert bg_color_gamma == "#ffffff"
    
    assert bg_color_latt_ux == "#ffffff"
    assert bg_color_latt_uy == "#ffffff"
    assert bg_color_latt_uz == "#ffffff"
    
    assert bg_color_latt_vx == "#ffffff"
    assert bg_color_latt_vy == "#ffffff"
    assert bg_color_latt_vz == "#ffffff"    
    
    
    #check the table updates
    ub_matrix_data = [
        ["-0.04538", "0.04055", "-0.01259"],
        ["0.00134","-0.00315","0.11687"],
        ["0.05739","0.03214","0.02734"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]
    
    dialog.close()

def test_lattice_parameters_invalid_input(qtbot):
    """Test for adding invalid inputs in lattice parameters"""
    
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
    #dialog.populate_sample_parameters()
    
    # set parameters
    qtbot.keyClicks(dialog.lattice_parameters.latt_a, "9999")
    qtbot.keyClicks(dialog.lattice_parameters.latt_b, "10001")
    qtbot.keyClicks(dialog.lattice_parameters.latt_c, "10000")

    qtbot.keyClicks(dialog.lattice_parameters.alpha, "4")
    qtbot.keyClicks(dialog.lattice_parameters.beta, "180")
    qtbot.keyClicks(dialog.lattice_parameters.gamma, "10001")

    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "a")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uy, "b")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uz, "c")

    qtbot.keyClicks(dialog.lattice_parameters.latt_vx, "d")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vy, "h")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vz, "f")

    color_search = re.compile("background-color: (.*) ")
    
    #check banckground color
    css_style_latt_a = dialog.lattice_parameters.latt_a.styleSheet()
    css_style_latt_b = dialog.lattice_parameters.latt_b.styleSheet()
    css_style_latt_c = dialog.lattice_parameters.latt_c.styleSheet()

    css_style_latt_alpha = dialog.lattice_parameters.alpha.styleSheet()
    css_style_latt_beta = dialog.lattice_parameters.beta.styleSheet()
    css_style_latt_gamma = dialog.lattice_parameters.gamma.styleSheet()

    #check text
    latt_ux_text = dialog.lattice_parameters.latt_ux.text()
    latt_uy_text = dialog.lattice_parameters.latt_ux.text()
    latt_uz_text = dialog.lattice_parameters.latt_ux.text()

    latt_vx_text = dialog.lattice_parameters.latt_vx.text()
    latt_vy_text = dialog.lattice_parameters.latt_vy.text()
    latt_vz_text = dialog.lattice_parameters.latt_vz.text()

    bg_color_latt_a = color_search.search(css_style_latt_a).group(1)
    bg_color_latt_b = color_search.search(css_style_latt_b).group(1)
    bg_color_latt_c = color_search.search(css_style_latt_c).group(1)
    
    bg_color_alpha = color_search.search(css_style_latt_alpha).group(1)
    bg_color_beta = color_search.search(css_style_latt_beta).group(1)
    bg_color_gamma = color_search.search(css_style_latt_gamma).group(1)
    
    assert bg_color_latt_a == "#ff0000"
    assert bg_color_latt_b == "#ff0000"
    assert bg_color_latt_c == "#ff0000"

    assert bg_color_alpha == "#ff0000"
    assert bg_color_beta == "#ff0000"
    assert bg_color_gamma == "#ff0000"
    
    assert latt_ux_text == ""
    assert latt_uy_text == ""
    assert latt_uz_text == ""
    
    assert latt_vx_text == ""
    assert latt_vy_text == ""
    assert latt_vz_text == ""    
    
    dialog.close()


    
def test_ub_matrix_valid_input(qtbot):
    """Test for adding valid inputs in UB matrix"""
    
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
    
    # set matrix data
    ub_matrix_data = [
        ["1.1", "1", "1"],
        ["0.0","1.2","0.0"],
        ["0.0","0.0","1.4"],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.tableWidget.cellWidget(row, column), str(ub_matrix_data[row][column]))
            dialog.tableWidget.cellWidget(row, column).editingFinished.emit()

    #check background color
    color_search = re.compile("QLineEdit { background-color: (.*) }")
    for row in range(3):
        for column in range(3):
            css_style_cell = dialog.tableWidget.cellWidget(row, column).styleSheet()
            bg_color_cell = color_search.search(css_style_cell).group(1)
            assert bg_color_cell == "#ffffff"
    
    assert dialog.lattice_parameters.latt_a.text() == '1.34982'
    assert dialog.lattice_parameters.latt_b.text() == '0.83333'
    assert dialog.lattice_parameters.latt_c.text() == '0.71429'

    assert dialog.lattice_parameters.alpha.text() == '90.00000'
    assert dialog.lattice_parameters.beta.text() == '118.75487'
    assert dialog.lattice_parameters.gamma.text() == '124.14164'
    
    assert dialog.lattice_parameters.latt_ux.text() == '-0.64935'
    assert dialog.lattice_parameters.latt_uy.text() == '0.00000'
    assert dialog.lattice_parameters.latt_uz.text() == '0.71429'

    assert dialog.lattice_parameters.latt_vx.text() == '0.90909'
    assert dialog.lattice_parameters.latt_vy.text() == '0.00000'
    assert dialog.lattice_parameters.latt_vz.text() == '0.00000'
    
    dialog.close()
    
    
def test_ub_matrix_invalid_input(qtbot):
    """Test for adding invalid inputs in UB matrix"""
    
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
    
    # set matrix data
    ub_matrix_data = [
        ["a", "b", "c"],
        ["k","q","l"],
        ["o","s","m"],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.tableWidget.cellWidget(row, column), str(ub_matrix_data[row][column]))

    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ""
    

    dialog.close()   
    
    
def test_sample_parameters_initialization(qtbot):
    """Test for initializing lattice parameters and UB matrix from an MDE"""    
    
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
 
def test_sample_parameters_updates(qtbot):
    """Test for updating lattice parameters and UB matrix"""    
    
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
    
    for row in range(3):
        for column in range(3):
            cell_text = dialog.tableWidget.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]
        
        
    #update UB matrix
    ub_matrix_data[1][1] = "-0.10000"
    dialog.tableWidget.cellWidget(1, 1).clear()
    qtbot.keyClicks(dialog.tableWidget.cellWidget(1, 1), ub_matrix_data[1][1])
    dialog.tableWidget.cellWidget(row, column).editingFinished.emit()


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
                    
    dialog.close()                

