"""Tests for the MakeSlice algorithm"""
import os
from pytest import approx
import numpy as np
from numpy.testing import assert_allclose
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    LoadMD,
    LoadEmptyInstrument,
    CloneMDWorkspace,
    MakeSlice,
    mtd,
)


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

    expected = np.array(
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
        ]
    )

    assert_allclose(line.getSignalArray(), expected)

    # test with normalization workspace
    # create a fake workspace all value 2, output should be halved
    LoadEmptyInstrument(InstrumentName="HYSPEC", DetectorValue=2, OutputWorkspace="norm")

    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace="norm",
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
        OutputWorkspace="line2",
    )

    assert "line2" in mtd

    line2 = mtd["line2"]

    assert_allclose(line2.getSignalArray(), expected / 2)

    # test with background
    # clone data as background and scale to 10%, output should be 90% of original
    background = CloneMDWorkspace("data")
    background = background * 0.1

    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace="background",
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
        OutputWorkspace="line3",
    )

    assert "line3" in mtd

    line3 = mtd["line3"]

    assert_allclose(line3.getSignalArray(), expected * 0.9)

    # test without smoothing
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
        Smoothing=0,
        OutputWorkspace="line4",
    )

    assert "line4" in mtd

    line4 = mtd["line4"]

    expected_no_smooth = np.array(
        [
            [[[0.0007342428736508]]],
            [[[0.0008463850998655]]],
            [[[0.0013263303906652]]],
            [[[0.0058883616232698]]],
            [[[0.0283100988444089]]],
            [[[0.5289070642434693]]],
            [[[0.7187110414506152]]],
            [[[0.0234447616812474]]],
            [[[0.0139223331986458]]],
            [[[0.0026170652918129]]],
            [[[0.0007270675061297]]],
            [[[0.0007382233589086]]],
        ]
    )

    assert_allclose(line4.getSignalArray(), expected_no_smooth)
