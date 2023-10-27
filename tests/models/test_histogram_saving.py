"""Test the histogram workspace saving"""
# pylint: disable=too-many-lines
import os
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    CreateMDHistoWorkspace,
    CompareMDWorkspaces,
    LoadMD,
    mtd,
    AddSampleLog,
)

from shiver.models.histogram import HistogramModel


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


def test_experiment_sample_log_valid(tmp_path):
    """Test the polarization state is retrieved as a sample log in the workspace: unpolarized state"""

    name = "test_workspace"
    pol_state = "UP"
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
    model.save_polarization_state(name, pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("polarization_state").value
    assert saved_pol_state == pol_state

    # retrieve the state
    experiment_state = model.get_experiment_sample_log(workspace, "polarization_state")
    assert experiment_state is not None
    assert experiment_state.value == pol_state


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
    workspace = mtd[name]
    # retrieve the state
    experiment_state = model.get_experiment_sample_log(workspace, "po")
    assert experiment_state is None


def test_polarization_state_unpol(tmp_path):
    """Test the polarization state is saved as a sample log in the worksapce: unpolarized state"""

    name = "test_workspace"
    pol_state = "UP"
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
    model.save_polarization_state(name, pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("polarization_state").value
    assert saved_pol_state == pol_state

    # retrieve the state after
    after_pol_state = model.get_polarization_state(name)
    assert after_pol_state == pol_state


def test_polarization_state_nsf(tmp_path):
    """Test the polarization state is saved as a sample log in the worksapce: NSF state"""

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
    model.save_polarization_state(name, pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("polarization_state").value
    assert saved_pol_state == pol_state

    # retrieve the state after
    after_pol_state = model.get_polarization_state(name)
    assert after_pol_state == pol_state


def test_polarization_state_sf(tmp_path):
    """Test the polarization state is saved as a sample log in the worksapce: SF state"""

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
    model.save_polarization_state(name, pol_state)

    # check polarization state in sample logs
    workspace = mtd[name]
    run = workspace.getExperimentInfo(0).run()
    saved_pol_state = run.getLogData("polarization_state").value
    assert saved_pol_state == pol_state

    # retrieve the state after
    after_pol_state = model.get_polarization_state(name)
    assert after_pol_state == pol_state


def test_polarization_state_invalid(tmp_path):
    """Test the polarization state is saved as a sample log in the worksapce: SF state"""

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
    model.save_polarization_state(name, pol_state)

    # check polarization state is not in sample logs
    run = workspace.getExperimentInfo(0).run()
    assert "polarization_state" not in run.keys()

    # retrieve the state after, UP is default
    after_pol_state = model.get_polarization_state(name)
    assert after_pol_state == "UP"


def test_polarization_state_no_saved_state(tmp_path):
    """Test the polarization state is saved as a sample log in the worksapce: SF state"""

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

    # retrieve the state after, UP is default
    after_pol_state = model.get_polarization_state(name)
    assert after_pol_state == "UP"


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
    flipping_ratio = model.get_flipping_ratio(workspace)
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
    AddSampleLog(workspace, LogName="FlippingSampleLog", LogText="omega", LogType="String")

    # retrieve the flipping ratio
    flipping_ratio = model.get_flipping_ratio(workspace)
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
    flipping_ratio = model.get_flipping_ratio(workspace)
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
    AddSampleLog(sf_workspace, LogName="FlippingSampleLog", LogText="omega", LogType="String")

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
    AddSampleLog(nsf_workspace, LogName="FlippingSampleLog", LogText="omega", LogType="String")

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
    AddSampleLog(sf_workspace, LogName="FlippingSampleLog", LogText="omega", LogType="String")

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
    AddSampleLog(sf_workspace, LogName="FlippingSampleLog", LogText="omega", LogType="String")

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
    AddSampleLog(sf_workspace, LogName="FlippingSampleLog", LogText="omega", LogType="String")

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
        "Algorithm": "MakeMultipleSlices",
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

    qtbot.waitUntil(check_data, timeout=5000)
    assert len(data["ws_names"]) == 2
    assert data["ws_names"] == ["sf_out", "nsf_out"]
    # get properties from algorithm history
    saved_config = model.get_make_slice_history(data["ws_names"][0])

    # all properties from input and saved configs should match
    for algo, value in saved_config.items():
        assert input_config[algo] == value

    assert saved_config["FlippingSampleLog"] == ""
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
        "Algorithm": "MakeMultipleSlices",
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
