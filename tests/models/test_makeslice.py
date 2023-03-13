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
    # pylint: disable=too-many-statements

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
            [[[np.nan]]],
            [[[0.0005115540635932]]],
            [[[0.0056131357337368]]],
            [[[0.0244047014270163]]],
            [[[0.1687128573667450]]],
            [[[0.8971096743581356]]],
            [[[1.0922733651467396]]],
            [[[0.1765486119007676]]],
            [[[0.0121833555862129]]],
            [[[0.0039449586710785]]],
            [[[0.0011579777633236]]],
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
        Dimension1Binning="0.45,0.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="line_norm",
    )

    assert "line_norm" in mtd

    line_norm = mtd["line_norm"]

    assert_allclose(line_norm.getSignalArray(), expected / 2)

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
        Dimension1Binning="0.45,0.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="line_bkg",
    )

    assert "line_bkg" in mtd

    line_bkg = mtd["line_bkg"]

    assert_allclose(line_bkg.getSignalArray(), expected * 0.9)

    # test with background and normalization, output should be scaled by 0.9/2
    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace="background",
        NormalizationWorkspace="norm",
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
        OutputWorkspace="line_bkg_norm",
    )

    assert "line_bkg_norm" in mtd

    line_bkg_norm = mtd["line_bkg_norm"]

    assert_allclose(line_bkg_norm.getSignalArray(), expected * 0.45)

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
        Dimension1Binning="0.45,0.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=0,
        OutputWorkspace="line_no_smooth",
    )

    assert "line_no_smooth" in mtd

    line_no_smooth = mtd["line_no_smooth"]

    expected_no_smooth = np.array(
        [
            [[[np.nan]]],
            [[[0.0]]],
            [[[0.0012908131910917]]],
            [[[0.0184138630158528]]],
            [[[0.0513475163695748]]],
            [[[0.9760902879269997]]],
            [[[1.2731272992006620]]],
            [[[0.0235049443414310]]],
            [[[0.0116971832360449]]],
            [[[0.0026341879092440]]],
            [[[0.0007270675061297]]],
            [[[0.0007382233589086]]],
        ]
    )

    assert_allclose(line_no_smooth.getSignalArray(), expected_no_smooth)

    # test with symmetry
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
        SymmetryOperations="-x,-y,-z",
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="line_symm",
    )

    assert "line_symm" in mtd

    line_symm = mtd["line_symm"]

    assert_allclose(
        line_symm.getSignalArray(),
        np.array(
            [
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
                [[[np.nan]]],
            ]
        ),
    )

    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="0,0,1",
        QDimension1="1,1,0",
        QDimension2="-1,1,0",
        Dimension0Name="QDimension1",
        Dimension0Binning="-0.65,0.025,-0.35",
        Dimension1Name="QDimension0",
        Dimension1Binning="-0.55,-0.45",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations="-x,-y,-z",
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="line_symm2",
    )

    assert "line_symm2" in mtd

    line_symm2 = mtd["line_symm2"]

    assert_allclose(line_symm2.getSignalArray(), expected[::-1])

    # test with convert_to_chi

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
        ConvertToChi=True,
        Temperature="sampletemp",
        Smoothing=1,
        OutputWorkspace="line_chi",
    )

    assert "line_chi" in mtd

    line_chi = mtd["line_chi"]

    expected_chi = np.array(
        [
            [[[np.nan]]],
            [[[-0.0003410174177501]]],
            [[[-0.0041780866838251]]],
            [[[-0.0335066160473299]]],
            [[[-0.2074643240427706]]],
            [[[-1.1402017587161484]]],
            [[[-3.1845498759730370]]],
            [[[-0.5757032090829151]]],
            [[[-0.0456650391806099]]],
            [[[-0.0148084317545845]]],
            [[[-0.0044824469148584]]],
            [[[-0.0023850718016570]]],
        ]
    )

    assert_allclose(line_chi.getSignalArray(), expected_chi)

    # test with convert_to_chi with background

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
        Dimension1Binning="0.45,0.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        ConvertToChi=True,
        Temperature="sampletemp",
        Smoothing=1,
        OutputWorkspace="line_chi_bkg",
    )

    assert "line_chi_bkg" in mtd

    line_chi_bkg = mtd["line_chi_bkg"]

    assert_allclose(line_chi_bkg.getSignalArray(), expected_chi * 0.9)


def test_make_slice_1d_inelastic():
    """Test for 1D line 'slice', 3 dimensions integrated with E!=0"""
    # pylint: disable=too-many-statements

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

    # E = 10
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
        Dimension1Binning="1.45,1.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="9.5,10.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="e10",
    )

    assert "e10" in mtd

    e10 = mtd["e10"]

    assert e10.isMDHistoWorkspace()
    assert e10.getNumDims() == 4
    assert len(e10.getNonIntegratedDimensions()) == 1

    dim = e10.getNonIntegratedDimensions()[0]
    assert dim.name == "[H,H,0]"
    assert dim.getMDFrame().name() == "HKL"
    assert dim.getUnits() == "r.l.u."
    assert dim.getMinimum() == approx(0.35)
    assert dim.getMaximum() == approx(0.65)
    assert dim.getBinWidth() == approx(0.025)

    expected = np.array(
        [
            [[[np.nan]]],
            [[[0.0014925674830340]]],
            [[[0.0032956696169066]]],
            [[[0.0073789915807166]]],
            [[[0.0106991719811672]]],
            [[[0.0098476515556289]]],
            [[[0.0078020659963413]]],
            [[[0.0078515947978436]]],
            [[[0.0072551860463859]]],
            [[[0.0051514132207535]]],
            [[[0.0029495986513100]]],
            [[[0.0013921775501808]]],
        ]
    )

    assert_allclose(e10.getSignalArray(), expected)

    # cut along E
    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="0,0,1",
        QDimension1="1,1,0",
        QDimension2="-1,1,0",
        Dimension0Name="DeltaE",
        Dimension0Binning="5,0.5,14",
        Dimension1Name="QDimension0",
        Dimension1Binning="1.3,1.7",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="QDimension1",
        Dimension3Binning="0.4,0.6",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="energy",
    )

    assert "energy" in mtd

    energy = mtd["energy"]

    assert energy.isMDHistoWorkspace()
    assert energy.getNumDims() == 4
    assert len(energy.getNonIntegratedDimensions()) == 1

    dim = energy.getNonIntegratedDimensions()[0]
    assert dim.name == "DeltaE"
    assert dim.getMDFrame().name() == "General Frame"
    assert dim.getUnits() == "DeltaE"
    assert dim.getMinimum() == approx(5)
    assert dim.getMaximum() == approx(14)
    assert dim.getBinWidth() == approx(0.5)

    expected = np.array(
        [
            [[[0.0001063926896827]]],
            [[[0.0002430199916913]]],
            [[[0.0003243146883928]]],
            [[[0.0005568162777679]]],
            [[[0.0009443520466246]]],
            [[[0.0014776476257624]]],
            [[[0.0018410791397010]]],
            [[[0.0026529832595533]]],
            [[[0.0040571146468762]]],
            [[[0.0057050928676846]]],
            [[[0.0065588709411226]]],
            [[[0.0065520938603378]]],
            [[[0.0052155014154480]]],
            [[[0.0034597123411606]]],
            [[[0.0027681145241323]]],
            [[[0.0022589059732835]]],
            [[[0.0021508136359628]]],
            [[[0.0020929087481173]]],
        ]
    )

    assert_allclose(energy.getSignalArray(), expected)


def test_2d_slice():
    """Test for 2D slice, 3 dimensions integrated"""
    # pylint: disable=too-many-statements

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

    # E = 0
    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="0,0,1",
        QDimension1="1,1,0",
        QDimension2="-1,1,0",
        Dimension0Name="QDimension1",
        Dimension0Binning="0.3,0.05,0.7",
        Dimension1Name="QDimension0",
        Dimension1Binning="0.3,0.05,0.7",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="slice_e0",
    )

    assert "slice_e0" in mtd

    slice_e0 = mtd["slice_e0"]

    assert slice_e0.isMDHistoWorkspace()
    assert slice_e0.getNumDims() == 4
    assert len(slice_e0.getNonIntegratedDimensions()) == 2

    dim = slice_e0.getNonIntegratedDimensions()[0]
    assert dim.name == "[H,H,0]"
    assert dim.getMDFrame().name() == "HKL"
    assert dim.getUnits() == "r.l.u."
    assert dim.getMinimum() == approx(0.3)
    assert dim.getMaximum() == approx(0.7)
    assert dim.getBinWidth() == approx(0.05)

    dim2 = slice_e0.getNonIntegratedDimensions()[1]
    assert dim2.name == "[0,0,L]"
    assert dim2.getMDFrame().name() == "HKL"
    assert dim2.getUnits() == "r.l.u."
    assert dim2.getMinimum() == approx(0.3)
    assert dim2.getMaximum() == approx(0.7)
    assert dim2.getBinWidth() == approx(0.05)

    expected = np.array(
        [
            [7.62560780e-04, 5.41023451e-04, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [9.17930724e-04, 1.09860963e-03, 1.37861343e-03, np.nan, np.nan, np.nan, np.nan, np.nan],
            [8.90772389e-04, 1.58530559e-03, 1.21628651e-02, 1.13745225e-01, 1.76704506e-01, np.nan, np.nan, np.nan],
            [
                1.11814903e-03,
                2.62303099e-03,
                7.90642277e-02,
                4.83081964e-01,
                4.42949757e-01,
                1.13931227e-01,
                6.24787511e-03,
                8.82772649e-04,
            ],
            [
                np.nan,
                np.nan,
                1.14207148e-01,
                6.03935811e-01,
                4.13801979e-01,
                5.77595046e-02,
                2.13964440e-03,
                7.26072265e-04,
            ],
            [np.nan, np.nan, np.nan, 1.25611364e-01, 6.41820014e-02, 9.93853957e-03, 1.63353197e-03, 9.31341426e-04],
            [np.nan, np.nan, np.nan, np.nan, 1.89748505e-03, 7.06069241e-04, 6.96099392e-04, 9.16674070e-04],
            [np.nan, np.nan, np.nan, np.nan, np.nan, 3.50431039e-04, 4.64391818e-04, 3.78890446e-04],
        ]
    )

    assert_allclose(slice_e0.getSignalArray().reshape((8, 8)), expected)

    # E = 10

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
        Dimension0Binning="0.3,0.05,0.7",
        Dimension1Name="QDimension0",
        Dimension1Binning="1.3,0.05,1.7",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="9.5,10.5",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="slice_e10",
    )

    assert "slice_e10" in mtd

    slice_e10 = mtd["slice_e10"]
    expected = np.array(
        [
            [0.00091451, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
            [0.00224435, 0.00319354, 0.0035866, 0.00344467, np.nan, np.nan, np.nan, np.nan],
            [0.00677898, 0.00977085, 0.00952857, 0.00717062, 0.00459069, 0.00233638, 0.00087981, 0.00018298],
            [0.00566341, 0.00900532, 0.01054974, 0.01006237, 0.00914189, 0.00691898, 0.00306066, 0.00081886],
            [0.00313092, 0.00588142, 0.00746063, 0.00777164, 0.00808489, 0.0085549, 0.00699807, 0.0034368],
            [0.00161906, 0.0027532, 0.00411434, 0.00539882, 0.00660891, 0.00748112, 0.0064838, 0.00271017],
            [0.00080522, 0.000943, 0.0014565, 0.00241518, 0.00266692, 0.00341086, 0.00291548, 0.00193296],
            [np.nan, np.nan, np.nan, 0.00104916, 0.00097631, 0.00108881, 0.00090306, 0.00089699],
        ]
    )

    assert_allclose(slice_e10.getSignalArray().reshape((8, 8)), expected, atol=1e-8)

    # slice ΔE vs [0,0,L]

    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="0,0,1",
        QDimension1="1,1,0",
        QDimension2="-1,1,0",
        Dimension0Name="QDimension0",
        Dimension0Binning="1,0.1,2",
        Dimension1Name="DeltaE",
        Dimension1Binning="7,1,15",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="QDimension1",
        Dimension3Binning="0.4,0.6",
        SymmetryOperations=None,
        ConvertToChi=False,
        Temperature=None,
        Smoothing=1,
        OutputWorkspace="slice_dE_vs_L",
    )

    assert "slice_dE_vs_L" in mtd

    slice_de_vs_l = mtd["slice_dE_vs_L"]

    assert slice_de_vs_l.isMDHistoWorkspace()
    assert slice_de_vs_l.getNumDims() == 4
    assert len(slice_de_vs_l.getNonIntegratedDimensions()) == 2

    dim = slice_de_vs_l.getNonIntegratedDimensions()[0]
    assert dim.name == "[0,0,L]"
    assert dim.getMDFrame().name() == "HKL"
    assert dim.getUnits() == "r.l.u."
    assert dim.getMinimum() == approx(1)
    assert dim.getMaximum() == approx(2)
    assert dim.getBinWidth() == approx(0.1)

    dim2 = slice_de_vs_l.getNonIntegratedDimensions()[1]
    assert dim2.name == "DeltaE"
    assert dim2.getMDFrame().name() == "General Frame"
    assert dim2.getUnits() == "DeltaE"
    assert dim2.getMinimum() == approx(7)
    assert dim2.getMaximum() == approx(15)
    assert dim2.getBinWidth() == approx(1)

    expected = np.array(
        [
            [8.82936605e-05, 8.64150215e-05, 3.41138142e-04, 1.50664228e-03, np.nan, np.nan, np.nan, np.nan],
            [9.12506312e-05, 1.05504326e-04, 3.94564072e-04, 2.02050599e-03, 5.36622465e-03, np.nan, np.nan, np.nan],
            [2.39997212e-04, 4.76932493e-04, 1.21635999e-03, 3.65897576e-03, 6.62008691e-03, np.nan, np.nan, np.nan],
            [
                8.21421151e-04,
                1.75229910e-03,
                3.82216645e-03,
                6.46048323e-03,
                5.54859139e-03,
                2.74146130e-03,
                np.nan,
                np.nan,
            ],
            [
                1.83856043e-03,
                3.31636365e-03,
                6.24175996e-03,
                7.27226496e-03,
                4.23311041e-03,
                1.92196746e-03,
                1.09746959e-03,
                1.27714172e-03,
            ],
            [
                2.15787400e-03,
                3.35905557e-03,
                5.97020282e-03,
                6.36500233e-03,
                4.17442088e-03,
                2.68992245e-03,
                1.97803754e-03,
                1.84551510e-03,
            ],
            [
                7.08046148e-04,
                1.31869117e-03,
                2.72866430e-03,
                3.90941954e-03,
                3.84056534e-03,
                3.33494832e-03,
                3.03152697e-03,
                2.48929317e-03,
            ],
            [
                5.71909216e-05,
                1.81203830e-04,
                4.85686941e-04,
                1.31530887e-03,
                2.29633791e-03,
                2.46292605e-03,
                2.63212109e-03,
                2.23801882e-03,
            ],
            [
                1.91779722e-05,
                1.78224960e-05,
                1.27647519e-04,
                6.41167644e-04,
                1.39753118e-03,
                1.45241847e-03,
                1.71145259e-03,
                1.51160393e-03,
            ],
            [
                9.36588435e-06,
                2.44429521e-05,
                1.07087262e-04,
                4.67674983e-04,
                1.08412113e-03,
                7.74248217e-04,
                7.63332508e-04,
                6.46029453e-04,
            ],
        ]
    )

    assert_allclose(slice_de_vs_l.getSignalArray().reshape((10, 8)), expected)
