"""Test the histogram workspace saving"""
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
    AddSampleLog(workspace, LogName="FlippingRatio", LogText="9", LogType="Number")

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
    AddSampleLog(nsf_workspace, LogName="FlippingRatio", LogText="900", LogType="Number")

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
    AddSampleLog(nsf_workspace, LogName="FlippingRatio", LogText="900", LogType="Number")

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
        return False

    # connect the mock warning callback
    model.connect_warning_message(mock_warning)
    assert model.warning_callback.__name__ == mock_warning.__name__

    # validate flipping ratios
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
    assert warning_message[0] == "FlippingRatio Sample Log value is defined in one workspace."


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
