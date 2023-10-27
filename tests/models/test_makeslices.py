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


# def test_make_slices_1d():
#     """Test for 1D line 'slice', 3 dimensions integrated"""

#     LoadMD(
#         Filename=os.path.join(
#             os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
#         ),
#         OutputWorkspace="sfdata",
#     )

#     LoadMD(
#         Filename=os.path.join(
#             os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
#         ),
#         OutputWorkspace="nsfdata",
#     )

#     # call make slice
#     MakeMultipleSlices(
#         SFInputWorkspace="sfdata",
#         NSFInputWorkspace="nsfdata",
#         SFOutputWorkspace="out_SF",
#         NSFOutputWorkspace="out_NSF",
#         BackgroundWorkspace=None,
#         NormalizationWorkspace=None,
#         QDimension0="0,0,1",
#         QDimension1="1,1,0",
#         QDimension2="-1,1,0",
#         Dimension0Name="QDimension1",
#         Dimension0Binning="0.35,0.025,0.65",
#         Dimension1Name="QDimension0",
#         Dimension1Binning="0.45,0.55",
#         Dimension2Name="QDimension2",
#         Dimension2Binning="-0.2,0.2",
#         Dimension3Name="DeltaE",
#         Dimension3Binning="-0.5,0.5",
#         SymmetryOperations="-x,-y,-z",
#         Smoothing=0,
#         FlippingRatio="1",
#     )

#     assert "out_SF" in mtd

#     line = mtd["out_SF"]

#     assert line.isMDHistoWorkspace()
#     assert line.getNumDims() == 4
#     assert len(line.getNonIntegratedDimensions()) == 1

#     dim = line.getNonIntegratedDimensions()[0]
#     assert dim.name == "[H,H,0]"
#     assert dim.getMDFrame().name() == "HKL"
#     assert dim.getUnits() == "r.l.u."
#     assert dim.getMinimum() == approx(0.35)
#     assert dim.getMaximum() == approx(0.65)
#     assert dim.getBinWidth() == approx(0.025)

#     expected = np.array(
#         [
#             [[[np.nan]]],
#             [[[0.0005115540635932]]],
#             [[[0.0056131357337368]]],
#             [[[0.0244047014270163]]],
#             [[[0.1687128573667450]]],
#             [[[0.8971096743581356]]],
#             [[[1.0922733651467396]]],
#             [[[0.1765486119007676]]],
#             [[[0.0121833555862129]]],
#             [[[0.0039449586710785]]],
#             [[[0.0011579777633236]]],
#             [[[0.0007351419622090]]],
#         ]
#     )

#     #assert_allclose(line.getSignalArray(), expected)

#     # Check shiver version is captured in workspace history
#     comment_history = line.getHistory().getAlgorithmHistory(4).getChildAlgorithm(8)
#     assert comment_history.name() == "Comment"
#     assert comment_history.getPropertyValue("text") == f"Shiver version {__version__}"


# # test with normalization workspace
# # create a fake workspace all value 2, output should be halved
# LoadEmptyInstrument(InstrumentName="HYSPEC", DetectorValue=2, OutputWorkspace="norm")

# MakeMultipleSlices(
#     InputWorkspace="data",
#     BackgroundWorkspace=None,
#     NormalizationWorkspace="norm",
#     QDimension0="0,0,1",
#     QDimension1="1,1,0",
#     QDimension2="-1,1,0",
#     Dimension0Name="QDimension1",
#     Dimension0Binning="0.35,0.025,0.65",
#     Dimension1Name="QDimension0",
#     Dimension1Binning="0.45,0.55",
#     Dimension2Name="QDimension2",
#     Dimension2Binning="-0.2,0.2",
#     Dimension3Name="DeltaE",
#     Dimension3Binning="-0.5,0.5",
#     SymmetryOperations=None,
#     Smoothing=1,
#     OutputWorkspace="line_norm",
# )

# assert "line_norm" in mtd

# line_norm = mtd["line_norm"]

# assert_allclose(line_norm.getSignalArray(), expected / 2)

# # test with background
# # clone data as background and scale to 10%, output should be 90% of original
# background = CloneMDWorkspace("data")
# background = background * 0.1

# MakeMultipleSlices(
#     InputWorkspace="data",
#     BackgroundWorkspace="background",
#     NormalizationWorkspace=None,
#     QDimension0="0,0,1",
#     QDimension1="1,1,0",
#     QDimension2="-1,1,0",
#     Dimension0Name="QDimension1",
#     Dimension0Binning="0.35,0.025,0.65",
#     Dimension1Name="QDimension0",
#     Dimension1Binning="0.45,0.55",
#     Dimension2Name="QDimension2",
#     Dimension2Binning="-0.2,0.2",
#     Dimension3Name="DeltaE",
#     Dimension3Binning="-0.5,0.5",
#     SymmetryOperations=None,
#     Smoothing=1,
#     OutputWorkspace="line_bkg",
# )

# assert "line_bkg" in mtd

# line_bkg = mtd["line_bkg"]

# assert_allclose(line_bkg.getSignalArray(), expected * 0.9)

# # test with background and normalization, output should be scaled by 0.9/2
# MakeMultipleSlices(
#     InputWorkspace="data",
#     BackgroundWorkspace="background",
#     NormalizationWorkspace="norm",
#     QDimension0="0,0,1",
#     QDimension1="1,1,0",
#     QDimension2="-1,1,0",
#     Dimension0Name="QDimension1",
#     Dimension0Binning="0.35,0.025,0.65",
#     Dimension1Name="QDimension0",
#     Dimension1Binning="0.45,0.55",
#     Dimension2Name="QDimension2",
#     Dimension2Binning="-0.2,0.2",
#     Dimension3Name="DeltaE",
#     Dimension3Binning="-0.5,0.5",
#     SymmetryOperations=None,
#     Smoothing=1,
#     OutputWorkspace="line_bkg_norm",
# )

# assert "line_bkg_norm" in mtd

# line_bkg_norm = mtd["line_bkg_norm"]

# assert_allclose(line_bkg_norm.getSignalArray(), expected * 0.45)

# # test without smoothing
# MakeMultipleSlices(
#     InputWorkspace="data",
#     BackgroundWorkspace=None,
#     NormalizationWorkspace=None,
#     QDimension0="0,0,1",
#     QDimension1="1,1,0",
#     QDimension2="-1,1,0",
#     Dimension0Name="QDimension1",
#     Dimension0Binning="0.35,0.025,0.65",
#     Dimension1Name="QDimension0",
#     Dimension1Binning="0.45,0.55",
#     Dimension2Name="QDimension2",
#     Dimension2Binning="-0.2,0.2",
#     Dimension3Name="DeltaE",
#     Dimension3Binning="-0.5,0.5",
#     SymmetryOperations=None,
#     Smoothing=0,
#     OutputWorkspace="line_no_smooth",
# )

# assert "line_no_smooth" in mtd

# line_no_smooth = mtd["line_no_smooth"]

# expected_no_smooth = np.array(
#     [
#         [[[np.nan]]],
#         [[[0.0]]],
#         [[[0.0012908131910917]]],
#         [[[0.0184138630158528]]],
#         [[[0.0513475163695748]]],
#         [[[0.9760902879269997]]],
#         [[[1.2731272992006620]]],
#         [[[0.0235049443414310]]],
#         [[[0.0116971832360449]]],
#         [[[0.0026341879092440]]],
#         [[[0.0007270675061297]]],
#         [[[0.0007382233589086]]],
#     ]
# )

# assert_allclose(line_no_smooth.getSignalArray(), expected_no_smooth)

# # test with symmetry
# MakeMultipleSlices(
#     InputWorkspace="data",
#     BackgroundWorkspace=None,
#     NormalizationWorkspace=None,
#     QDimension0="0,0,1",
#     QDimension1="1,1,0",
#     QDimension2="-1,1,0",
#     Dimension0Name="QDimension1",
#     Dimension0Binning="0.35,0.025,0.65",
#     Dimension1Name="QDimension0",
#     Dimension1Binning="0.45,0.55",
#     Dimension2Name="QDimension2",
#     Dimension2Binning="-0.2,0.2",
#     Dimension3Name="DeltaE",
#     Dimension3Binning="-0.5,0.5",
#     SymmetryOperations="-x,-y,-z",
#     Smoothing=1,
#     OutputWorkspace="line_symm",
# )

# assert "line_symm" in mtd

# line_symm = mtd["line_symm"]

# assert_allclose(
#     line_symm.getSignalArray(),
#     np.array(
#         [
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#             [[[np.nan]]],
#         ]
#     ),
# )

# MakeMultipleSlices(
#     InputWorkspace="data",
#     BackgroundWorkspace=None,
#     NormalizationWorkspace=None,
#     QDimension0="0,0,1",
#     QDimension1="1,1,0",
#     QDimension2="-1,1,0",
#     Dimension0Name="QDimension1",
#     Dimension0Binning="-0.65,0.025,-0.35",
#     Dimension1Name="QDimension0",
#     Dimension1Binning="-0.55,-0.45",
#     Dimension2Name="QDimension2",
#     Dimension2Binning="-0.2,0.2",
#     Dimension3Name="DeltaE",
#     Dimension3Binning="-0.5,0.5",
#     SymmetryOperations="-x,-y,-z",
#     Smoothing=1,
#     OutputWorkspace="line_symm2",
# )

# assert "line_symm2" in mtd

# line_symm2 = mtd["line_symm2"]

# assert_allclose(line_symm2.getSignalArray(), expected[::-1])
