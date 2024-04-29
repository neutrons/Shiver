"""UI tests for Reduction Parameters widget: input values"""

import os
import re
from functools import partial
from qtpy import QtCore, QtWidgets
from shiver.views.generate import Generate


def test_reduction_parameters_mask_valid_input(qtbot):
    """Test for adding valid inputs in reduction parameters mask"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    nexus_path = str(os.path.abspath(processed_sample_file))

    completed = False

    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.mask_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_dialog, str(nexus_path)))
    # push the browse button
    qtbot.mouseClick(red_params.mask_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    assert red_params.mask_path.text().endswith(nexus_path) is True


def test_reduction_parameters_norm_valid_input(qtbot):
    """Test for adding valid inputs in reduction parameters norm"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    nexus_path = str(os.path.abspath(processed_sample_file))

    completed = False

    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.norm_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_dialog, str(nexus_path)))
    # push the browse button
    qtbot.mouseClick(red_params.norm_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    assert red_params.norm_path.text().endswith(nexus_path) is True


def test_reduction_parameters_text_valid_input(qtbot):
    """Test for adding valid inputs in reduction parameters ei and t0"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    qtbot.keyClicks(red_params.ei_input, "72.94")
    qtbot.keyClicks(red_params.t0_input, "18.09")

    assert red_params.ei_input.text() == "72.94"
    assert red_params.t0_input.text() == "18.09"


def test_reduction_parameters_text_invalid_input(qtbot):
    """Test for adding invalid inputs in reduction parameters ei and t0"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)

    red_params = generate.reduction_parameters
    qtbot.keyClicks(red_params.ei_input, "-a")
    qtbot.keyClicks(red_params.t0_input, "a")

    assert red_params.ei_input.text() == ""
    assert red_params.t0_input.text() == ""


def test_reduction_parameters_text_invalid_numbers(qtbot):
    """Test for adding invalid number format inputs in reduction parameters ei and t0"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)
    color_search = re.compile("border-color: (.*);")

    red_params = generate.reduction_parameters
    qtbot.keyClicks(red_params.ei_input, "-")
    qtbot.keyClicks(red_params.t0_input, "-")

    # check output_dir border
    css_style_t0 = red_params.t0_input.styleSheet()
    color = color_search.search(css_style_t0).group(1)
    assert color == "red"

    assert red_params.ei_input.text() == ""
    assert red_params.t0_input.text() == "-"


def test_reduction_parameters_get_data_first_level(qtbot):
    """Test for retrieving all reduction parameters from initial widget"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)
    red_params = generate.reduction_parameters

    # mask input
    processed_mask_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    mask_path = str(os.path.abspath(processed_mask_file))

    completed = False

    # This is to handle modal dialogs
    def handle_mask_dialog(mask_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.mask_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, mask_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_mask_dialog, str(mask_path)))
    # push the browse button
    qtbot.mouseClick(red_params.mask_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    # norm input
    processed_norm_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/HYS_371495.nxs.h5")
    norm_path = str(os.path.abspath(processed_norm_file))

    completed = False

    # This is to handle modal dialogs
    def handle_norm_dialog(norm_path):
        nonlocal completed

        # get a File Name field
        line_edit = red_params.norm_browse.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, norm_path)
        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    QtCore.QTimer.singleShot(500, partial(handle_norm_dialog, str(norm_path)))
    # push the browse button
    qtbot.mouseClick(red_params.norm_browse, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    qtbot.keyClicks(red_params.ei_input, "85.49")
    qtbot.keyClicks(red_params.t0_input, "10")

    # get data
    reduction_data = red_params.get_reduction_params_dict()

    # check first layer reduction parameters
    assert reduction_data["MaskingDataFile"].endswith(mask_path) is True
    assert reduction_data["NormalizationDataFile"].endswith(norm_path) is True
    assert reduction_data["Ei"] == red_params.ei_input.text()
    assert reduction_data["T0"] == red_params.t0_input.text()


def test_reduction_parameters_initialization_from_dict_reduct(qtbot):
    """Test for initializing all reduction parameters from dict"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)
    red_params = generate.reduction_parameters

    parameters = {
        "MaskingDataFile": "/home/test/maskfile/",
        "NormalizationDataFile": "/home/test/normfile/",
        "Ei": 1.2,
        "T0": 3.89,
        "AdvancedOptions": {},
        "SampleParameters": {},
        "PolarizedOptions": {},
    }
    red_params.populate_red_params_from_dict(parameters)

    # check first layer reduction parameters
    assert red_params.mask_path.text() == parameters["MaskingDataFile"]
    assert red_params.norm_path.text() == parameters["NormalizationDataFile"]
    assert red_params.ei_input.text() == str(parameters["Ei"])
    assert red_params.t0_input.text() == str(parameters["T0"])

    qtbot.wait(500)


def test_reduction_parameters_initialization_from_dict_to_dict(qtbot):
    """Test for initializing all reduction parameters from dict"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)
    red_params = generate.reduction_parameters
    table_data = [{"Bank": "1,5,9", "Tube": "4,5,7", "Pixel": "8-67"}, {"Bank": "2", "Tube": "2", "Pixel": "12"}]
    parameters = {
        # "MaskingDataFile": None,
        # "NormalizationDataFile": None,
        # "Ei": None,
        # "T0": None,
        "AdvancedOptions": {
            "MaskInputs": table_data,
            # "E_min": None,
            # "E_max": None,
            "ApplyFilterBadPulses": False,
            # "BadPulsesThreshold": None,
            # "TimeIndepBackgroundWindow": None,
            "Goniometer": "g1",
            "AdditionalDimensions": "xx,23,45",
        },
        "SampleParameters": {
            "a": 5.12484,
            "b": 5.33161,
            "c": 7.31103,
            "alpha": 90,
            "beta": 90,
            "gamma": 90,
            "u": "-0.04936,4.27279,-4.37293",
            "v": "-0.07069,-3.18894,-5.85775",
        },
        "PolarizedOptions": {
            "PolarizationState": "UNP",
            "FlippingRatio": None,
            "FlippingRatioSampleLog": "",
            "PSDA": 2.2,
        },
    }
    red_params.populate_red_params_from_dict(parameters)

    # check first layer reduction parameters
    assert red_params.mask_path.text() == ""
    assert red_params.norm_path.text() == ""
    assert red_params.ei_input.text() == ""
    assert red_params.t0_input.text() == ""

    # check advanced options
    completed = False

    # This is to handle advanced dialog
    def handle_adv_dialog(params, table_data):
        nonlocal completed
        dialog = red_params.active_dialog
        # assert fields are populated properly
        for row in range(len(table_data)):
            assert dialog.table_view.item(row, 0).text() == params["MaskInputs"][row]["Bank"]
            assert dialog.table_view.item(row, 1).text() == params["MaskInputs"][row]["Tube"]
            assert dialog.table_view.item(row, 2).text() == params["MaskInputs"][row]["Pixel"]

        assert dialog.emin_input.text() == ""
        assert dialog.emax_input.text() == ""
        assert dialog.filter_check.isChecked() is params["ApplyFilterBadPulses"]
        assert dialog.lcutoff_input.text() == ""
        assert dialog.tib_min_input.text() == ""
        assert dialog.tib_max_input.text() == ""

        assert dialog.gonio_input.text() == params["Goniometer"]
        assert dialog.adt_dim_input.text() == params["AdditionalDimensions"]

        # click apply
        qtbot.keyClick(dialog.btn_apply, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_adv_dialog, parameters["AdvancedOptions"], table_data))
    qtbot.mouseClick(red_params.adv_btn, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check sample parameters
    completed = False

    # This is to handle sample dialog
    def handle_sample_dialog(params):
        nonlocal completed
        dialog = red_params.active_dialog
        # assert fields are populated properly
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

        # click apply
        qtbot.keyClick(dialog.btn_apply, QtCore.Qt.Key_Enter)
        completed = True

    QtCore.QTimer.singleShot(500, partial(handle_sample_dialog, parameters["SampleParameters"]))
    qtbot.mouseClick(red_params.sample_btn, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check polarized options
    completed = False

    # This is to handle pol dialog
    def handle_pol_dialog():
        nonlocal completed
        dialog = red_params.active_dialog
        # assert fields are populated properly
        assert dialog.state_unpolarized.isChecked() is True
        assert dialog.state_spin.isChecked() is False
        assert dialog.state_no_spin.isChecked() is False

        assert dialog.dir_pz.isChecked() is True
        assert dialog.dir_px.isChecked() is False
        assert dialog.dir_py.isChecked() is False

        assert dialog.ratio_input.text() == ""
        assert dialog.ratio_input.isVisible() is False
        assert dialog.log_input.text() == ""
        assert dialog.ratio_input.isVisible() is False
        assert dialog.psda_input.text() == "2.2"
        assert len(dialog.invalid_fields) == 0

        # click apply
        qtbot.keyClick(dialog.btn_apply, QtCore.Qt.Key_Enter)
        completed = True

    QtCore.QTimer.singleShot(500, partial(handle_pol_dialog))
    qtbot.mouseClick(red_params.pol_btn, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)


def test_update_polarization_label(qtbot):
    """Test for the polarization label"""

    generate = Generate()
    generate.show()
    qtbot.addWidget(generate)
    red_params = generate.reduction_parameters
    red_params.dict_polarized = {"PolarizationState": "SF", "PolarizationDirection": "Px"}
    red_params.update_polarization_label()
    assert red_params.polarization_label.text() == "SF_Px"
