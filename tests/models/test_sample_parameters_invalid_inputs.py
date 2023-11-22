"""tests for Sample Parameters dialog: inputs"""
import os

# pylint: disable=no-name-in-module
from mantid.simpleapi import LoadMD

from shiver.models.sample import SampleModel


def test_invalid_angles():
    """Test for adding invalid input in alpha and beta parameters"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)

    params = {}
    params["a"] = 4.44000
    params["b"] = 4.44000
    params["c"] = 4.44000
    params["alpha"] = 120
    params["beta"] = 7
    params["gamma"] = 90.00000
    params["ux"] = 0.00
    params["uy"] = 0.00
    params["uz"] = 4.44000
    params["vx"] = 3.13955
    params["vy"] = 3.13955
    params["vz"] = -0.000
    params["ub_matrix"] = [
        [0.00151, 0.22447, -0.01833],
        [-0.01839, 0.01839, 0.22372],
        [0.22447, 0.00000, 0.01846],
    ]

    return_data = sample_model.get_ub_matrix_from_lattice(params)
    assert len(return_data) == 0


def test_colinear_u_v():
    """Test for adding colinear u anv v parameters"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)

    params = {}
    params["a"] = 4.44000
    params["b"] = 4.44000
    params["c"] = 4.44000
    params["alpha"] = 90.00000
    params["beta"] = 90.00000
    params["gamma"] = 90.00000
    params["ux"] = 0.00
    params["uy"] = 0.00
    params["uz"] = 1
    params["vx"] = 0.00
    params["vy"] = 0.00
    params["vz"] = -0.000
    params["ub_matrix"] = [
        [0.00151, 0.22447, -0.01833],
        [-0.01839, 0.01839, 0.22372],
        [0.22447, 0.00000, 0.01846],
    ]

    return_data = sample_model.get_ub_matrix_from_lattice(params)
    assert len(return_data) == 0


def test_invalid_matrix():
    """Test for adding invalid matrix data"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)

    ub_matrix = [
        [0, 0, 0.000],
        [0.0, 1, 0.000],
        [0.000, 0.5774, 1.1547],
    ]

    oriented_lattice = sample_model.get_lattice_from_ub_matrix(ub_matrix)
    assert oriented_lattice is None


def test_invalid_workspace():
    """Test for adding invalid workspace"""

    name = "data"

    sample_model = SampleModel(name)

    errors = []

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    oriented_lattice = sample_model.get_lattice_ub()
    assert oriented_lattice is not None
