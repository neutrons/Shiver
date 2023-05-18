"""Test the histogram workspace saving"""
from mantid.simpleapi import CreateMDHistoWorkspace, CompareMDWorkspaces, LoadMD  # pylint: disable=no-name-in-module
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
        " ".join([l.strip() for l in lines[4:]]) == 'CreateMDHistoWorkspace(SignalInput="2,3", ErrorInput="1,1", '
        'Dimensionality="1", Extents="-2,2", NumberOfBins="2", Names="A", Units="a", OutputWorkspace="test_workspace")'
    )
