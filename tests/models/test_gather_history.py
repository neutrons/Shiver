"""Test for histogram model."""

import os
import pytest

# shiver needs to be first for importing makeslice/s algorithms
from shiver.shiver import Shiver  # noqa # pylint: disable=unused-import
from shiver.models.histogram import HistogramModel
from mantid.simpleapi import (  # pylint: disable=no-name-in-module, wrong-import-order
    mtd,
    LoadMD,
    MakeSlice,
    MakeSFCorrectedSlices,
)


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


def test_do_make_slice_invalid_workspaces():
    """Test do_make_slice method."""
    model = HistogramModel()
    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="sfdata",
    )

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="nsfdata",
    )

    # call make slice
    MakeSFCorrectedSlices(
        SFInputWorkspace="sfdata",
        NSFInputWorkspace="nsfdata",
        SFOutputWorkspace="sf_out",
        NSFOutputWorkspace="nsf_out",
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
        FlippingRatio="1",
    )

    # gather history
    history = model.get_make_slice_history("sf_out")
    assert history["SFInputWorkspace"] == "sfdata"
    assert history["NSFInputWorkspace"] == "nsfdata"

    # remove workspaces
    mtd.remove("sfdata")
    mtd.remove("nsfdata")

    # gather history
    history = model.get_make_slice_history("nsf_out")
    # workspaces should be empty
    assert history["SFInputWorkspace"] == ""
    assert history["NSFInputWorkspace"] == ""


if __name__ == "__main__":
    pytest.main([__file__])
