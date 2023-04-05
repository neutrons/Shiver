"""UI tests for Sample Parameters dialog"""
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

#laod processed Nexus
#python unittest mock qfileDialog in
#invalid a- > load ub -> a background color should be valid

def test_lattice_parameters_valid_input(qtbot):
    """Test for adding a valid input in lattice parameters"""
    
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
    
    def handle_dialog(name):
        dialog = sample.start_dialog(name)
        dialog.show()
        #dialog.populate_sample_parameters()
        
        # set steps
        qtbot.keyClicks(dialog.lattice_parameters.latt_a, "3")
        qtbot.keyClicks(dialog.lattice_parameters.latt_b, "0.3")
        qtbot.keyClicks(dialog.lattice_parameters.latt_c, "888")

        qtbot.keyClicks(dialog.lattice_parameters.alpha, "88")
        qtbot.keyClicks(dialog.lattice_parameters.beta, "50")
        qtbot.keyClicks(dialog.lattice_parameters.gamma, "39")

        qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "5")
        qtbot.keyClicks(dialog.lattice_parameters.latt_uy, "14")
        qtbot.keyClicks(dialog.lattice_parameters.latt_uz, "9")

        qtbot.keyClicks(dialog.lattice_parameters.latt_vx, "9.9")
        qtbot.keyClicks(dialog.lattice_parameters.latt_vy, "10")
        qtbot.keyClicks(dialog.lattice_parameters.latt_vz, "16.5")

        color_search = re.compile("background-color: (.*) ")
        
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
    
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(name)))
    #qtbot.waitUntil(handle_dialog)
    qtbot.wait(3000)
def test_lattice_parameters_invalid_input(qtbot):
    """Test for adding a valid input in lattice parameters"""
    
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
    
    qtbot.wait(800)
    
    
def test_ub_matrix_valid_input(qtbot):
    """Test for adding a valid input in lattice parameters"""
    
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
    [1.2, 3.4, 5.6],
    [7.89,21,4.902],
    [0.023,0.33,0.897],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.tableWidget.cellWidget(row, column), "3")


    color_search = re.compile("background-color: (.*) ")
    
    assert 1 == 1
    
    qtbot.wait(3000)    
    
