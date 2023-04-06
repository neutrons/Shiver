"""tests for Sample Parameters dialog"""

from mantid.simpleapi import (
    mtd,
    LoadMD,
)
from shiver.models.sample import SampleModel

import os
import re


def test_invalid_angles(qtbot):
    """Test for adding invalid input in alphag and beta parameters"""    
    
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
    params["latt_a"] = 4.44000
    params["latt_b"] = 4.44000
    params["latt_c"] = 4.44000
    params["latt_alpha"] = 120
    params["latt_beta"] = 7
    params["latt_gamma"] = 90.00000
    params["latt_ux"] = 0.00
    params["latt_uy"] = 0.00
    params["latt_uz"] = 4.44000
    params["latt_vx"] =3.13955
    params["latt_vy"] = 3.13955
    params["latt_vz"] = -0.000
    params["ub_matrix"] = [
        [0.00151, 0.22447, -0.01833],
        [-0.01839,0.01839,0.22372],
        [0.22447,0.00000,0.01846],
    ]


    def error_callback(msg):
        errors.append(msg) 

    sample_model.connect_error_message(error_callback)
    sample_model.get_UB_data_from_lattice(params)
    assert len(errors) == 1
    assert (
        errors[-1] == 'Invalid lattices: Invalid angles\n'
    )
    

def test_colinear_u_v(qtbot):
    """Test for adding colinear u anv v parameters"""    
    
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
    params["latt_a"] = 4.44000
    params["latt_b"] = 4.44000
    params["latt_c"] = 4.44000
    params["latt_alpha"] = 90.00000
    params["latt_beta"] = 90.00000
    params["latt_gamma"] = 90.00000
    params["latt_ux"] = 0.00
    params["latt_uy"] = 0.00
    params["latt_uz"] = 1
    params["latt_vx"] = 0.00
    params["latt_vy"] = 0.00
    params["latt_vz"] = -0.000
    params["ub_matrix"] = [
        [0.00151, 0.22447, -0.01833],
        [-0.01839,0.01839,0.22372],
        [0.22447,0.00000,0.01846],
    ]


    def error_callback(msg):
        errors.append(msg) 

    sample_model.connect_error_message(error_callback)
    sample_model.get_UB_data_from_lattice(params)
    assert len(errors) == 1
    assert (
        errors[-1] == 'uv and vx arrays need to be non co-linear\n'
    )    

def test_invalid_matrix(qtbot):
    """Test for adding invalid matrix data"""    
    
    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample_model = SampleModel(name)

    errors = []

    ub_matrix = [
        [0, 0, 0.000],
        [0.0,1,0.000],
        [0.000,0.5774,1.1547],
    ]


    def error_callback(msg):
        errors.append(msg) 

    sample_model.connect_error_message(error_callback)
    ol = sample_model.get_lattice_from_UB_data(ub_matrix)
    assert ol == None
    assert len(errors) == 1
    assert (
        errors[-1] == 'Invalid values in matrix\n'
    )    

    
def test_invalid_workspace(qtbot):
    """Test for adding invalid matrix data"""    
    
    name = "data"

    sample_model = SampleModel(name)

    errors = []

    def error_callback(msg):
        errors.append(msg) 

    sample_model.connect_error_message(error_callback)
    ol = sample_model.get_lattice_ub()
    assert ol == False
    assert len(errors) == 1
    assert (
        errors[-1] == 'Workspace data does not exist\n'
    )    
    
    
    
