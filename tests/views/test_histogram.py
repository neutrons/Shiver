"""UI test for the histogram tab"""
import os
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    LoadMD,
    MakeSlice,
    CreateSampleWorkspace,
)
from shiver import Shiver


def test_histogram(qtbot):
    """Test the mde and norm lists"""
    shiver = Shiver()
    qtbot.addWidget(shiver)
    shiver.show()

    # mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    # check
    med_list = shiver.main_window.histogram.input_workspaces.mde_workspaces
    assert med_list.count() == 1
    assert med_list.item(0).text() == "data"

    # norm workspace
    CreateSampleWorkspace(OutputWorkspace="ws2d", BinWidth=20000)
    # check
    norm_list = shiver.main_window.histogram.input_workspaces.norm_workspaces
    assert norm_list.count() == 1
    assert norm_list.item(0).text() == "ws2d"

    # mdh workspace
    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="0,0,1",
        QDimension1="1,1,0",
        QDimension2="-1,1,0",
        Dimension0Name="QDimension1",
        Dimension0Binning="0.35,0.025,0.65",
        Dimension1Name="QDimension0",
        Dimension1Binning="0.45,0.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="line",
    )
    # check that the workspace
    histogram_list = shiver.main_window.histogram.histogram_workspaces.histogram_workspaces
    assert histogram_list.count() == 1
    assert histogram_list.item(0).text() == "line"