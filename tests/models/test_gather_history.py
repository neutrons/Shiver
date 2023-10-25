"""Test for histogram model."""
import os
import pytest
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    LoadMD,
    MakeSlice,
)
from shiver.models.histogram import HistogramModel


def test_get_make_slice_history():
    """Test get_make_slice_history method."""
    model = HistogramModel()

    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    # call make slice
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
        Smoothing=1,
        OutputWorkspace="line",
    )
    # gather history
    history = model.get_make_slice_history("line")
    # check
    assert history == {
        "Algorithm": "MakeSlice",
        "InputWorkspace": "data",
        "BackgroundWorkspace": "",
        "NormalizationWorkspace": "",
        "QDimension0": "0,0,1",
        "QDimension1": "1,1,0",
        "QDimension2": "-1,1,0",
        "Dimension0Name": "QDimension1",
        "Dimension0Binning": "0.35,0.025,0.65",
        "Dimension1Name": "QDimension0",
        "Dimension1Binning": "0.45,0.55",
        "Dimension2Name": "QDimension2",
        "Dimension2Binning": "-0.2,0.2",
        "Dimension3Name": "DeltaE",
        "Dimension3Binning": "-0.5,0.5",
        "SymmetryOperations": "",
        "Smoothing": "1",  # everything is converted to string in history
        "OutputWorkspace": "line",
    }


if __name__ == "__main__":
    pytest.main([__file__])
