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
