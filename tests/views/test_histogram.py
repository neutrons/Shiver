"""UI test for the histogram tab"""
import os
from shiver import Shiver
from mantid.simpleapi import LoadMD


def test_histogram(qtbot):
    """Test the mde and norm lists"""
    shiver = Shiver()
    qtbot.addWidget(shiver)
    shiver.show()

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

    # check that the workspace is in the norm list
    assert shiver.main_window.histogram.input_workspaces.norm_workspaces.count() == 1
