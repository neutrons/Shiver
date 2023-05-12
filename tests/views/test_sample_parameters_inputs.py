"""UI tests for Sample Parameters dialog: input values"""
import os
import re
from functools import partial
from qtpy import QtCore

# pylint: disable=no-name-in-module
from mantid.simpleapi import LoadMD

from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel


def test_lattice_parameters_valid_input(qtbot):
    """Test for adding valid inputs in lattice parameters"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()

    # set parameters
    qtbot.keyClicks(dialog.lattice_parameters.latt_a, "14.15262")
    qtbot.keyClicks(dialog.lattice_parameters.latt_b, "19.29034")
    qtbot.keyClicks(dialog.lattice_parameters.latt_c, "8.58130")

    qtbot.keyClicks(dialog.lattice_parameters.alpha, "90.00000")
    qtbot.keyClicks(dialog.lattice_parameters.beta, "105.07377")
    qtbot.keyClicks(dialog.lattice_parameters.gamma, "89.99999")

    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "10.63154")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uy, "11.95967")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uz, "0.20051")

    qtbot.keyClicks(dialog.lattice_parameters.latt_vx, "-8.69201")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vy, "15.09003")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vz, "0.50648")

    assert dialog.lattice_parameters.latt_a.styleSheet() == ""
    assert dialog.lattice_parameters.latt_b.styleSheet() == ""
    assert dialog.lattice_parameters.latt_c.styleSheet() == ""

    assert dialog.lattice_parameters.alpha.styleSheet() == ""
    assert dialog.lattice_parameters.beta.styleSheet() == ""
    assert dialog.lattice_parameters.gamma.styleSheet() == ""

    assert dialog.lattice_parameters.latt_ux.styleSheet() == ""
    assert dialog.lattice_parameters.latt_uy.styleSheet() == ""
    assert dialog.lattice_parameters.latt_uz.styleSheet() == ""

    assert dialog.lattice_parameters.latt_vx.styleSheet() == ""
    assert dialog.lattice_parameters.latt_vy.styleSheet() == ""
    assert dialog.lattice_parameters.latt_vz.styleSheet() == ""

    # check the table updates
    ub_matrix_data = [
        ["-0.04538", "0.04055", "-0.01259"],
        ["0.00134", "-0.00315", "0.11687"],
        ["0.05739", "0.03214", "0.02734"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    assert dialog.btn_apply.isEnabled() is True
    dialog.close()


def test_lattice_parameters_invalid_input(qtbot):
    """Test for adding invalid inputs in lattice parameters"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    # dialog.populate_sample_parameters()

    # set parameters
    qtbot.keyClicks(dialog.lattice_parameters.latt_a, "9999")
    qtbot.keyClicks(dialog.lattice_parameters.latt_b, "10001")
    qtbot.keyClicks(dialog.lattice_parameters.latt_c, "10000")

    qtbot.keyClicks(dialog.lattice_parameters.alpha, "4")
    qtbot.keyClicks(dialog.lattice_parameters.beta, "180")
    qtbot.keyClicks(dialog.lattice_parameters.gamma, "10001")

    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "a")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uy, "b")
    qtbot.keyClicks(dialog.lattice_parameters.latt_uz, "c")

    qtbot.keyClicks(dialog.lattice_parameters.latt_vx, "d")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vy, "h")
    qtbot.keyClicks(dialog.lattice_parameters.latt_vz, "f")

    color_search = re.compile("border-color: (.*);")

    # check banckground color
    css_style_latt_a = dialog.lattice_parameters.latt_a.styleSheet()
    css_style_latt_b = dialog.lattice_parameters.latt_b.styleSheet()
    css_style_latt_c = dialog.lattice_parameters.latt_c.styleSheet()

    css_style_latt_alpha = dialog.lattice_parameters.alpha.styleSheet()
    css_style_latt_beta = dialog.lattice_parameters.beta.styleSheet()
    css_style_latt_gamma = dialog.lattice_parameters.gamma.styleSheet()

    # check text
    latt_ux_text = dialog.lattice_parameters.latt_ux.text()
    latt_uy_text = dialog.lattice_parameters.latt_ux.text()
    latt_uz_text = dialog.lattice_parameters.latt_ux.text()

    latt_vx_text = dialog.lattice_parameters.latt_vx.text()
    latt_vy_text = dialog.lattice_parameters.latt_vy.text()
    latt_vz_text = dialog.lattice_parameters.latt_vz.text()

    bg_color_latt_a = color_search.search(css_style_latt_a).group(1)
    bg_color_latt_b = color_search.search(css_style_latt_b).group(1)
    bg_color_latt_c = color_search.search(css_style_latt_c).group(1)

    bg_color_alpha = color_search.search(css_style_latt_alpha).group(1)
    bg_color_beta = color_search.search(css_style_latt_beta).group(1)
    bg_color_gamma = color_search.search(css_style_latt_gamma).group(1)

    assert bg_color_latt_a == "red"
    assert bg_color_latt_b == "red"
    assert bg_color_latt_c == "red"

    assert bg_color_alpha == "red"
    assert bg_color_beta == "red"
    assert bg_color_gamma == "red"

    assert latt_ux_text == ""
    assert latt_uy_text == ""
    assert latt_uz_text == ""

    assert latt_vx_text == ""
    assert latt_vy_text == ""
    assert latt_vz_text == ""

    assert dialog.btn_apply.isEnabled() is False
    dialog.close()


def test_ub_matrix_valid_input(qtbot):
    """Test for adding valid inputs in UB matrix"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()

    # set matrix data
    ub_matrix_data = [
        ["1.1", "1", "1"],
        ["0.0", "1.2", "0.0"],
        ["0.0", "0.0", "1.4"],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.ub_matrix_table.cellWidget(row, column), str(ub_matrix_data[row][column]))
            dialog.ub_matrix_table.cellWidget(row, column).editingFinished.emit()

    # check background color
    for row in range(3):
        for column in range(3):
            assert dialog.ub_matrix_table.cellWidget(row, column).styleSheet() == ""

    assert dialog.lattice_parameters.latt_a.text() == "1.34982"
    assert dialog.lattice_parameters.latt_b.text() == "0.83333"
    assert dialog.lattice_parameters.latt_c.text() == "0.71429"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "118.75487"
    assert dialog.lattice_parameters.gamma.text() == "124.14164"

    assert dialog.lattice_parameters.latt_ux.text() == "-0.64935"
    assert dialog.lattice_parameters.latt_uy.text() == "0.00000"
    assert dialog.lattice_parameters.latt_uz.text() == "0.71429"

    assert dialog.lattice_parameters.latt_vx.text() == "0.90909"
    assert dialog.lattice_parameters.latt_vy.text() == "0.00000"
    assert dialog.lattice_parameters.latt_vz.text() == "0.00000"

    assert dialog.btn_apply.isEnabled() is True
    dialog.close()


def test_ub_matrix_invalid_input(qtbot):
    """Test for adding invalid inputs in UB matrix"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()

    # set matrix data
    ub_matrix_data = [
        ["a", "b", "c"],
        ["k", "q", "l"],
        ["o", "s", "m"],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.ub_matrix_table.cellWidget(row, column), str(ub_matrix_data[row][column]))

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ""

    assert dialog.btn_apply.isEnabled() is True
    dialog.close()


def test_sample_parameters_initialization():
    """Test for initializing lattice parameters and UB matrix from an MDE"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "4.44000"
    assert dialog.lattice_parameters.latt_b.text() == "4.44000"
    assert dialog.lattice_parameters.latt_c.text() == "4.44000"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "90.00000"
    assert dialog.lattice_parameters.gamma.text() == "90.00000"

    assert dialog.lattice_parameters.latt_ux.text() == "0.00000"
    assert dialog.lattice_parameters.latt_uy.text() == "0.00000"
    assert dialog.lattice_parameters.latt_uz.text() == "4.44000"

    assert dialog.lattice_parameters.latt_vx.text() == "3.13955"
    assert dialog.lattice_parameters.latt_vy.text() == "3.13955"
    assert dialog.lattice_parameters.latt_vz.text() == "-0.00000"

    # check UB matrix
    ub_matrix_data = [
        ["0.15926", "0.15926", "0.00000"],
        ["-0.15926", "0.15926", "0.00000"],
        ["0.00000", "-0.00000", "0.22523"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_sample_parameters_initialization_no_workspace():
    """Test for initializing lattice parameters and UB matrix without MDE"""

    sample = SampleView()
    sample_model = SampleModel()
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()
    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "1.00000"
    assert dialog.lattice_parameters.latt_b.text() == "1.00000"
    assert dialog.lattice_parameters.latt_c.text() == "1.00000"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "90.00000"
    assert dialog.lattice_parameters.gamma.text() == "90.00000"

    assert dialog.lattice_parameters.latt_ux.text() == "0.00000"
    assert dialog.lattice_parameters.latt_uy.text() == "0.00000"
    assert dialog.lattice_parameters.latt_uz.text() == "1.00000"

    assert dialog.lattice_parameters.latt_vx.text() == "1.00000"
    assert dialog.lattice_parameters.latt_vy.text() == "0.00000"
    assert dialog.lattice_parameters.latt_vz.text() == "-0.00000"

    # check UB matrix
    ub_matrix_data = [
        ["1.00000", "0.00000", "0.00000"],
        ["0.00000", "1.00000", "0.00000"],
        ["0.00000", "-0.00000", "1.00000"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_sample_parameters_initialization_from_dict():
    """Test for initializing lattice parameters and UB matrix without MDE"""

    sample = SampleView()
    sample_model = SampleModel()
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    params = {
        "a": 5.12484,
        "b": 5.33161,
        "c": 7.31103,
        "alpha": 90,
        "beta": 90,
        "gamma": 90,
        "u": "-0.04936,4.27279,-4.37293",
        "v": "-0.07069,-3.18894,-5.85775",
    }
    dialog.populate_sample_parameters_from_dict(params)
    param_u = params["u"].split(",")
    param_v = params["v"].split(",")
    # check lattice parameters
    assert float(dialog.lattice_parameters.latt_a.text()) == params["a"]
    assert float(dialog.lattice_parameters.latt_b.text()) == params["b"]
    assert float(dialog.lattice_parameters.latt_c.text()) == params["c"]

    assert float(dialog.lattice_parameters.alpha.text()) == params["alpha"]
    assert float(dialog.lattice_parameters.beta.text()) == params["beta"]
    assert float(dialog.lattice_parameters.gamma.text()) == params["gamma"]

    assert float(dialog.lattice_parameters.latt_ux.text()) == float(param_u[0])
    assert float(dialog.lattice_parameters.latt_uy.text()) == float(param_u[1])
    assert float(dialog.lattice_parameters.latt_uz.text()) == float(param_u[2])

    assert float(dialog.lattice_parameters.latt_vx.text()) == float(param_v[0])
    assert float(dialog.lattice_parameters.latt_vy.text()) == float(param_v[1])
    assert float(dialog.lattice_parameters.latt_vz.text()) == float(param_v[2])

    # check UB matrix
    ub_matrix_data = [
        ["-0.00269", "-0.11219", "-0.10959"],
        ["-0.19510", "0.00010", "0.00230"],
        ["-0.00188", "0.15030", "-0.08181"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_sample_parameters_initialization_from_dict_invalid():
    """Test for initializing lattice parameters and UB matrix without MDE - invalid"""

    sample = SampleView()
    sample_model = SampleModel()
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    params = {
        "a": 5.12484,
        "b": 5.33161,
        "c": 7.31103,
        "alpha": 90,
        "beta": 90,
        "gamma": 90,
        "u": "-0.04936,4.27279,-4.37293",
        "w": "-0.07069,-3.18894,-5.85775",
    }

    # This is to handle modal dialog expected error
    def handle_dialog():
        dialog.done(-1)

    QtCore.QTimer.singleShot(500, partial(handle_dialog))
    dialog.populate_sample_parameters_from_dict(params)


def test_sample_parameters_updates(qtbot):
    """Test for updating lattice parameters and UB matrix"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # update lattice parameter
    dialog.lattice_parameters.latt_ux.clear()
    qtbot.keyClicks(dialog.lattice_parameters.latt_ux, "54")

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "4.44000"
    assert dialog.lattice_parameters.latt_b.text() == "4.44000"
    assert dialog.lattice_parameters.latt_c.text() == "4.44000"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "90.00000"
    assert dialog.lattice_parameters.gamma.text() == "90.00000"

    assert dialog.lattice_parameters.latt_ux.text() == "54"
    assert dialog.lattice_parameters.latt_uy.text() == "0.00000"
    assert dialog.lattice_parameters.latt_uz.text() == "4.44000"

    assert dialog.lattice_parameters.latt_vx.text() == "3.13955"
    assert dialog.lattice_parameters.latt_vy.text() == "3.13955"
    assert dialog.lattice_parameters.latt_vz.text() == "-0.00000"

    # check UB matrix
    ub_matrix_data = [
        ["0.00151", "0.22447", "-0.01833"],
        ["-0.01839", "0.01839", "0.22372"],
        ["0.22447", "0.00000", "0.01846"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    # update UB matrix
    ub_matrix_data[1][1] = "-0.10000"
    dialog.ub_matrix_table.cellWidget(1, 1).clear()
    qtbot.keyClicks(dialog.ub_matrix_table.cellWidget(1, 1), ub_matrix_data[1][1])
    dialog.ub_matrix_table.cellWidget(row, column).editingFinished.emit()

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "4.44443"
    assert dialog.lattice_parameters.latt_b.text() == "4.63920"
    assert dialog.lattice_parameters.latt_c.text() == "5.05774"

    assert dialog.lattice_parameters.alpha.text() == "61.38455"
    assert dialog.lattice_parameters.beta.text() == "91.23222"
    assert dialog.lattice_parameters.gamma.text() == "92.56976"

    assert dialog.lattice_parameters.latt_ux.text() == "4.42503"
    assert dialog.lattice_parameters.latt_uy.text() == "-0.00007"
    assert dialog.lattice_parameters.latt_uz.text() == "0.36371"

    assert dialog.lattice_parameters.latt_vx.text() == "-0.16882"
    assert dialog.lattice_parameters.latt_vy.text() == "4.62371"
    assert dialog.lattice_parameters.latt_vz.text() == "2.05286"

    dialog.close()
