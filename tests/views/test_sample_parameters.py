"""UI tests for LoadingButtons widget"""
import functools
from qtpy import QtCore, QtWidgets
from mantid.simpleapi import (
    mtd,
    LoadMD,
)
from shiver.views.sample import SampleView
import os

def test_file_loading(qtbot, tmp_path):
    """Test for pressing the load buttons and checking that the callback function is called"""
    sample = SampleView()
    # load test MD workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    #open the dialog

    def set_default_parameters(self):
       pass 

    dialog = sample.start_dialog("data")
