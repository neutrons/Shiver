"""Tests for the ConvertDGSToSingleMDE algorithm"""
import os
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    ConvertDGSToSingleMDE,
    MergeMD,
    CompareMDWorkspaces,
    LoadMD,
    LoadEventNexus,
    LoadEmptyInstrument,
    MaskBTP,
)


def test_convert_dgs_to_single_mde_single_qsample():
    """Test for ConvertDGSToSingleMDE"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md1.getNumDims() == 4
    assert md1.getSpecialCoordinateSystem().name == "QSample"
    assert md1.getDimension(0).name == "Q_sample_x"
    assert md1.getDimension(1).name == "Q_sample_y"
    assert md1.getDimension(2).name == "Q_sample_z"
    assert md1.getDimension(3).name == "DeltaE"
    assert md1.getNEvents() == 23682

    # compare to preloaded data
    data = LoadEventNexus(os.path.join(raw_data_folder, "HYS_178921.nxs.h5"))

    md2 = ConvertDGSToSingleMDE(InputWorkspace=data, Ei=25.0, T0=112.0, TimeIndependentBackground="Default")

    assert CompareMDWorkspaces(md1, md2, IgnoreBoxID=True)[0]


def test_convert_dgs_to_single_mde_single_qlab():
    """Test for QFrame=Q_lab option ConvertDGSToSingleMDE"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        QFrame="Q_lab",
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md1.getNumDims() == 4
    assert md1.getSpecialCoordinateSystem().name == "QLab"
    assert md1.getDimension(0).name == "Q_lab_x"
    assert md1.getDimension(1).name == "Q_lab_y"
    assert md1.getDimension(2).name == "Q_lab_z"
    assert md1.getDimension(3).name == "DeltaE"
    assert md1.getNEvents() == 23682


def test_convert_dgs_to_single_mde_mask():
    """Test for MaskWorkspace option ConvertDGSToSingleMDE"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    mask_workspace = LoadEmptyInstrument(InstrumentName="HYSPEC")

    # Mask almost all pixels, final MD should have small number of events
    MaskBTP(mask_workspace, Pixel="1-63,66-128")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        MaskWorkspace=mask_workspace,
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md1.getNEvents() == 415


def test_convert_dgs_to_single_mde_additional_dims():
    """Test for Additional Dimensions option ConvertDGSToSingleMDE"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
        AdditionalDimensions="omega,18,30",
    )

    assert md1.getNumDims() == 5
    assert md1.getSpecialCoordinateSystem().name == "QSample"
    assert md1.getDimension(0).name == "Q_sample_x"
    assert md1.getDimension(1).name == "Q_sample_y"
    assert md1.getDimension(2).name == "Q_sample_z"
    assert md1.getDimension(3).name == "DeltaE"
    assert md1.getDimension(4).name == "omega"
    assert md1.getDimension(4).getMinimum() == 18
    assert md1.getDimension(4).getMaximum() == 30
    assert md1.getNEvents() == 23682


def test_convert_dgs_to_single_mde_merged():
    """Test for merging results and compare to existing data ConvertDGSToSingleMDE"""

    data_files = [
        "HYS_178921.nxs.h5",
        "HYS_178922.nxs.h5",
        "HYS_178923.nxs.h5",
        "HYS_178924.nxs.h5",
        "HYS_178925.nxs.h5",
        "HYS_178926.nxs.h5",
    ]

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    mds = []
    for data_file in data_files:
        mds.append(
            ConvertDGSToSingleMDE(
                Filenames=os.path.join(raw_data_folder, data_file),
                Ei=25.0,
                T0=112.0,
                TimeIndependentBackground="Default",
                OutputWorkspace=data_file,
            )
        )

    merged_md = MergeMD(mds)

    expected_md = LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        )
    )

    assert CompareMDWorkspaces(merged_md, expected_md, Tolerance=1e-5, IgnoreBoxID=True)[0]
