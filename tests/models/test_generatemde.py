"""Tests for the ConvertDGSToSingleMDE algorithm"""

import os

import pytest
import tempfile
# Need to import the new algorithms so they are registered with mantid
import shiver.models.convert_dgs_to_single_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
import shiver.models.generate_dgs_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
from mantid.kernel import amend_config
from mantid.simpleapi import (  # pylint: disable=no-name-in-module, ungrouped-imports
    AddTimeSeriesLog,
    CompareMDWorkspaces,
    ConfigService,
    ConvertDGSToSingleMDE,
    ConvertToMD,
    ConvertToMDMinMaxGlobal,
    CropWorkspace,
    DgsReduction,
    FilterByLogValue,
    GenerateDGSMDE,
    GetEiT0atSNS,
    LoadEmptyInstrument,
    LoadEventNexus,
    LoadMD,
    LoadNexusMonitors,
    MaskBTP,
    MergeMD,
    SaveNexus,
    SetGoniometer,
    SetUB,
    mtd,
)
from pytest import approx, raises

# Need to import the new algorithms so they are registered with mantid
import shiver.models.convert_dgs_to_single_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
import shiver.models.generate_dgs_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.parameters]
        keep_logs = True
        additional_logs =
    """
    ],
    indirect=True,
)
def test_convert_dgs_to_single_mde_config_all_logs(monkeypatch, user_conf_file_with_version):
    """test configuration for logs - all logs"""
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)
    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )
    assert len(md1.getExperimentInfo(0).run().keys()) == 60


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.parameters]
        keep_logs = False
        additional_logs =
    """
    ],
    indirect=True,
)
def test_convert_dgs_to_single_mde_config_necessary_logs(monkeypatch, user_conf_file_with_version):
    """test configuration for logs - all logs"""
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)
    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )
    assert len(md1.getExperimentInfo(0).run().keys()) == 28


@pytest.mark.parametrize(
    "user_conf_file_with_version",
    [
        """
        [generate_tab.parameters]
        keep_logs = False
        additional_logs =
    """
    ],
    indirect=True,
)
def test_convert_dgs_to_single_mde_config_additional(monkeypatch, user_conf_file_with_version):
    """test configuration for logs - all logs"""
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file_with_version)
    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
        AdditionalDimensions="FermiSpeed, 200, 400",
        OmegaMotorName="SensorA",
    )
    # There should be 28 by default (as in previous test) plus SensorA and FermiSpeed
    assert len(md1.getExperimentInfo(0).run().keys()) == 30


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
    assert md1.getExperimentInfo(0).run()["CalculatedT0"].value == 112
    assert md1.getExperimentInfo(0).run()["Ei"].value == 25

    # compare to preloaded data
    data = LoadEventNexus(os.path.join(raw_data_folder, "HYS_178921.nxs.h5"))

    md2 = ConvertDGSToSingleMDE(InputWorkspace=data, Ei=25.0, T0=112.0, TimeIndependentBackground="Default")

    assert CompareMDWorkspaces(md1, md2, IgnoreBoxID=True)[0]


def test_convert_dgs_to_single_pause():
    """Test for correctly handling pause"""
    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    data = LoadEventNexus(os.path.join(raw_data_folder, "HYS_178921.nxs.h5"))
    AddTimeSeriesLog(Workspace=data, Name="pause", Time="2017-11-02T01:48:58.543570666", Value=1, Type="int")
    md_p = ConvertDGSToSingleMDE(InputWorkspace=data, Ei=25.0, T0=112.0, TimeIndependentBackground="Default")
    assert md_p.getNEvents() == 6140  # the original mde has 23682 events


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


def test_convert_dgs_to_single_mde_mask_single_quotes():
    """Test for MaskWorkspace option ConvertDGSToSingleMDE with single-quouted pixels"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    # custom mask
    md1 = GenerateDGSMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        MaskInputs="[{'Bank': '1', 'Tube': '1', 'Pixel': '1-8'}]",
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md1.getNEvents() == 24750


def test_convert_dgs_to_single_mde_mask_empty():
    """Test for MaskInputs empty option ConvertDGSToSingleMDE"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    # custom mask
    md1 = GenerateDGSMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        MaskInputs='[{"Bank": "1", "Tube": "1", "Pixel": "1"}]',
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md1.getNEvents() == 24750

    # implicit mask in the algorithm first and last 8 pixels in each tube
    md2 = GenerateDGSMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        MaskInputs="[]",
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md2.getNEvents() == 23682

    # explicit mask in the algorithm first and last 8 pixels in each tube
    md3 = GenerateDGSMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        MaskInputs='[{"Bank": "", "Tube": "", "Pixel": "1-8,121-128"}]',
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    assert md3.getNEvents() == md2.getNEvents()


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


def test_convert_dgs_to_single_mde_calculate_t0_ei():
    """Test for ConvertDGSToSingleMDE"""

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    md1 = ConvertDGSToSingleMDE(
        Filenames=os.path.join(raw_data_folder, "HYS_178921.nxs.h5"),
        TimeIndependentBackground="Default",
    )

    assert md1.getNumDims() == 4
    assert md1.getSpecialCoordinateSystem().name == "QSample"
    assert md1.getDimension(0).name == "Q_sample_x"
    assert md1.getDimension(1).name == "Q_sample_y"
    assert md1.getDimension(2).name == "Q_sample_z"
    assert md1.getDimension(3).name == "DeltaE"
    assert md1.getNEvents() == 23681

    assert md1.getExperimentInfo(0).run()["CalculatedT0"].value == approx(74.187533)
    assert md1.getExperimentInfo(0).run()["Ei"].value == 25


def test_convert_dgs_to_single_mde_facility():
    """Test for ConvertDGSToSingleMDE facility"""

    with amend_config(facility="HFIR"):
        facility = ConfigService.getFacility().name()
        assert facility == "HFIR"
        data_files = [
            "HYS_178921.nxs.h5",
            "HYS_178922.nxs.h5",
            "HYS_178923.nxs.h5",
            "HYS_178924.nxs.h5",
            "HYS_178925.nxs.h5",
            "HYS_178926.nxs.h5",
        ]

        raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

        _ = GenerateDGSMDE(
            Filenames=",".join(os.path.join(raw_data_folder, data_file) for data_file in data_files),
            Ei=25.0,
            T0=112.0,
            TimeIndependentBackground="Default",
        )
        assert ConfigService.getFacility().name() == "HFIR"


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


def test_generate_dgs_mde():
    """Test results compared to existing data from GenerateDGSMDE"""

    data_files = [
        "HYS_178921.nxs.h5",
        "HYS_178922.nxs.h5",
        "HYS_178923.nxs.h5",
        "HYS_178924.nxs.h5",
        "HYS_178925.nxs.h5",
        "HYS_178926.nxs.h5",
    ]

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    result_md = GenerateDGSMDE(
        Filenames=",".join(os.path.join(raw_data_folder, data_file) for data_file in data_files),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
    )

    expected_md = LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        )
    )

    # Compare to expected workspace
    assert CompareMDWorkspaces(result_md, expected_md, Tolerance=1e-5, IgnoreBoxID=True)[0]


def test_generate_dgs_mde_bkg():
    """Test background generation using GenerateDGSMDE"""

    result_md = GenerateDGSMDE(
        Filenames=os.path.join(os.path.dirname(__file__), "../data/raw", "HYS_178921.nxs.h5"),
        Ei=25.0,
        T0=112.0,
        TimeIndependentBackground="Default",
        Type="Background (angle integrated)",
    )

    assert result_md.getNumDims() == 4
    assert result_md.getSpecialCoordinateSystem().name == "QLab"
    assert result_md.getDimension(0).name == "Q_lab_x"
    assert result_md.getDimension(1).name == "Q_lab_y"
    assert result_md.getDimension(2).name == "Q_lab_z"
    assert result_md.getDimension(3).name == "DeltaE"
    assert result_md.getNEvents() == 23682

def test_use_mask_norm():
    """Use mask file or normalization file"""
    datafile = os.path.join(os.path.dirname(__file__), "../data/raw", "SEQ_124735.nxs.h5")

    # Reduce data using GenerateDGSMDE
    GenerateDGSMDE(
        Filenames=datafile,
        OmegaMotorName="phi",
        EMin=-17.5,
        EMax=31.5,
        UBParameters="{'a':'4.48', 'b':'4.48', 'c':'10.8', 'v':'0,0,1'}",
        MaskInputs="["
        '{"Pixel": "1-7,122-128"},'
        '{"Bank": "114,115,75,76,38,39"},'
        '{"Bank": "88", "Tube": "2-4", "Pixel": "30-35"},'
        '{"Bank": "127", "Tube": "7-8", "Pixel": "99-128"},'
        '{"Bank": "99-102"},'
        '{"Bank": "38-42", "Pixel": "120-128"},'
        '{"Bank": "43", "Pixel": "119-128"},'
        '{"Bank": "44-48", "Pixel": "120-128"},'
        '{"Bank": "74", "Tube": "8"},'
        '{"Bank": "96", "Tube": "8"},'
        '{"Bank": "130-132", "Pixel": "113-128"},'
        '{"Bank": "148", "Tube": "4"},'
        '{"Bank": "46", "Tube": "6-8", "Pixel": "105-110"}'
        "]",
        OutputWorkspace="result_explicit_mask_md",
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        mask_file =  os.path.join(tmpdirname, "test_mask.nxs")

        # Generate mask
        LoadEventNexus(Filename=datafile, OutputWorkspace="data")
        SetGoniometer(Workspace="data", Axis0="phi,0,1,0,1")
        SetUB(Workspace="data", a="4.48", b="4.48", c="10.8", v="0,0,1")
        MaskBTP(Workspace="data", Pixel="1-7,122-128")
        MaskBTP(Workspace="data", Bank="114,115,75,76,38,39")
        MaskBTP(Workspace="data", Bank="88", Tube="2-4", Pixel="30-35")
        MaskBTP(Workspace="data", Bank="127", Tube="7-8", Pixel="99-128")
        MaskBTP(Workspace="data", Bank="99-102")
        MaskBTP(Workspace="data", Bank="38-42", Pixel="120-128")
        MaskBTP(Workspace="data", Bank="43", Pixel="119-128")
        MaskBTP(Workspace="data", Bank="44-48", Pixel="120-128")
        MaskBTP(Workspace="data", Bank="74", Tube="8")
        MaskBTP(Workspace="data", Bank="96", Tube="8")
        MaskBTP(Workspace="data", Bank="130-132", Pixel="113-128")
        MaskBTP(Workspace="data", Bank="148", Tube="4")
        MaskBTP(Workspace="data", Bank="46", Tube="6-8", Pixel="105-110")

        SaveNexus(InputWorkspace="data", Filename=mask_file)

        # Reduce data using GenerateDGSMDE
        GenerateDGSMDE(
            Filenames=datafile,
            OmegaMotorName="phi",
            EMin=-17.5,
            EMax=31.5,
            UBParameters="{'a':'4.48', 'b':'4.48', 'c':'10.8', 'v':'0,0,1'}",
            MaskFilename=mask_file,
            OutputWorkspace="result_mask_filename_md",
        )
        GenerateDGSMDE(
            Filenames=datafile,
            OmegaMotorName="phi",
            EMin=-17.5,
            EMax=31.5,
            UBParameters="{'a':'4.48', 'b':'4.48', 'c':'10.8', 'v':'0,0,1'}",
            NormFilename=mask_file,
            OutputWorkspace="result_norm_filename_md",
        )

    # Compare to expected workspace
    assert CompareMDWorkspaces("result_explicit_mask_md", "result_norm_filename_md", IgnoreBoxID=True)[0]


def test_generate_dgs_mde_seq():
    """Compare manual sequoia reduction with GenerateDGSMDE"""

    datafile = os.path.join(os.path.dirname(__file__), "../data/raw", "SEQ_124735.nxs.h5")

    # Manual data reduction
    LoadEventNexus(Filename=datafile, OutputWorkspace="data")
    SetGoniometer(Workspace="data", Axis0="phi,0,1,0,1")
    SetUB(Workspace="data", a="4.48", b="4.48", c="10.8", v="0,0,1")
    MaskBTP(Workspace="data", Pixel="1-7,122-128")
    MaskBTP(Workspace="data", Bank="114,115,75,76,38,39")
    MaskBTP(Workspace="data", Bank="88", Tube="2-4", Pixel="30-35")
    MaskBTP(Workspace="data", Bank="127", Tube="7-8", Pixel="99-128")
    MaskBTP(Workspace="data", Bank="99-102")
    MaskBTP(Workspace="data", Bank="38-42", Pixel="120-128")
    MaskBTP(Workspace="data", Bank="43", Pixel="119-128")
    MaskBTP(Workspace="data", Bank="44-48", Pixel="120-128")
    MaskBTP(Workspace="data", Bank="74", Tube="8")
    MaskBTP(Workspace="data", Bank="96", Tube="8")
    MaskBTP(Workspace="data", Bank="130-132", Pixel="113-128")
    MaskBTP(Workspace="data", Bank="148", Tube="4")
    MaskBTP(Workspace="data", Bank="46", Tube="6-8", Pixel="105-110")

    FilterByLogValue(InputWorkspace="data", LogName="pause", MinimumValue=-1, MaximumValue=0.5, OutputWorkspace="data")

    LoadNexusMonitors(Filename=datafile, OutputWorkspace="__MonWS")
    e_i, t_0 = GetEiT0atSNS(MonitorWorkspace="__MonWS", IncidentEnergyGuess="35")
    with amend_config(facility="SNS"):
        DgsReduction(
            SampleInputWorkspace="data",
            SampleInputMonitorWorkspace="__MonWS",
            IncidentEnergyGuess=e_i,
            UseIncidentEnergyGuess=True,
            TimeZeroGuess=t_0,
            EnergyTransferRange="-17.5,1,31.5",
            SofPhiEIsDistribution=False,
            OutputWorkspace="dgs",
        )
    CropWorkspace(InputWorkspace="dgs", OutputWorkspace="dgs", XMin="-17.5", XMax="31.5")
    min_values, max_values = ConvertToMDMinMaxGlobal(
        InputWorkspace="dgs", QDimensions="Q3D", dEAnalysisMode="Direct", Q3DFrames="Q"
    )

    ConvertToMD(
        InputWorkspace="dgs",
        QDimensions="Q3D",
        dEAnalysisMode="Direct",
        Q3DFrames="Q_sample",
        MinValues=min_values,
        MaxValues=max_values,
        MaxRecursionDepth=2,
        OutputWorkspace="expected_md",
    )

    # Reduce data using GenerateDGSMDE
    GenerateDGSMDE(
        Filenames=datafile,
        OmegaMotorName="phi",
        EMin=-17.5,
        EMax=31.5,
        UBParameters="{'a':'4.48', 'b':'4.48', 'c':'10.8', 'v':'0,0,1'}",
        MaskInputs="["
        '{"Pixel": "1-7,122-128"},'
        '{"Bank": "114,115,75,76,38,39"},'
        '{"Bank": "88", "Tube": "2-4", "Pixel": "30-35"},'
        '{"Bank": "127", "Tube": "7-8", "Pixel": "99-128"},'
        '{"Bank": "99-102"},'
        '{"Bank": "38-42", "Pixel": "120-128"},'
        '{"Bank": "43", "Pixel": "119-128"},'
        '{"Bank": "44-48", "Pixel": "120-128"},'
        '{"Bank": "74", "Tube": "8"},'
        '{"Bank": "96", "Tube": "8"},'
        '{"Bank": "130-132", "Pixel": "113-128"},'
        '{"Bank": "148", "Tube": "4"},'
        '{"Bank": "46", "Tube": "6-8", "Pixel": "105-110"}'
        "]",
        OutputWorkspace="result_md",
    )

    # Compare to expected workspace
    assert CompareMDWorkspaces("result_md", "expected_md", IgnoreBoxID=True)[0]


def test_generate_dgs_mde_bkg_minimized():
    """Test background (minimized by angle and energy) generation using GenerateDGSMDE"""

    data_files = [
        "HYS_178921.nxs.h5",
        "HYS_178922.nxs.h5",
        "HYS_178923.nxs.h5",
        "HYS_178924.nxs.h5",
        "HYS_178925.nxs.h5",
        "HYS_178926.nxs.h5",
    ]

    raw_data_folder = os.path.join(os.path.dirname(__file__), "../data/raw")

    # check for missing grouping file
    with raises(RuntimeError) as excinfo:
        bkg_md = GenerateDGSMDE(
            Filenames=",".join(os.path.join(raw_data_folder, data_file) for data_file in data_files),
            Type="Background (minimized by angle and energy)",
        )

    assert "A grouping file is required when for 'Background (minimized by angle and energy)'" in str(excinfo.value)

    bkg_md = GenerateDGSMDE(
        Filenames=",".join(os.path.join(raw_data_folder, data_file) for data_file in data_files),
        DetectorGroupingFile=os.path.join(os.path.dirname(__file__), "../data/HYS_groups.xml"),
        Ei=25.0,
        T0=112.0,
        Type="Background (minimized by angle and energy)",
    )

    assert bkg_md.getNumDims() == 4
    assert bkg_md.getSpecialCoordinateSystem().name == "QLab"
    assert bkg_md.getDimension(0).name == "Q_lab_x"
    assert bkg_md.getDimension(1).name == "Q_lab_y"
    assert bkg_md.getDimension(2).name == "Q_lab_z"
    assert bkg_md.getDimension(3).name == "DeltaE"
    assert bkg_md.getNEvents() == 6655

    # this time don't provide Ei and T0, will get slightly different number of events due to different T0 found
    bkg_md = GenerateDGSMDE(
        Filenames=",".join(os.path.join(raw_data_folder, data_file) for data_file in data_files),
        DetectorGroupingFile=os.path.join(os.path.dirname(__file__), "../data/HYS_groups.xml"),
        Type="Background (minimized by angle and energy)",
    )

    assert bkg_md.getNumDims() == 4
    assert bkg_md.getSpecialCoordinateSystem().name == "QLab"
    assert bkg_md.getDimension(0).name == "Q_lab_x"
    assert bkg_md.getDimension(1).name == "Q_lab_y"
    assert bkg_md.getDimension(2).name == "Q_lab_z"
    assert bkg_md.getDimension(3).name == "DeltaE"
    assert bkg_md.getNEvents() == 6738

    # Do top 20% intensity
    bkg_md = GenerateDGSMDE(
        Filenames=",".join(os.path.join(raw_data_folder, data_file) for data_file in data_files),
        DetectorGroupingFile=os.path.join(os.path.dirname(__file__), "../data/HYS_groups.xml"),
        Type="Background (minimized by angle and energy)",
        PercentMin=80,
        PercentMax=100,
    )

    assert bkg_md.getNumDims() == 4
    assert bkg_md.getSpecialCoordinateSystem().name == "QLab"
    assert bkg_md.getDimension(0).name == "Q_lab_x"
    assert bkg_md.getDimension(1).name == "Q_lab_y"
    assert bkg_md.getDimension(2).name == "Q_lab_z"
    assert bkg_md.getDimension(3).name == "DeltaE"
    assert bkg_md.getNEvents() == 576992
