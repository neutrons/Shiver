"""Tests for the MakeSlice algorithm"""
import os
from pytest import raises
from shiver.shiver import Shiver  # noqa # pylint: disable=unused-import
from mantid.simpleapi import (  # pylint: disable=no-name-in-module, wrong-import-order
    LoadMD,
    MakeMultipleSlices,
    mtd,
)


def test_make_slices_invalid():
    """Test for 1D line 'slice', 3 dimensions integrated"""

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="sfdata",
    )

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/mde_provenance_test.nxs"),
        OutputWorkspace="nsfdata",
    )

    # case 1. flipping ratio is None
    with raises(RuntimeError) as excinfo:
        MakeMultipleSlices(
            SFInputWorkspace="sfdata",
            NSFInputWorkspace="nsfdata",
            SFOutputWorkspace="out_SF",
            NSFOutputWorkspace="out_NSF",
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
            SymmetryOperations="-x,-y,-z",
            Smoothing=0,
            FlippingRatio=None,
        )

    assert len(mtd.getObjectNames()) == 2
    assert mtd.getObjectNames() == ["nsfdata", "sfdata"]
    assert str(excinfo.value).startswith("MakeMultipleSlices-v1: Flipping ratio is not defined")

    # case 2. flipping ratio is ""
    with raises(RuntimeError) as excinfo:
        MakeMultipleSlices(
            SFInputWorkspace="sfdata",
            NSFInputWorkspace="nsfdata",
            SFOutputWorkspace="out_SF",
            NSFOutputWorkspace="out_NSF",
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
            SymmetryOperations="-x,-y,-z",
            Smoothing=0,
            FlippingRatio="",
        )

    assert len(mtd.getObjectNames()) == 2
    assert mtd.getObjectNames() == ["nsfdata", "sfdata"]
    assert str(excinfo.value).startswith("MakeMultipleSlices-v1: Flipping ratio is not defined")

    # case 3. flipping ratio is formula, flipping sample log is missing
    with raises(RuntimeError) as excinfo:
        MakeMultipleSlices(
            SFInputWorkspace="sfdata",
            NSFInputWorkspace="nsfdata",
            SFOutputWorkspace="out_SF",
            NSFOutputWorkspace="out_NSF",
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
            SymmetryOperations="-x,-y,-z",
            Smoothing=0,
            FlippingRatio="2+omega",
        )

    assert len(mtd.getObjectNames()) == 2
    assert mtd.getObjectNames() == ["nsfdata", "sfdata"]
    assert str(excinfo.value).startswith("MakeMultipleSlices-v1: FlippingRatioCorrectionMD-v1: Parsing error")

    # case 4. delete intermediate workspaces
    with raises(RuntimeError) as excinfo:
        MakeMultipleSlices(
            SFInputWorkspace="sfdata",
            NSFInputWorkspace="nsfdata",
            SFOutputWorkspace="out_SF",
            NSFOutputWorkspace="out_NSF",
            BackgroundWorkspace=None,
            NormalizationWorkspace=None,
            QDimension0="0,0,1",
            QDimension1="1,1,0",
            QDimension2="-1,1,0",
            Dimension0Name="QDimension1",
            Dimension0Binning="0.09",
            Dimension1Name="QDimension0",
            Dimension1Binning="",
            Dimension2Name="QDimension2",
            Dimension2Binning="",
            Dimension3Name="DeltaE",
            Dimension3Binning="",
            SymmetryOperations="",
            Smoothing=0,
            FlippingRatio="2+omega",
            FlippingSampleLog="omega",
        )

    # only the original workspaces exist
    assert len(mtd.getObjectNames()) == 2
    assert mtd.getObjectNames() == ["nsfdata", "sfdata"]
    assert str(excinfo.value).startswith(
        "MakeMultipleSlices-v1: Cannot perform MinusMD on MDHistoWorkspace's with a different number of points."
    )
