"""tests for Sample Parameters dialog: button actions"""
import os
from pytest import approx

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


def test_procesed_nexus_button_processed_valid():
    """Test for pressing processed Nexus button with processed nexus"""

    # initialize
    name = ""
    errors = []
    sample_model = SampleModel(name)

    assert sample_model.oriented_lattice is None

    # load the file
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    nexus_path = str(os.path.abspath(filename))

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.load_nexus_processed(nexus_path)

    # check if the oriented lattice is updated
    assert len(errors) == 0
    assert sample_model.oriented_lattice.a() == approx(3.00)
    assert sample_model.oriented_lattice.b() == approx(5.00)
    assert sample_model.oriented_lattice.c() == approx(7.00)
    assert sample_model.oriented_lattice.alpha() == approx(90)
    assert sample_model.oriented_lattice.beta() == approx(90)
    assert sample_model.oriented_lattice.gamma() == approx(120)


def test_procesed_nexus_button_md_valid():
    """Test for pressing processed Nexus button with load md"""

    # initialize
    name = ""
    errors = []
    sample_model = SampleModel(name)

    assert sample_model.oriented_lattice is None

    # load the file
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/mde/mde_provenance_test.nxs")
    nexus_path = str(os.path.abspath(filename))

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.load_nexus_processed(nexus_path)

    # check if the oriented lattice is updated
    assert len(errors) == 0
    assert sample_model.oriented_lattice.a() == approx(1.00)
    assert sample_model.oriented_lattice.b() == approx(1.00)
    assert sample_model.oriented_lattice.c() == approx(1.00)
    assert sample_model.oriented_lattice.alpha() == approx(90)
    assert sample_model.oriented_lattice.beta() == approx(90)
    assert sample_model.oriented_lattice.gamma() == approx(90)


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


def test_save_isaw_button_valid(tmp_path):
    """Test for pressing Save Isaw button with valid input"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    save_filename = str(tmp_path / "test_ub.isaw")

    sample_model = SampleModel(name)

    errors = []
    params = {}

    params["a"] = 4.44000
    params["b"] = 4.44000
    params["c"] = 4.44000
    params["alpha"] = 90
    params["beta"] = 90
    params["gamma"] = 90
    params["u"] = "0,0,4.44"
    params["v"] = "-4.44,0,0"
    params["ub_matrix"] = [
        [-2.25225225e-01, -1.37910676e-17, 0],
        [0, -2.25225225e-01, 0],
        [1.37910676e-17, -1.37910676e-17, 2.25225225e-01],
    ]

    def error_callback(msg):
        errors.append(msg)

    sample_model.connect_error_message(error_callback)
    sample_model.get_lattice_ub()

    # set ub matrix
    sample_model.set_ub(params)

    assert sample_model.oriented_lattice.a() == approx(4.44)
    assert sample_model.oriented_lattice.b() == approx(4.44)
    assert sample_model.oriented_lattice.c() == approx(4.44)
    assert sample_model.oriented_lattice.alpha() == approx(90)
    assert sample_model.oriented_lattice.beta() == approx(90)
    assert sample_model.oriented_lattice.gamma() == approx(90)

    assert sample_model.oriented_lattice.getuVector()[0] == approx(0)
    assert sample_model.oriented_lattice.getuVector()[1] == approx(0)
    assert sample_model.oriented_lattice.getuVector()[2] == approx(4.44)

    assert sample_model.oriented_lattice.getvVector()[0] == approx(-4.44)
    assert sample_model.oriented_lattice.getvVector()[1] == approx(0)
    assert sample_model.oriented_lattice.getvVector()[2] == approx(0)

    # save it in the file
    sample_model.save_isaw(save_filename)
    sample_model.oriented_lattice = None
    assert sample_model.oriented_lattice is None

    # load the file
    sample_model.load_isaw_ub(save_filename)
    assert sample_model.oriented_lattice.a() == approx(4.44)
    assert sample_model.oriented_lattice.b() == approx(4.44)
    assert sample_model.oriented_lattice.c() == approx(4.44)
    assert sample_model.oriented_lattice.alpha() == approx(90)
    assert sample_model.oriented_lattice.beta() == approx(90)
    assert sample_model.oriented_lattice.gamma() == approx(90)

    assert sample_model.oriented_lattice.getuVector()[0] == approx(0)
    assert sample_model.oriented_lattice.getuVector()[1] == approx(0)
    assert sample_model.oriented_lattice.getuVector()[2] == approx(4.44)

    assert sample_model.oriented_lattice.getvVector()[0] == approx(-4.44)
    assert sample_model.oriented_lattice.getvVector()[1] == approx(0)
    assert sample_model.oriented_lattice.getvVector()[2] == approx(0)

    ub_matrix = sample_model.oriented_lattice.getUB()
    for row in range(3):
        for col in range(3):
            assert ub_matrix[row][col] == approx(params["ub_matrix"][row][col])

    assert len(errors) == 0
