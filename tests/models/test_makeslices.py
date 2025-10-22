"""Tests for the MakeSlice algorithm"""

import os

import numpy as np

# Need to import the new algorithms so they are registered with mantid
import shiver.shiver  # noqa: F401 isort: skip #must be imported before mantid
from mantid.simpleapi import (  # pylint: disable=no-name-in-module, wrong-import-order
    LoadMD,
    LoadNexusProcessed,
    MakeSFCorrectedSlices,
    MakeSlice,
    mtd,
)
from numpy.testing import assert_allclose
from pytest import approx, raises

from shiver import __version__


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
    with raises(TypeError) as excinfo:
        MakeSFCorrectedSlices(
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
    assert str(excinfo.value) == "in running MakeSFCorrectedSlices: Some invalid Properties found"

    # case 2. flipping ratio is ""
    with raises(ValueError) as excinfo:
        MakeSFCorrectedSlices(
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
    assert str(excinfo.value).startswith('Problem setting "FlippingRatio" in MakeSFCorrectedSlices-v1:')

    # case 3. flipping ratio is formula, flipping sample log is missing
    with raises(RuntimeError) as excinfo:
        MakeSFCorrectedSlices(
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
    assert str(excinfo.value).startswith("MakeSFCorrectedSlices-v1: FlippingRatioCorrectionMD-v1: Parsing error")

    # case 4. delete intermediate workspaces
    with raises(RuntimeError) as excinfo:
        MakeSFCorrectedSlices(
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
            FlippingRatioSampleLog="omega",
        )

    # only the original workspaces exist
    assert len(mtd.getObjectNames()) == 2
    assert mtd.getObjectNames() == ["nsfdata", "sfdata"]
    assert str(excinfo.value).startswith(
        "MakeSFCorrectedSlices-v1: Cannot perform MinusMD on MDHistoWorkspace's with a different number of points."
    )


def test_make_slices_1d():
    """Test for 1D 'slices'"""

    LoadNexusProcessed(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/normalization/TiZr.nxs"),
        OutputWorkspace="norm",
    )

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_SF.nxs"),
        OutputWorkspace="sfdata",
    )

    MakeSlice(
        InputWorkspace="sfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace="norm",
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="",
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="sfdata_unpol",
    )

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
        OutputWorkspace="nsfdata",
    )

    MakeSlice(
        InputWorkspace="nsfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace="norm",
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="",
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="nsfdata_unpol",
    )

    # call make slice
    MakeSFCorrectedSlices(
        SFInputWorkspace="sfdata",
        NSFInputWorkspace="nsfdata",
        SFOutputWorkspace="out_SF",
        NSFOutputWorkspace="out_NSF",
        BackgroundWorkspace=None,
        NormalizationWorkspace="norm",
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="",  # 0.05
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        FlippingRatio="8",
    )

    # corrected SF
    assert "out_SF" in mtd

    sfdata_cor = mtd["out_SF"]

    assert sfdata_cor.isMDHistoWorkspace()
    assert sfdata_cor.getNumDims() == 4
    assert len(sfdata_cor.getNonIntegratedDimensions()) == 1

    dim = sfdata_cor.getNonIntegratedDimensions()[0]
    assert dim.name == "[H,H,0]"
    assert dim.getMDFrame().name() == "HKL"
    assert dim.getUnits() == "r.l.u."
    assert dim.getMinimum() == approx(0)
    assert dim.getMaximum() == approx(1)
    assert dim.getBinWidth() == approx(0.05)

    # corrected NSF
    assert "out_NSF" in mtd

    nsfdata_cor = mtd["out_NSF"]

    assert nsfdata_cor.isMDHistoWorkspace()
    assert nsfdata_cor.getNumDims() == 4
    assert len(nsfdata_cor.getNonIntegratedDimensions()) == 1

    dim = nsfdata_cor.getNonIntegratedDimensions()[0]
    assert dim.name == "[H,H,0]"
    assert dim.getMDFrame().name() == "HKL"
    assert dim.getUnits() == "r.l.u."
    assert dim.getMinimum() == approx(0)
    assert dim.getMaximum() == approx(1)
    assert dim.getBinWidth() == approx(0.05)

    # compare intensities
    sfdata = mtd["sfdata_unpol"]
    nsfdata = mtd["nsfdata_unpol"]

    sfdata_intensities = sfdata.getSignalArray()
    nsfdata_intensities = nsfdata.getSignalArray()

    sfdata_cor_intensities = sfdata_cor.getSignalArray()
    nsfdata_cor_intensities = nsfdata_cor.getSignalArray()

    assert len(sfdata_intensities) == len(sfdata_cor_intensities)
    assert len(nsfdata_intensities) == len(nsfdata_cor_intensities)
    assert len(sfdata_cor_intensities) == len(nsfdata_cor_intensities)

    # check intensities
    for i in range(0, 14):
        assert_allclose(sfdata_cor_intensities[i], [[[np.nan]]])
        assert_allclose(nsfdata_cor_intensities[i], [[[np.nan]]])

    # flipping ratio = 8
    # formula for SFc[i] = 8/7*SF[i] - 1/7*NSF[i]
    for i in range(14, len(sfdata_intensities)):
        expected_corr_sf = 8 / 7 * sfdata_intensities[i] - 1 / 7 * nsfdata_intensities[i]
        assert_allclose(expected_corr_sf, sfdata_cor_intensities[i])

    # flipping ratio = 8
    # formula for NSFc[i] = 8/7*NSF[i] - 1/7*FSF[i]
    for i in range(14, len(nsfdata_intensities)):
        expected_corr_nsf = 8 / 7 * nsfdata_intensities[i] - 1 / 7 * sfdata_intensities[i]
        assert_allclose(expected_corr_nsf, nsfdata_cor_intensities[i])

    # Check shiver version is captured in SF workspace history
    makemultipleslices_algo = sfdata_cor.getHistory().getAlgorithmHistory(15)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"

    # Check shiver version is captured in NSF workspace history
    makemultipleslices_algo = nsfdata_cor.getHistory().getAlgorithmHistory(15)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"


def test_make_slices_2d():
    """Test for 2D 'slices'"""

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_SF.nxs"),
        OutputWorkspace="sfdata",
    )

    MakeSlice(
        InputWorkspace="sfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="sfdata_unpol",
    )

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
        OutputWorkspace="nsfdata",
    )

    MakeSlice(
        InputWorkspace="nsfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="nsfdata_unpol",
    )

    # call make slice
    MakeSFCorrectedSlices(
        SFInputWorkspace="sfdata",
        NSFInputWorkspace="nsfdata",
        SFOutputWorkspace="out_SF",
        NSFOutputWorkspace="out_NSF",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        FlippingRatio="2*Ei",
        FlippingRatioSampleLog="Ei",
    )

    # corrected SF
    assert "out_SF" in mtd
    sfdata_cor = mtd["out_SF"]

    assert sfdata_cor.isMDHistoWorkspace()
    assert sfdata_cor.getNumDims() == 4
    assert len(sfdata_cor.getNonIntegratedDimensions()) == 2

    # dimension 1
    dim_1 = sfdata_cor.getNonIntegratedDimensions()[0]
    assert dim_1.name == "[H,H,0]"
    assert dim_1.getMDFrame().name() == "HKL"
    assert dim_1.getUnits() == "r.l.u."
    assert dim_1.getMinimum() == approx(0)
    assert dim_1.getMaximum() == approx(1)
    assert dim_1.getBinWidth() == approx(0.05)

    # dimension 2
    dim_2 = sfdata_cor.getNonIntegratedDimensions()[1]
    assert dim_2.name == "[0,0,L]"
    assert dim_2.getBinWidth() == approx(0.05)

    # corrected NSF
    assert "out_NSF" in mtd
    nsfdata_cor = mtd["out_NSF"]

    assert nsfdata_cor.isMDHistoWorkspace()
    assert nsfdata_cor.getNumDims() == 4
    assert len(nsfdata_cor.getNonIntegratedDimensions()) == 2

    # dimension 1
    dim_1 = nsfdata_cor.getNonIntegratedDimensions()[0]
    assert dim_1.name == "[H,H,0]"
    assert dim_1.getMDFrame().name() == "HKL"
    assert dim_1.getUnits() == "r.l.u."
    assert dim_1.getMinimum() == approx(0)
    assert dim_1.getMaximum() == approx(1)
    assert dim_1.getBinWidth() == approx(0.05)

    # dimension 2
    dim_2 = nsfdata_cor.getNonIntegratedDimensions()[1]
    assert dim_2.name == "[0,0,L]"
    assert dim_2.getBinWidth() == approx(0.05)

    # compare intensities
    sfdata = mtd["sfdata_unpol"]
    nsfdata = mtd["nsfdata_unpol"]

    sfdata_intensities = sfdata.getSignalArray()
    nsfdata_intensities = nsfdata.getSignalArray()

    sfdata_cor_intensities = sfdata_cor.getSignalArray()
    nsfdata_cor_intensities = nsfdata_cor.getSignalArray()

    assert len(sfdata_intensities) == len(sfdata_cor_intensities)
    assert len(nsfdata_intensities) == len(nsfdata_cor_intensities)
    assert len(sfdata_cor_intensities) == len(nsfdata_cor_intensities)

    # check intensities
    for i in range(0, 14):
        for j in range(0, len(sfdata_cor_intensities[i])):
            assert_allclose(sfdata_cor_intensities[i][j], [[np.nan]])
            assert_allclose(nsfdata_cor_intensities[i][j], [[np.nan]])

    # flipping ratio = 2*20
    # formula for SFc[i] = 40/39*SF[i] - 1/39*NSF[i]
    for i in range(14, len(sfdata_intensities)):
        for j in range(0, len(sfdata_cor_intensities[i])):
            expected_corr_sf = 40 / 39 * sfdata_intensities[i][j] - 1 / 39 * nsfdata_intensities[i][j]
            assert_allclose(expected_corr_sf, sfdata_cor_intensities[i][j])

    # flipping ratio = 2*20
    # formula for NSFc[i] = 40/39*NSF[i] - 1/39*FSF[i]
    for i in range(14, len(nsfdata_intensities)):
        for j in range(0, len(nsfdata_cor_intensities[i])):
            expected_corr_nsf = 40 / 39 * nsfdata_intensities[i][j] - 1 / 39 * sfdata_intensities[i][j]
            assert_allclose(expected_corr_nsf, nsfdata_cor_intensities[i][j])

    # Check shiver version is captured in SF workspace history
    makemultipleslices_algo = sfdata_cor.getHistory().getAlgorithmHistory(4)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"

    # Check shiver version is captured in NSF workspace history
    makemultipleslices_algo = nsfdata_cor.getHistory().getAlgorithmHistory(4)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"


def test_make_slices_3d():
    """Test for 3D 'slices'"""

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_SF.nxs"),
        OutputWorkspace="sfdata",
    )

    MakeSlice(
        InputWorkspace="sfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="0.05",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="sfdata_unpol",
    )

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
        OutputWorkspace="nsfdata",
    )

    MakeSlice(
        InputWorkspace="nsfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0.5,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="0.5,0.05,1",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="nsfdata_unpol",
    )

    # call make slice
    MakeSFCorrectedSlices(
        SFInputWorkspace="sfdata",
        NSFInputWorkspace="nsfdata",
        SFOutputWorkspace="out_SF",
        NSFOutputWorkspace="out_NSF",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0.5,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="0.5,0.05,1",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,1",
        SymmetryOperations="",
        Smoothing=0,
        FlippingRatio="2*Ei",
        FlippingRatioSampleLog="Ei",
    )

    # corrected SF
    assert "out_SF" in mtd
    sfdata_cor = mtd["out_SF"]

    assert sfdata_cor.isMDHistoWorkspace()
    assert sfdata_cor.getNumDims() == 4
    assert len(sfdata_cor.getNonIntegratedDimensions()) == 3

    # dimension 1
    dim_1 = sfdata_cor.getNonIntegratedDimensions()[0]
    assert dim_1.name == "[H,H,0]"
    assert dim_1.getMDFrame().name() == "HKL"
    assert dim_1.getUnits() == "r.l.u."
    assert dim_1.getMinimum() == approx(0)
    assert dim_1.getMaximum() == approx(1)
    assert dim_1.getBinWidth() == approx(0.05)

    # dimension 2
    dim_2 = sfdata_cor.getNonIntegratedDimensions()[1]
    assert dim_2.name == "[0,0,L]"
    assert dim_2.getBinWidth() == approx(0.05)

    # dimension 3
    dim_3 = sfdata_cor.getNonIntegratedDimensions()[2]
    assert dim_3.name == "[-H,H,0]"
    assert dim_3.getBinWidth() == approx(0.05)

    # corrected NSF
    assert "out_NSF" in mtd
    nsfdata_cor = mtd["out_NSF"]

    assert nsfdata_cor.isMDHistoWorkspace()
    assert nsfdata_cor.getNumDims() == 4
    assert len(nsfdata_cor.getNonIntegratedDimensions()) == 3

    # dimension 1
    dim_1 = nsfdata_cor.getNonIntegratedDimensions()[0]
    assert dim_1.name == "[H,H,0]"
    assert dim_1.getMDFrame().name() == "HKL"
    assert dim_1.getUnits() == "r.l.u."
    assert dim_1.getMinimum() == approx(0)
    assert dim_1.getMaximum() == approx(1)
    assert dim_1.getBinWidth() == approx(0.05)

    # dimension 2
    dim_2 = nsfdata_cor.getNonIntegratedDimensions()[1]
    assert dim_2.name == "[0,0,L]"
    assert dim_2.getBinWidth() == approx(0.05)

    # dimension 3
    dim_3 = nsfdata_cor.getNonIntegratedDimensions()[2]
    assert dim_3.name == "[-H,H,0]"
    assert dim_3.getBinWidth() == approx(0.05)

    # compare intensities
    sfdata = mtd["sfdata_unpol"]
    nsfdata = mtd["nsfdata_unpol"]

    sfdata_intensities = sfdata.getSignalArray()
    nsfdata_intensities = nsfdata.getSignalArray()

    sfdata_cor_intensities = sfdata_cor.getSignalArray()
    nsfdata_cor_intensities = nsfdata_cor.getSignalArray()

    assert len(sfdata_intensities) == len(sfdata_cor_intensities)
    assert len(nsfdata_intensities) == len(nsfdata_cor_intensities)
    assert len(sfdata_cor_intensities) == len(nsfdata_cor_intensities)

    # check intensities
    for i in range(0, 14):
        for j in range(0, len(sfdata_cor_intensities[i])):
            for k in range(0, len(sfdata_cor_intensities[i][j])):
                assert_allclose(sfdata_cor_intensities[i][j][k], [np.nan])
                assert_allclose(nsfdata_cor_intensities[i][j][k], [np.nan])

    # flipping ratio = 2*20
    # formula for SFc[i] = 40/39*SF[i] - 1/39*NSF[i]
    for i in range(14, len(sfdata_intensities)):
        for j in range(0, len(sfdata_cor_intensities[i])):
            for k in range(0, len(sfdata_cor_intensities[i][j])):
                expected_corr_sf = 40 / 39 * sfdata_intensities[i][j][k] - 1 / 39 * nsfdata_intensities[i][j][k]
                assert_allclose(expected_corr_sf, sfdata_cor_intensities[i][j][k])

    # flipping ratio = 2*20
    # formula for NSFc[i] = 40/39*NSF[i] - 1/39*FSF[i]
    for i in range(14, len(nsfdata_intensities)):
        for j in range(0, len(nsfdata_cor_intensities[i])):
            for k in range(0, len(sfdata_cor_intensities[i][j])):
                expected_corr_nsf = 40 / 39 * nsfdata_intensities[i][j][k] - 1 / 39 * sfdata_intensities[i][j][k]
                assert_allclose(expected_corr_nsf, nsfdata_cor_intensities[i][j][k])

    # Check shiver version is captured in SF workspace history
    makemultipleslices_algo = sfdata_cor.getHistory().getAlgorithmHistory(4)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"

    # Check shiver version is captured in NSF workspace history
    makemultipleslices_algo = nsfdata_cor.getHistory().getAlgorithmHistory(4)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"


def test_make_slices_4d():
    """Test for 4D 'slices'"""

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_SF.nxs"),
        OutputWorkspace="sfdata",
    )

    MakeSlice(
        InputWorkspace="sfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0.5,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="0.5,0.05,1",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,0.05,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="sfdata_unpol",
    )

    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
        OutputWorkspace="nsfdata",
    )

    MakeSlice(
        InputWorkspace="nsfdata",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0.5,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="0.5,0.05,1",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,0.05,1",
        SymmetryOperations="",
        Smoothing=0,
        OutputWorkspace="nsfdata_unpol",
    )

    # call make slice
    MakeSFCorrectedSlices(
        SFInputWorkspace="sfdata",
        NSFInputWorkspace="nsfdata",
        SFOutputWorkspace="out_SF",
        NSFOutputWorkspace="out_NSF",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        QDimension2="0,0,1",
        Dimension0Name="QDimension0",
        Dimension0Binning="0,0.05,1",
        Dimension1Name="QDimension2",
        Dimension1Binning="0.5,0.05,1",
        Dimension2Name="QDimension1",
        Dimension2Binning="0.5,0.05,1",
        Dimension3Name="DeltaE",
        Dimension3Binning="-1,0.05,1",
        SymmetryOperations="",
        Smoothing=0,
        FlippingRatio="2*Ei",
        FlippingRatioSampleLog="Ei",
    )

    # corrected SF
    assert "out_SF" in mtd
    sfdata_cor = mtd["out_SF"]

    assert sfdata_cor.isMDHistoWorkspace()
    assert sfdata_cor.getNumDims() == 4
    assert len(sfdata_cor.getNonIntegratedDimensions()) == 4

    # dimension 1
    dim_1 = sfdata_cor.getNonIntegratedDimensions()[0]
    assert dim_1.name == "[H,H,0]"
    assert dim_1.getMDFrame().name() == "HKL"
    assert dim_1.getUnits() == "r.l.u."
    assert dim_1.getMinimum() == approx(0)
    assert dim_1.getMaximum() == approx(1)
    assert dim_1.getBinWidth() == approx(0.05)

    # dimension 2
    dim_2 = sfdata_cor.getNonIntegratedDimensions()[1]
    assert dim_2.name == "[0,0,L]"
    assert dim_2.getBinWidth() == approx(0.05)

    # dimension 3
    dim_3 = sfdata_cor.getNonIntegratedDimensions()[2]
    assert dim_3.name == "[-H,H,0]"
    assert dim_3.getBinWidth() == approx(0.05)

    # dimension 4
    dim_4 = sfdata_cor.getNonIntegratedDimensions()[3]
    assert dim_4.name == "DeltaE"
    assert dim_4.getBinWidth() == approx(0.05)
    assert dim_4.getMinimum() == approx(-1)
    assert dim_4.getMaximum() == approx(1)

    # corrected NSF
    assert "out_NSF" in mtd
    nsfdata_cor = mtd["out_NSF"]

    assert nsfdata_cor.isMDHistoWorkspace()
    assert nsfdata_cor.getNumDims() == 4
    assert len(nsfdata_cor.getNonIntegratedDimensions()) == 4

    # dimension 1
    dim_1 = nsfdata_cor.getNonIntegratedDimensions()[0]
    assert dim_1.name == "[H,H,0]"
    assert dim_1.getMDFrame().name() == "HKL"
    assert dim_1.getUnits() == "r.l.u."
    assert dim_1.getMinimum() == approx(0)
    assert dim_1.getMaximum() == approx(1)
    assert dim_1.getBinWidth() == approx(0.05)

    # dimension 2
    dim_2 = nsfdata_cor.getNonIntegratedDimensions()[1]
    assert dim_2.name == "[0,0,L]"
    assert dim_2.getBinWidth() == approx(0.05)

    # dimension 3
    dim_3 = nsfdata_cor.getNonIntegratedDimensions()[2]
    assert dim_3.name == "[-H,H,0]"
    assert dim_3.getBinWidth() == approx(0.05)

    # dimension 4
    dim_4 = nsfdata_cor.getNonIntegratedDimensions()[3]
    assert dim_4.name == "DeltaE"
    assert dim_4.getBinWidth() == approx(0.05)
    assert dim_4.getMinimum() == approx(-1)
    assert dim_4.getMaximum() == approx(1)

    # compare intensities
    sfdata = mtd["sfdata_unpol"]
    nsfdata = mtd["nsfdata_unpol"]

    sfdata_intensities = sfdata.getSignalArray()
    nsfdata_intensities = nsfdata.getSignalArray()

    sfdata_cor_intensities = sfdata_cor.getSignalArray()
    nsfdata_cor_intensities = nsfdata_cor.getSignalArray()

    assert len(sfdata_intensities) == len(sfdata_cor_intensities)
    assert len(nsfdata_intensities) == len(nsfdata_cor_intensities)
    assert len(sfdata_cor_intensities) == len(nsfdata_cor_intensities)

    # check intensities
    for dim1 in range(0, 14):
        for dim2 in range(0, len(sfdata_cor_intensities[dim1])):
            for dim3 in range(0, len(sfdata_cor_intensities[dim1][dim2])):
                for dim4 in range(0, len(sfdata_cor_intensities[dim1][dim2][dim3])):
                    assert_allclose(sfdata_cor_intensities[dim1][dim2][dim3][dim4], np.nan)
                    assert_allclose(nsfdata_cor_intensities[dim1][dim2][dim3][dim4], np.nan)

    # flipping ratio = 2*20
    # formula for SFc[i] = 40/39*SF[i] - 1/39*NSF[i]
    for dim1 in range(0, len(sfdata_cor_intensities)):  # pylint: disable=consider-using-enumerate
        for dim2 in range(0, len(sfdata_cor_intensities[dim1])):
            for dim3 in range(0, len(sfdata_cor_intensities[dim1][dim2])):
                for dim4 in range(0, len(sfdata_cor_intensities[dim1][dim2][dim3])):
                    expected_corr_sf = (
                        40 / 39 * sfdata_intensities[dim1][dim2][dim3][dim4]
                        - 1 / 39 * nsfdata_intensities[dim1][dim2][dim3][dim4]
                    )
                    assert_allclose(expected_corr_sf, sfdata_cor_intensities[dim1][dim2][dim3][dim4])

    # flipping ratio = 2*20
    # formula for NSFc[i] = 40/39*NSF[i] - 1/39*FSF[i]
    for dim1 in range(0, len(nsfdata_cor_intensities)):  # pylint: disable=consider-using-enumerate
        for dim2 in range(0, len(nsfdata_cor_intensities[dim1])):
            for dim3 in range(0, len(nsfdata_cor_intensities[dim1][dim2])):
                for dim4 in range(0, len(nsfdata_cor_intensities[dim1][dim2][dim3])):
                    expected_corr_nsf = (
                        40 / 39 * nsfdata_intensities[dim1][dim2][dim3][dim4]
                        - 1 / 39 * sfdata_intensities[dim1][dim2][dim3][dim4]
                    )
                    assert_allclose(expected_corr_nsf, nsfdata_cor_intensities[dim1][dim2][dim3][dim4])

    # Check shiver version is captured in SF workspace history
    makemultipleslices_algo = sfdata_cor.getHistory().getAlgorithmHistory(4)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"

    # Check shiver version is captured in NSF workspace history
    makemultipleslices_algo = nsfdata_cor.getHistory().getAlgorithmHistory(4)
    assert makemultipleslices_algo.name() == "MakeSFCorrectedSlices"
    comment_history = makemultipleslices_algo.getChildAlgorithm(8)
    assert comment_history.name() == "Comment"
    assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"
