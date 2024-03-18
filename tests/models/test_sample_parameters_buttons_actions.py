"""tests for Sample Parameters dialog: button actions"""

import os

# pylint: disable=no-name-in-module
from mantid.simpleapi import LoadMD
from shiver.models.sample import SampleModel


def test_apply_button_valid():
    """Test for pressing Apply button with valid input"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)

    errors = []
    params = {}

    params["a"] = 4.44000
    params["b"] = 4.44000
    params["c"] = 4.44000
    params["alpha"] = 90.00000
    params["beta"] = 89.09991
    params["gamma"] = 90.00000
    params["u"] = "0.00,0.00,4.44000"
    params["v"] = "3.13955,3.13955,-0.000"
    params["ub_matrix"] = [
        [0.00151, 0.22447, -0.01833],
        [-0.01839, 0.01839, 0.22372],
        [0.22447, 0.00000, 0.01846],
    ]

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.set_ub(params)
    assert len(errors) == 0


def test_apply_button_invalid():
    """Test for pressing Apply button with invalid input"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)

    errors = []
    params = {}
    params["a"] = 4.44000
    params["b"] = 4.44000
    params["c"] = 4.44000
    params["alpha"] = 120
    params["beta"] = 7
    params["gamma"] = 90.00000
    params["u"] = "0.00,0.00,4.44000"
    params["v"] = "3.13955,3.13955,-0.000"
    params["ub_matrix"] = [
        [0.00151, 0.22447, -0.01833],
        [-0.01839, 0.01839, 0.22372],
        [0.22447, 0.00000, 0.01846],
    ]

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.set_ub(params)
    assert len(errors) == 1
    assert errors[-1] == "Invalid lattices: Invalid angles\n"


def test_procesed_nexus_button_invalid():
    """Test for pressing processed Nexus button"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    errors = []
    sample_model = SampleModel(name)

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/isaw_ub_do_not_load.mat")
    nexus_path = str(os.path.abspath(filename))

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.load_nexus_processed(nexus_path)
    assert len(errors) == 1
    assert errors[-1][0:29] == "Could not open the Nexus file"


def test_nexus_button_invalid():
    """Test for pressing unprocossed Nexus button"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    errors = []
    sample_model = SampleModel(name)

    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/isaw_ub_do_not_load.mat")
    nexus_path = str(os.path.abspath(filename))

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.load_nexus_ub(nexus_path)
    assert len(errors) == 1
    assert errors[-1][0:29] == "Could not open the Nexus file"


def test_isaw_button_invalid():
    """Test for pressing Isaw button"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    errors = []
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/isaw_ub_do_not_load.mat")
    isaw_path = str(os.path.abspath(filename))

    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    sample_model = SampleModel(name)

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.load_isaw_ub(isaw_path)
    assert len(errors) == 1
    assert errors[-1][0:28] == "Could not open the Isaw file"
