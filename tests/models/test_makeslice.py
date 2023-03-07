"""Tests for the MakeSlice algorithm"""
import os
from pytest import approx
from numpy.testing import assert_allclose
from mantid.simpleapi import LoadMD, MakeSlice, mtd  # pylint: disable=no-name-in-module


def test_make_slice_1d():
    """Test for 1D line 'slice', 3 dimensions integrated"""
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

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
        Dimension1Binning="-0.45,0.45",
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

    assert "line" in mtd

    line = mtd["line"]

    assert line.isMDHistoWorkspace()
    assert line.getNumDims() == 4
    assert len(line.getNonIntegratedDimensions()) == 1

    dim = line.getNonIntegratedDimensions()[0]
    assert dim.name == "[H,H,0]"
    assert dim.getMDFrame().name() == "HKL"
    assert dim.getUnits() == "r.l.u."
    assert dim.getMinimum() == approx(0.35)
    assert dim.getMaximum() == approx(0.65)
    assert dim.getBinWidth() == approx(0.025)

    assert_allclose(
        line.getSignalArray(),
        [
            [[[0.0007492361972872]]],
            [[[0.0008929792371696]]],
            [[[0.0017903405332970]]],
            [[[0.0078072896843412]]],
            [[[0.0829953919765112]]],
            [[[0.4845837178890777]]],
            [[[0.6266513551237636]]],
            [[[0.1284697945220168]]],
            [[[0.0143526387179438]]],
            [[[0.0044217235881553]]],
            [[[0.0011562705147176]]],
            [[[0.0007351419622090]]],
        ],
    )
