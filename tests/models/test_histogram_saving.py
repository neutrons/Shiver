"""Test the histogram workspace saving"""
# pylint: disable=too-many-lines
import os
import ast
import h5py
import pytest
from pytest import approx

# Need to import the new algorithms so they are registered with mantid
import shiver.models.makeslice  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    CreateMDHistoWorkspace,
    CompareMDWorkspaces,
    LoadMD,
    mtd,
    AddSampleLog,
    MakeSlice,
)

from shiver.models.histogram import HistogramModel
from shiver.models.polarized import PolarizedModel
from shiver.views.polarized_options import PolarizedView
from shiver.presenters.polarized import PolarizedPresenter


def test_saving(tmp_path):
    """Test the file saving and history saving in the histogram model"""

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace="test_workspace",
    )

    model = HistogramModel()

    model.save("test_workspace", str(tmp_path / "test_workspace.nxs"))
    model.save_history("test_workspace", str(tmp_path / "test_workspace.py"))

    # Compare MD to loaded file
    load_md = LoadMD(str(tmp_path / "test_workspace.nxs"))
    assert CompareMDWorkspaces("test_workspace", load_md)[0]

    # Compare python script
    with open(tmp_path / "test_workspace.py", encoding="utf-8") as f_open:
        lines = f_open.readlines()

    assert len(lines) == 12
    assert lines[0] == "import shiver\n"
    assert lines[1] == "from mantid.simpleapi import CreateMDHistoWorkspace\n"
    assert (
        " ".join([line.strip() for line in lines[4:]]) == 'CreateMDHistoWorkspace(SignalInput="2,3", ErrorInput="1,1", '
        'Dimensionality="1", Extents="-2,2", NumberOfBins="2", Names="A", Units="a", OutputWorkspace="test_workspace")'
    )


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.save_mdhisto]
        save_instrument = True
        save_sample = False
        save_logs = False
        save_history = False
    """
    ],
    indirect=True,
)
def test_save_with_save_instrument(user_conf_file, monkeypatch, tmp_path):
    """Test saving with Nexus and save_instrument set to True"""

    # mock get sample_logs info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = "test_workspace"
    filepath = f"{tmp_path}/{workspace}.nxs"

    # load mde workspace
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
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
        Smoothing=1,
        OutputWorkspace=workspace,
    )
    model = HistogramModel()
    model.save(workspace, filepath)

    with h5py.File(filepath, "r") as file_data:
        assert "experiment0" in file_data["MDHistoWorkspace"]
        assert "instrument" in file_data["MDHistoWorkspace"]["experiment0"]
        assert "logs" not in file_data["MDHistoWorkspace"]["experiment0"]
        assert "sample" not in file_data["MDHistoWorkspace"]["experiment0"]
        assert "process" not in file_data["MDHistoWorkspace"]


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.save_mdhisto]
        save_instrument = False
        save_sample = True
        save_logs = False
        save_history = False
    """
    ],
    indirect=True,
)
def test_save_with_save_sample(user_conf_file, monkeypatch, tmp_path):
    """Test saving with Nexus and save_sample set to True"""

    # mock get sample_logs info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = "test_workspace"
    filepath = f"{tmp_path}/{workspace}.nxs"

    # load mde workspace
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
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
        Smoothing=1,
        OutputWorkspace=workspace,
    )

    model = HistogramModel()
    model.save(workspace, filepath)

    with h5py.File(filepath, "r") as file_data:
        assert "experiment0" in file_data["MDHistoWorkspace"]
        assert "instrument" not in file_data["MDHistoWorkspace"]["experiment0"]
        assert "logs" not in file_data["MDHistoWorkspace"]["experiment0"]
        assert "sample" in file_data["MDHistoWorkspace"]["experiment0"]
        assert "process" not in file_data["MDHistoWorkspace"]


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.save_mdhisto]
        save_instrument = False
        save_sample = False
        save_logs = True
        save_history = False
    """
    ],
    indirect=True,
)
def test_save_with_save_logs(user_conf_file, monkeypatch, tmp_path):
    """Test saving with Nexus and save_logs set to True"""

    # mock get sample_logs info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = "test_workspace"
    filepath = f"{tmp_path}/{workspace}.nxs"

    # load mde workspace
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
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
        Smoothing=1,
        OutputWorkspace=workspace,
    )

    model = HistogramModel()
    model.save(workspace, filepath)

    with h5py.File(filepath, "r") as file_data:
        assert "experiment0" in file_data["MDHistoWorkspace"]
        assert "instrument" not in file_data["MDHistoWorkspace"]["experiment0"]
        assert "logs" in file_data["MDHistoWorkspace"]["experiment0"]
        assert "sample" not in file_data["MDHistoWorkspace"]["experiment0"]
        assert "process" not in file_data["MDHistoWorkspace"]


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.save_mdhisto]
        save_instrument = False
        save_sample = False
        save_logs = False
        save_history = True
    """
    ],
    indirect=True,
)
def test_save_with_save_history(user_conf_file, monkeypatch, tmp_path):
    """Test saving with Nexus and save_history set to True"""

    # mock get sample_logs info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = "test_workspace"
    filepath = f"{tmp_path}/{workspace}.nxs"

    # load mde workspace
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
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
        Smoothing=1,
        OutputWorkspace=workspace,
    )

    model = HistogramModel()
    model.save(workspace, filepath)

    with h5py.File(filepath, "r") as file_data:
        assert "experiment0" not in file_data["MDHistoWorkspace"]
        assert "process" in file_data["MDHistoWorkspace"]
        assert len(file_data["MDHistoWorkspace"]["process"]) > 0


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.save_mdhisto]
        save_instrument = False
        save_sample = False
        save_logs = False
        save_history = False
    """
    ],
    indirect=True,
)
def test_save_with_no_save_sample_logs(user_conf_file, monkeypatch, tmp_path):
    """Test saving with Nexus and sample_logs set to False"""

    # mock get sample_logs info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = "test_workspace"
    filepath = f"{tmp_path}/{workspace}.nxs"

    # load mde workspace
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
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
        Smoothing=1,
        OutputWorkspace=workspace,
    )

    model = HistogramModel()
    model.save(workspace, filepath)

    with h5py.File(filepath, "r") as file_data:
        assert "experiment0" not in file_data["MDHistoWorkspace"]
        assert "process" not in file_data["MDHistoWorkspace"]


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.save_mdhisto]
        save_instrument = galse
        save_sample = False
        save_logs = False
        save_history = False
    """
    ],
    indirect=True,
)
def test_save_with_sample_logs_invalid(user_conf_file, monkeypatch, tmp_path):
    """Test saving with Nexus and sample_logs set to invalid value"""

    # mock get sample_logs info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = "test_workspace"
    filepath = f"{tmp_path}/{workspace}.nxs"

    # load mde workspace
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_NSF.nxs"),
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
        Smoothing=1,
        OutputWorkspace=workspace,
    )

    model = HistogramModel()
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model.connect_error_message(error_callback)

    model.save(workspace, filepath)

    assert not os.path.exists(filepath)
    assert len(errors) == 1
    assert errors[0] == "Save_logs in configuration file has invalid input. Please update it and try again."


def test_experiment_sample_log_valid(tmp_path):
    """Test the polarization state is retrieved as a sample log in the workspace: unpolarized state"""

    name = "test_workspace"
    pol_state = "UNP"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()
    polarized_model = PolarizedModel(name)

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    # save polarization state: unpolarized
    polarized_model.save_polarization_state(pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("PolarizationState").value
    assert saved_pol_state == pol_state

    # retrieve the state
    experiment_state = polarized_model.get_experiment_sample_log("PolarizationState")
    assert experiment_state is not None
    assert experiment_state == pol_state


def test_experiment_sample_log_invalid(tmp_path):
    """Test experiment sample log function for invalid sample log"""

    name = "test_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))

    # check polarization state is not in sample logs
    # retrieve the state
    polarized_model = PolarizedModel(name)
    experiment_state = polarized_model.get_experiment_sample_log("po")
    assert experiment_state is None


def test_polarization_state_unpol(tmp_path):
    """Test the polarization state is saved as a sample log in the workspace: unpolarized state"""

    name = "test_workspace"
    pol_state = "UNP"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()
    polarized_model = PolarizedModel(name)

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    # save polarization state: unpolarized
    polarized_model.save_polarization_state(pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("PolarizationState").value
    assert saved_pol_state == pol_state

    # retrieve the state after
    after_pol_state = polarized_model.get_polarization_state()
    assert after_pol_state == pol_state


def test_polarization_state_nsf(tmp_path):
    """Test the polarization state is saved as a sample log in the workspace: NSF state"""

    name = "test_workspace"
    pol_state = "NSF"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    # save polarization state: unpolarized
    polarized_model = PolarizedModel(name)
    polarized_model.save_polarization_state(pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("PolarizationState").value
    assert saved_pol_state == pol_state

    # default polarization direction saved: Pz
    saved_pol_dir = run.getLogData("PolarizationDirection").value
    assert saved_pol_dir == "Pz"

    # retrieve the state after
    after_pol_state = polarized_model.get_polarization_state()
    assert after_pol_state == pol_state


def test_polarization_state_sf(tmp_path):
    """Test the polarization state is saved as a sample log in the workspace: SF state"""

    name = "test_workspace"
    pol_state = "SF"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    # save polarization state: unpolarized
    polarized_model = PolarizedModel(name)
    polarized_model.save_polarization_state(pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("PolarizationState").value
    assert saved_pol_state == pol_state

    # retrieve the state after
    after_pol_state = polarized_model.get_polarization_state()
    assert after_pol_state == pol_state


def test_polarization_parameters(tmp_path, shiver_app, qtbot):
    """Test the polarization parameters are saved as sample logs in the workspace: NSF state"""

    name = "test_workspace"

    pol_sample_logs = {
        "PolarizationState": "NSF",
        "PolarizationDirection": "Px",
        "FlippingRatio": "3Ei+1/4",
        "FlippingRatioSampleLog": "Ei",
        "PSDA": "not this",
    }

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )
    workspace = mtd[name]
    AddSampleLog(workspace, LogName="psda", LogText="1.3", LogType="String")

    model = shiver_app.main_window.histogram_presenter.model

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    qtbot.wait(100)
    # save polarization parameters except from psda
    polarized_view = PolarizedView()
    polarized_model = PolarizedModel(name)
    polarized_presenter = PolarizedPresenter(polarized_view, polarized_model)
    polarized_view.start_dialog(True)
    polarized_presenter.handle_apply_button(pol_sample_logs)

    # check polarization parameters in sample logs
    run = workspace.getExperimentInfo(0).run()
    assert run.getLogData("PolarizationState").value == pol_sample_logs["PolarizationState"]
    assert run.getLogData("PolarizationDirection").value == pol_sample_logs["PolarizationDirection"]
    assert run.getLogData("FlippingRatio").value == pol_sample_logs["FlippingRatio"]
    assert run.getLogData("FlippingRatioSampleLog").value == pol_sample_logs["FlippingRatioSampleLog"]
    assert run.getLogData("psda").value == "1.3"

    # retrieve the polarization parameters after
    saved_pol_logs = polarized_presenter.get_polarization_logs()
    assert saved_pol_logs["PolarizationState"] == pol_sample_logs["PolarizationState"]
    assert saved_pol_logs["PolarizationDirection"] == pol_sample_logs["PolarizationDirection"]
    assert saved_pol_logs["FlippingRatio"] == pol_sample_logs["FlippingRatio"]
    assert saved_pol_logs["FlippingRatioSampleLog"] == pol_sample_logs["FlippingRatioSampleLog"]
    assert saved_pol_logs["PSDA"] == "1.3"


def test_polarization_state_invalid(tmp_path):
    """Test the polarization state for invalid state"""

    name = "test_workspace"
    pol_state = "unpol"

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    workspace = mtd[name]
    AddSampleLog(workspace, LogName="test_log", LogText="test", LogType="String")
    # save polarization state: invalid
    polarized_model = PolarizedModel(name)
    polarized_model.save_polarization_state(pol_state)

    # check polarization state is not in sample logs
    run = workspace.getExperimentInfo(0).run()
    assert "PolarizationState" not in run.keys()

    # retrieve the state after, UNP is default
    after_pol_state = polarized_model.get_polarization_state()
    assert after_pol_state == "UNP"


def test_polarization_state_no_saved_state(tmp_path):
    """Test default state"""

    name = "test_workspace"

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))

    # retrieve the state after, UNP is default
    polarized_model = PolarizedModel(name)
    after_pol_state = polarized_model.get_polarization_state()
    assert after_pol_state == "UNP"


def test_get_flipping_ratio_number(tmp_path):
    """Test for retrieving the flipping ratio number from sample logs"""

    name = "test_workspace"

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    workspace = mtd[name]
    # add the flipping ratio sample log
    AddSampleLog(workspace, LogName="FlippingRatio", LogText="9", LogType="String")

    # retrieve the flipping ratio
    polarized_model = PolarizedModel(name)
    flipping_ratio = polarized_model.get_flipping_ratio()
    assert flipping_ratio == 9


def test_get_flipping_ratio_formula(tmp_path):
    """Test for retrieving the flipping ratio formula from sample logs"""

    name = "test_workspace"

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    workspace = mtd[name]

    # add the flipping ratio sample log
    AddSampleLog(workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")
    AddSampleLog(workspace, LogName="FlippingRatioSampleLog", LogText="omega", LogType="String")

    # retrieve the flipping ratio
    polarized_model = PolarizedModel(name)
    flipping_ratio = polarized_model.get_flipping_ratio()
    assert flipping_ratio == "2*omega+9,omega"


def test_get_flipping_ratio_formula_invalid(tmp_path):
    """Test for retrieving the flipping ratio formula from sample logs"""

    name = "test_workspace"

    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=name,
    )

    model = HistogramModel()

    model.save(name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(name, str(tmp_path / "test_workspace.py"))
    workspace = mtd[name]

    # add the flipping ratio sample log
    AddSampleLog(workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")

    # retrieve the flipping ratio
    polarized_model = PolarizedModel(name)
    flipping_ratio = polarized_model.get_flipping_ratio()
    assert flipping_ratio is None


def test_validate_wokspace_logs_same(tmp_path):
    """Test for validating the flipping ratios of SF and NSF workspaces: same values"""

    model = HistogramModel()

    # SF workspace
    sf_name = "sf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=sf_name,
    )

    model.save(sf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(sf_name, str(tmp_path / "test_workspace.py"))
    sf_workspace = mtd[sf_name]

    # add the flipping ratio sample log for SF
    AddSampleLog(sf_workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")
    AddSampleLog(sf_workspace, LogName="FlippingRatioSampleLog", LogText="omega", LogType="String")

    # NSF workspace
    nsf_name = "nsf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=nsf_name,
    )

    model.save(nsf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(nsf_name, str(tmp_path / "test_workspace.py"))
    nsf_workspace = mtd[nsf_name]

    # add the flipping ratio sample log for SF
    AddSampleLog(nsf_workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")
    AddSampleLog(nsf_workspace, LogName="FlippingRatioSampleLog", LogText="omega", LogType="String")

    config = {"SFInputWorkspace": sf_name, "NSFInputWorkspace": nsf_name}

    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    model.error_callback = mock_error

    # validate flipping ratios
    continue_val = model.validate_workspace_logs(config)
    assert continue_val is True
    assert len(errors) == 0


def test_validate_wokspace_logs_different_cont(tmp_path):
    """Test for validating the flipping ratios of SF and NSF workspaces: different values with OK user input"""

    model = HistogramModel()

    # SF workspace
    sf_name = "sf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=sf_name,
    )

    model.save(sf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(sf_name, str(tmp_path / "test_workspace.py"))
    sf_workspace = mtd[sf_name]

    # add the flipping ratio sample log for SF
    AddSampleLog(sf_workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")
    AddSampleLog(sf_workspace, LogName="FlippingRatioSampleLog", LogText="omega", LogType="String")

    # NSF workspace
    nsf_name = "nsf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=nsf_name,
    )

    model.save(nsf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(nsf_name, str(tmp_path / "test_workspace.py"))
    nsf_workspace = mtd[nsf_name]
    # add the flipping ratio sample log for SF
    AddSampleLog(nsf_workspace, LogName="FlippingRatio", LogText="900", LogType="String")

    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    # connect the mock error callback
    model.connect_error_message(mock_error)
    assert model.error_callback.__name__ == mock_error.__name__

    # show message and return the `user input`
    warning_message = []

    def mock_warning(msg):
        warning_message.append(msg)
        return True

    # connect the mock warning callback
    model.connect_warning_message(mock_warning)
    assert model.warning_callback.__name__ == mock_warning.__name__

    # validate flipping ratios
    config = {"SFInputWorkspace": sf_name, "NSFInputWorkspace": nsf_name}
    continue_val = model.validate_workspace_logs(config)
    assert continue_val is True
    assert len(errors) == 0
    assert warning_message[0].startswith("FlippingRatio Sample Log value is different between workspaces") is True
    assert warning_message[0].endswith("Would you like to continue?") is True


def test_validate_wokspace_logs_different_err(tmp_path):
    """Test for validating the flipping ratios of SF and NSF workspaces: different values with Cancel user input"""

    model = HistogramModel()

    # SF workspace
    sf_name = "sf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=sf_name,
    )

    model.save(sf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(sf_name, str(tmp_path / "test_workspace.py"))
    sf_workspace = mtd[sf_name]

    # add the flipping ratio sample log for SF
    AddSampleLog(sf_workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")
    AddSampleLog(sf_workspace, LogName="FlippingRatioSampleLog", LogText="omega", LogType="String")

    # NSF workspace
    nsf_name = "nsf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=nsf_name,
    )

    model.save(nsf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(nsf_name, str(tmp_path / "test_workspace.py"))
    nsf_workspace = mtd[nsf_name]
    # add the flipping ratio sample log for SF
    AddSampleLog(nsf_workspace, LogName="FlippingRatio", LogText="900", LogType="String")

    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    # connect the mock error callback
    model.connect_error_message(mock_error)
    assert model.error_callback.__name__ == mock_error.__name__

    # show message and return the `user input`
    warning_message = []

    def mock_warning(msg):
        warning_message.append(msg)
        return False

    # connect the mock warning callback
    model.connect_warning_message(mock_warning)
    assert model.warning_callback.__name__ == mock_warning.__name__

    # validate flipping ratios
    config = {"SFInputWorkspace": sf_name, "NSFInputWorkspace": nsf_name}
    continue_val = model.validate_workspace_logs(config)
    assert continue_val is False
    assert len(errors) == 0
    assert warning_message[0].startswith("FlippingRatio Sample Log value is different between workspaces") is True
    assert warning_message[0].endswith("Would you like to continue?") is True


def test_validate_wokspace_logs_one_cont(tmp_path):
    """Test for validating the flipping ratios of SF and NSF workspaces: one value with OK user input"""

    model = HistogramModel()

    # SF workspace
    sf_name = "sf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=sf_name,
    )

    model.save(sf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(sf_name, str(tmp_path / "test_workspace.py"))
    sf_workspace = mtd[sf_name]

    # add the flipping ratio sample log for SF
    AddSampleLog(sf_workspace, LogName="FlippingRatio", LogText="2*omega+9", LogType="String")
    AddSampleLog(sf_workspace, LogName="FlippingRatioSampleLog", LogText="omega", LogType="String")

    # NSF workspace
    nsf_name = "nsf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=nsf_name,
    )

    model.save(nsf_name, str(tmp_path / "test_workspace.nxs"))
    model.save_history(nsf_name, str(tmp_path / "test_workspace.py"))

    config = {"SFInputWorkspace": sf_name, "NSFInputWorkspace": nsf_name}

    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    # connect the mock error callback
    model.connect_error_message(mock_error)
    assert model.error_callback.__name__ == mock_error.__name__

    # show message and return the `user input`
    warning_message = []

    def mock_warning(msg):
        warning_message.append(msg)
        return True

    # connect the mock warning callback
    model.connect_warning_message(mock_warning)
    assert model.warning_callback.__name__ == mock_warning.__name__

    # validate flipping ratios
    continue_val = model.validate_workspace_logs(config)
    assert continue_val is True
    assert len(errors) == 0
    assert (
        warning_message[0]
        == """FlippingRatio Sample Log value is defined only in SF.
                2*omega+9,omega will be used. Would you like to continue?"""
    )


def test_validate_wokspace_logs_invalid():
    """Test for validating the flipping ratios of SF and NSF workspaces: invalid"""

    model = HistogramModel()

    # SF workspace
    sf_name = "sf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=sf_name,
    )

    # NSF workspace
    nsf_name = "nsf_workspace"
    # Create test workspace
    CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-2,2",
        SignalInput=[2, 3],
        ErrorInput=[1, 1],
        NumberOfBins="2",
        Names="A",
        Units="a",
        OutputWorkspace=nsf_name,
    )

    config = {"SFInputWorkspace": sf_name, "NSFInputWorkspace": nsf_name}

    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    model.error_callback = mock_error

    # validate flipping ratios
    continue_val = model.validate_workspace_logs(config)
    assert continue_val is False
    assert len(errors) == 1
    assert errors[0] == "FlippingRatio Sample Log value is missing/invalid from both workspaces."


def test_do_make_slice_single(shiver_app, qtbot, monkeypatch):
    """Test test_do_make_slice single slice of input and save configurations: algorithm properties"""

    data = {}

    def finish_make_slice_mock(self, obs, ws_names):
        nonlocal data
        data["ws_names"] = ws_names
        self.algorithms_observers.remove(obs)

    model = shiver_app.main_window.histogram_presenter.model
    monkeypatch.setattr("shiver.models.histogram.HistogramModel.finish_make_slice", finish_make_slice_mock)

    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    input_config = {
        "Algorithm": "MakeSlice",
        "InputWorkspace": "data",
        "Name": "line",
        "QDimension0": "1,0,0",
        "QDimension1": "0,1,0",
        "QDimension2": "0,0,1",
        "Dimension0Name": "DeltaE",
        "Dimension0Binning": "0.1",
        "Dimension1Name": "QDimension0",
        "Dimension1Binning": "",
        "Dimension2Name": "QDimension1",
        "Dimension2Binning": "",
        "Dimension3Name": "QDimension2",
        "Dimension3Binning": "",
        "SymmetryOperations": "",
        "Smoothing": "1",
        "OutputWorkspace": "line",
        "BackgroundWorkspace": "",
        "NormalizationWorkspace": "",
    }

    # send the input_config to model for processing
    model.do_make_slice(input_config)

    def check_data():
        nonlocal data
        assert len(data) != 0

    qtbot.waitUntil(check_data, timeout=5000)
    assert data["ws_names"] == ["line"]
    # get properties from algorithm history
    saved_config = model.get_make_slice_history(data["ws_names"][0])

    # all properties from input and saved configs should match
    for algo, value in saved_config.items():
        assert input_config[algo] == value


def test_finish_make_slice_invalid():
    """Test finish_make_slice invalid"""

    model = HistogramModel()
    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    # connect the mock error callback
    model.connect_error_message(mock_error)
    assert model.error_callback.__name__ == mock_error.__name__

    # get the finish callback
    finish = {}

    def mock_finish(workspaces, error):
        finish["workspaces"] = workspaces
        finish["error"] = error

    # connect the mock finish callback
    model.connect_makeslice_finish(mock_finish)
    assert model.makeslice_finish_callback.__name__ == mock_finish.__name__

    obs = 1
    model.algorithms_observers = [obs]
    ws_names = ["test"]
    model.finish_make_slice(obs, ws_names, True, msg="Test Message")
    workspace = list(finish["workspaces"].keys())[0]
    dimension = list(finish["workspaces"].values())[0]

    assert workspace == ws_names[0]
    # workspace dimension is -1
    assert dimension == -1
    assert finish["error"] is True
    assert len(errors) == 1
    assert errors[0] == "Error making slice for test\nTest Message"


def test_do_make_slice_multi(shiver_app, qtbot, monkeypatch):
    """Test test_do_make_slice multiples slices of input and save configurations: algorithm properties"""

    data = {}

    def finish_make_slice_mock(self, obs, ws_names):
        nonlocal data
        data["ws_names"] = ws_names
        self.algorithms_observers.remove(obs)

    model = shiver_app.main_window.histogram_presenter.model
    monkeypatch.setattr("shiver.models.histogram.HistogramModel.finish_make_slice", finish_make_slice_mock)

    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="sfdata_test",
    )
    AddSampleLog(workspace="sfdata_test", LogName="FlippingRatio", LogText="9", LogType="String")

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="nsfdata_test",
    )
    AddSampleLog(workspace="nsfdata_test", LogName="FlippingRatio", LogText="9", LogType="String")

    input_config = {
        "Algorithm": "MakeSFCorrectedSlices",
        "SFOutputWorkspace": "sf_out",
        "NSFOutputWorkspace": "nsf_out",
        "SFInputWorkspace": "sfdata_test",
        "NSFInputWorkspace": "nsfdata_test",
        "QDimension0": "1,0,0",
        "QDimension1": "0,1,0",
        "QDimension2": "0,0,1",
        "Dimension0Name": "DeltaE",
        "Dimension0Binning": "0.1",
        "Dimension1Name": "QDimension0",
        "Dimension1Binning": "",
        "Dimension2Name": "QDimension1",
        "Dimension2Binning": "",
        "Dimension3Name": "QDimension2",
        "Dimension3Binning": "",
        "SymmetryOperations": "",
        "Smoothing": "1",
        "BackgroundWorkspace": "",
        "NormalizationWorkspace": "",
    }

    # send the input_config to model for processing
    model.do_make_slice(input_config)

    def check_data():
        nonlocal data
        assert len(data) != 0

    qtbot.waitUntil(check_data, timeout=10000)
    assert len(data["ws_names"]) == 2
    assert data["ws_names"] == ["sf_out", "nsf_out"]
    # get properties from algorithm history
    saved_config = model.get_make_slice_history("sf_out")

    # all properties from input and saved configs should match
    for algo, value in saved_config.items():
        assert input_config[algo] == value

    assert saved_config["FlippingRatioSampleLog"] == ""
    assert saved_config["FlippingRatio"] == "9"


def test_do_make_slice_invalid(qtbot):
    """Test test_do_make_slice multiples slices of input and save configurations: algorithm properties invalid"""

    model = HistogramModel()
    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    model.error_callback = mock_error

    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="sfdata",
    )
    AddSampleLog(workspace="sfdata", LogName="FlippingRatio", LogText="K", LogType="String")

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="nsfdata",
    )

    input_config = {
        "Algorithm": "MakeSFCorrectedSlices",
        "SFOutputWorkspace": "sf_out",
        "NSFOutputWorkspace": "nsf_out",
        "SFInputWorkspace": "sfdata",
        "NSFInputWorkspace": "nsfdata",
        "QDimension0": "1,0,0",
        "QDimension1": "0,1,0",
        "QDimension2": "0,0,1",
        "Dimension0Name": "DeltaE",
        "Dimension0Binning": "0.1",
        "Dimension1Name": "QDimension0",
        "Dimension1Binning": "",
        "Dimension2Name": "QDimension1",
        "Dimension2Binning": "",
        "Dimension3Name": "QDimension2",
        "Dimension3Binning": "",
        "SymmetryOperations": "",
        "Smoothing": 1,
        "BackgroundWorkspace": "",
        "NormalizationWorkspace": "",
    }

    # send the input_config to model for processing
    model.do_make_slice(input_config)

    def check_data():
        nonlocal errors
        assert len(errors) != 0

    qtbot.waitUntil(check_data, timeout=5000)
    assert len(errors) == 1
    assert errors[0].startswith("Error making slice for sf_out,nsf_out\nFlippingRatioCorrectionMD-v1: Parsing error")


def test_finish_make_slice_valid():
    """Test finish_make_slice valid"""

    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="test",
    )

    model = HistogramModel()
    # get the error
    errors = []

    def mock_error(err):
        errors.append(err)

    # connect the mock error callback
    model.connect_error_message(mock_error)
    assert model.error_callback.__name__ == mock_error.__name__

    # get the finish callback
    finish = {}

    def mock_finish(workspaces, error):
        finish["workspaces"] = workspaces
        finish["error"] = error

    # connect the mock finish callback
    model.connect_makeslice_finish(mock_finish)
    assert model.makeslice_finish_callback.__name__ == mock_finish.__name__

    obs = 1
    model.algorithms_observers = [obs]
    ws_names = ["test"]
    model.finish_make_slice(obs, ws_names, False, msg="")
    workspace = list(finish["workspaces"].keys())[0]
    dimension = list(finish["workspaces"].values())[0]

    assert workspace == ws_names[0]
    # workspace dimension is 4
    assert dimension == 4
    assert finish["error"] is False


def test_save_mde_workspace(shiver_app):
    """Test the MDEConfig in save mde workspace."""
    histogram_presenter = shiver_app.main_window.histogram_presenter

    # clear mantid workspace
    mtd.clear()

    # load test MD workspace
    data = "px_mini_SF"
    LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/px_mini_SF.nxs"),
        OutputWorkspace=data,
    )

    def mock_save_workspace(name, filepath):  # pylint: disable=unused-argument
        return

    histogram_presenter.save_workspace = mock_save_workspace
    histogram_presenter.save_mde_workspace(data, "/test/file/path/")

    # check the MDEConfig dictionary
    config = {}
    config_data = mtd[data].getExperimentInfo(0).run().getProperty("MDEConfig").value
    config.update(ast.literal_eval(config_data))

    assert config["mde_name"] == data
    assert config["output_dir"] == "/test/file/path"
    assert config["mde_type"] == "Data"


def test_scale_workspace(shiver_app):
    """Test scale workspace"""

    histogram_presenter = shiver_app.main_window.histogram_presenter
    scale_factor = 3
    scaled_mde = "scaled_mde"
    # clear mantid workspace
    mtd.clear()

    # load test MD workspace
    mde = LoadMD(
        Filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/mde_provenance_test.nxs")
    )

    # scale
    histogram_presenter.scale_workspace(mde, scaled_mde, scale_factor)

    # makeslices
    mdh_orig = MakeSlice(
        InputWorkspace=mde,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        Dimension0Binning="-10,10",
        Dimension1Binning="-10,10",
        Dimension2Binning="-10,10",
        Dimension3Name="DeltaE",
        Dimension3Binning="-10,10",
    )

    mdh_scaled = MakeSlice(
        InputWorkspace=scaled_mde,
        QDimension0="1,1,0",
        QDimension1="-1,1,0",
        Dimension0Binning="-10,10",
        Dimension1Binning="-10,10",
        Dimension2Binning="-10,10",
        Dimension3Name="DeltaE",
        Dimension3Binning="-10,10",
    )

    # test scaling factor
    mdh_orig_intensity = mdh_orig.getSignalArray()[0][0][0]
    mdh_scaled_intensity = mdh_scaled.getSignalArray()[0][0][0]

    assert mdh_scaled_intensity / mdh_orig_intensity == approx(scale_factor, rel=1e-3)
