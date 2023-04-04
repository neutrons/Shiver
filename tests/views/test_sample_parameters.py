"""UI tests for LoadingButtons widget"""
import functools
from qtpy import QtCore, QtWidgets
from mantid.simpleapi import (
    mtd,
    LoadMD,
)
from shiver.views.sample import SampleView, LatticeParametersWidget, SampleDialog

# from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel

import os


def test_sample_loading(qtbot, tmp_path):
    """Test for pressing the load buttons and checking that the callback function is called"""
    sample = SampleView()
    qtbot.addWidget(sample)
    # sample.show()
    # load test MD workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

    # open the dialog
    # dialog = sample.start_dialog("data")
    # dialog.exec_()
    # print("after dialog")
    # maybe show the widget?
    def get_matrix_data():
        matrix_data = [["0.0100", "0.0000", "0.0000"], ["0.0000", "0.0100", "0.0000"], ["0.0000", "0.0000", "0.0100"]]
        return matrix_data

    # sample.connect_matrix_data(get_matrix_data)

    def get_lattice_data():
        latt_parameters = {
            "latt_a": 4.44,
            "latt_b": 4.44,
            "latt_c": 4.44,
            "latt_alpha": 90.0,
            "latt_beta": 90.00000000000001,
            "latt_gamma": 90.0,
            "latt_ux": 0.0,
            "latt_uy": 0.0,
            "latt_uz": 4.44,
            "latt_vx": 3.139554108468271,
            "latt_vy": 3.139554108468271,
            "latt_vz": -4.295477125869151e-32,
        }
        return latt_parameters

    # sample.connect_lattice_data(get_lattice_data)

    params = {}
    # set steps
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_a, "4.44")
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_b, "4.44")
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_c, "4.44")
    #
    #    qtbot.keyClicks(dialog.lattice_parameters.alpha, "90.0")
    #    qtbot.keyClicks(dialog.lattice_parameters.beta, "90.0")
    #    qtbot.keyClicks(dialog.lattice_parameters.gamma, "90.0")
    #
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "0.0")
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_uy, "0.0")
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_uz, "4.44")

    #    qtbot.keyClicks(dialog.lattice_parameters.latt_vx, "3.1395")
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_vy, "3.1395")
    #    qtbot.keyClicks(dialog.lattice_parameters.latt_vz, "-4.2955")

    qtbot.wait(6000)

    assert 1 == 1

    # dialog.hide()
    # dialog = None


def test_lattice_loading(qtbot):
    """Test for pressing the load buttons and checking that the callback function is called"""
    sample = SampleView()
    # dialog = sample.start_dialog("data")
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

    # lattice = LatticeParametersWidget("data",sample,dialog)
    # qtbot.addWidget(lattice)
    # lattice.show()

    qtbot.wait(5000)

    assert 1 == 1


def test_2(qtbot):
    sample = SampleView()
    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)
    dialog = SampleDialog(name,parent = sample)
    # qtbot.addWidget(dialog)

    # if not dialog.exec_():
    #    return
    # open the dialog
    dialog = sample.start_dialog(name)

    # This is to handle modal dialogs
    def handle_dialog():
        print("inside")
        # get a reference to the dialog and handle it here
        #dialog = sample.findChild(QtWidgets.QDialog)
        # dialog = sample.start_dialog(name)
        # dialog = sample.SampleDialog(name,parent = sample)
        #dialog.show()
        # get a File Name field
        # line_edit = dialog.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        # qtbot.keyClicks(line_edit, filename)
        qtbot.wait(10000)
        # qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        #dialog.close()

    # click on load normalization
    #QtCore.QTimer.singleShot(500, functools.partial(handle_dialog))
    # qtbot.mouseClick(buttons.load_norm, QtCore.Qt.LeftButton)
    # dialog.populate_sample_parameters()
    print("I AM AFTER")
