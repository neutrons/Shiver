"""UI tests for Sample Parameters dialog: buttons"""
import os
import re
import functools
import pytest

from qtpy import QtCore, QtWidgets

# pylint: disable=no-name-in-module
from mantid.simpleapi import LoadMD

from shiver.views.sample import SampleView
from shiver.presenters.sample import SamplePresenter
from shiver.models.sample import SampleModel


def test_load_processed_button(qtbot):
    """Test for pressing load processed nexus button"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    sample_path = str(os.path.abspath(processed_sample_file))

    completed = False

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # This is to handle modal dialogs
    def handle_dialog(sample_path):
        nonlocal completed

        # get a File Name field
        line_edit = dialog.btn_load.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, sample_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(sample_path)))
    # push the Nexus button
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "3.00000"
    assert dialog.lattice_parameters.latt_b.text() == "5.00000"
    assert dialog.lattice_parameters.latt_c.text() == "7.00000"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "90.00000"
    assert dialog.lattice_parameters.gamma.text() == "120.00000"

    assert dialog.lattice_parameters.latt_ux.text() == "1.85577"
    assert dialog.lattice_parameters.latt_uy.text() == "1.85577"
    assert dialog.lattice_parameters.latt_uz.text() == "0.00000"

    assert dialog.lattice_parameters.latt_vx.text() == "-0.00000"
    assert dialog.lattice_parameters.latt_vy.text() == "-0.00000"
    assert dialog.lattice_parameters.latt_vz.text() == "7.00000"

    # check UB matrix
    ub_matrix_data = [
        ["0.00000", "-0.00000", "0.14286"],
        ["0.14286", "-0.14286", "0.00000"],
        ["0.35741", "0.18145", "0.00000"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_sample_parameters_updates_and_load_button(qtbot):
    """Test for updating lattice parameters, UB matrix and then push processed Nexus button"""

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
    # check UB matrix
    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    # update UB matrix
    ub_matrix_data[1][1] = "-0.10000"
    dialog.ub_matrix_table.cellWidget(1, 1).clear()
    qtbot.keyClicks(dialog.ub_matrix_table.cellWidget(1, 1), ub_matrix_data[1][1])
    dialog.ub_matrix_table.cellWidget(row, column).editingFinished.emit()

    # check UB matrix
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

    # push the processed Nexus button
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    sample_path = str(os.path.abspath(processed_sample_file))

    completed = False

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # This is to handle modal dialogs
    def handle_dialog(sample_path):
        nonlocal completed

        # get a File Name field
        line_edit = dialog.btn_load.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, sample_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(sample_path)))
    # push the Nexus button
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "3.00000"
    assert dialog.lattice_parameters.latt_b.text() == "5.00000"
    assert dialog.lattice_parameters.latt_c.text() == "7.00000"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "90.00000"
    assert dialog.lattice_parameters.gamma.text() == "120.00000"

    assert dialog.lattice_parameters.latt_ux.text() == "1.85577"
    assert dialog.lattice_parameters.latt_uy.text() == "1.85577"
    assert dialog.lattice_parameters.latt_uz.text() == "0.00000"

    assert dialog.lattice_parameters.latt_vx.text() == "-0.00000"
    assert dialog.lattice_parameters.latt_vy.text() == "-0.00000"
    assert dialog.lattice_parameters.latt_vz.text() == "7.00000"

    # check UB matrix
    ub_matrix_data = [
        ["0.00000", "-0.00000", "0.14286"],
        ["0.14286", "-0.14286", "0.00000"],
        ["0.35741", "0.18145", "0.00000"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_sample_parameters_updates_invalid_and_load_button(qtbot):
    """Test for updating lattice parameters, UB matrix and then push processed Nexus button"""

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

    ub_matrix = [
        [0, 0, 0.000],
        [0.0, 1, 0.000],
        [0.000, 0.5774, 1.1547],
    ]
    for row in range(3):
        for column in range(3):
            qtbot.keyClicks(dialog.ub_matrix_table.cellWidget(row, column), str(ub_matrix[row][column]))
            dialog.ub_matrix_table.cellWidget(column, row).editingFinished.emit()

    # check background color
    color_search = re.compile("border-color: (.*);")
    for row in range(3):
        for column in range(3):
            css_style_cell = dialog.ub_matrix_table.cellWidget(row, column).styleSheet()
            bg_color_cell = color_search.search(css_style_cell).group(1)
            assert bg_color_cell == "red"

    # push the processed Nexus button
    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    sample_path = str(os.path.abspath(processed_sample_file))

    completed = False

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # This is to handle modal dialogs
    def handle_dialog(sample_path):
        nonlocal completed

        # get a File Name field
        line_edit = dialog.btn_load.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, sample_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(sample_path)))
    # push the Nexus button
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "3.00000"
    assert dialog.lattice_parameters.latt_b.text() == "5.00000"
    assert dialog.lattice_parameters.latt_c.text() == "7.00000"

    assert dialog.lattice_parameters.alpha.text() == "90.00000"
    assert dialog.lattice_parameters.beta.text() == "90.00000"
    assert dialog.lattice_parameters.gamma.text() == "120.00000"

    assert dialog.lattice_parameters.latt_ux.text() == "1.85577"
    assert dialog.lattice_parameters.latt_uy.text() == "1.85577"
    assert dialog.lattice_parameters.latt_uz.text() == "0.00000"

    assert dialog.lattice_parameters.latt_vx.text() == "-0.00000"
    assert dialog.lattice_parameters.latt_vy.text() == "-0.00000"
    assert dialog.lattice_parameters.latt_vz.text() == "7.00000"

    # check UB matrix
    ub_matrix_data = [
        ["0.00000", "-0.00000", "0.14286"],
        ["0.14286", "-0.14286", "0.00000"],
        ["0.35741", "0.18145", "0.00000"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_nexus_button(qtbot):
    """Test for pushing the Nexus button"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    nexus_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/HYS_371495.nxs.h5")

    nexus_path = str(os.path.abspath(nexus_sample_file))
    completed = False

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # This is to handle modal dialogs
    def handle_dialog(nexus_path):
        nonlocal completed

        # get a File Name field
        line_edit = dialog.btn_nexus.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, nexus_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(nexus_path)))
    # push the Nexus button
    qtbot.mouseClick(dialog.btn_nexus, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "3.59982"
    assert dialog.lattice_parameters.latt_b.text() == "3.59919"
    assert dialog.lattice_parameters.latt_c.text() == "5.68864"

    assert dialog.lattice_parameters.alpha.text() == "89.99979"
    assert dialog.lattice_parameters.beta.text() == "90.01047"
    assert dialog.lattice_parameters.gamma.text() == "119.99615"

    assert dialog.lattice_parameters.latt_ux.text() == "0.06670"
    assert dialog.lattice_parameters.latt_uy.text() == "-0.16580"
    assert dialog.lattice_parameters.latt_uz.text() == "5.68253"

    assert dialog.lattice_parameters.latt_vx.text() == "2.84609"
    assert dialog.lattice_parameters.latt_vy.text() == "0.48566"
    assert dialog.lattice_parameters.latt_vz.text() == "0.06355"

    # check UB matrix
    ub_matrix_data = [
        ["0.31780", "0.19640", "0.00200"],
        ["-0.04340", "0.25330", "0.00790"],
        ["-0.00160", "-0.01360", "0.17560"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_isaw_button(qtbot):
    """Test for pushing the Isaw button"""

    name = "data"
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace=name,
    )

    isaw_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ls_5637.mat")
    isaw_path = str(os.path.abspath(isaw_sample_file))

    completed = False

    sample = SampleView()
    sample_model = SampleModel(name)
    SamplePresenter(sample, sample_model)

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # This is to handle modal dialogs
    def handle_dialog(isaw_path):
        nonlocal completed

        # get a File Name field
        line_edit = dialog.btn_isaw.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, isaw_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    # click on isaw button
    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(isaw_path)))
    # push the Nexus button
    qtbot.mouseClick(dialog.btn_isaw, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)

    # check lattice parameters
    assert dialog.lattice_parameters.latt_a.text() == "4.74399"
    assert dialog.lattice_parameters.latt_b.text() == "4.74850"
    assert dialog.lattice_parameters.latt_c.text() == "5.12352"

    assert dialog.lattice_parameters.alpha.text() == "62.39176"
    assert dialog.lattice_parameters.beta.text() == "62.39641"
    assert dialog.lattice_parameters.gamma.text() == "59.95937"

    assert dialog.lattice_parameters.latt_ux.text() == "-1.67586"
    assert dialog.lattice_parameters.latt_uy.text() == "-3.66099"
    assert dialog.lattice_parameters.latt_uz.text() == "-4.53080"

    assert dialog.lattice_parameters.latt_vx.text() == "2.38488"
    assert dialog.lattice_parameters.latt_vy.text() == "2.97840"
    assert dialog.lattice_parameters.latt_vz.text() == "-1.44883"

    # check UB matrix
    ub_matrix_data = [
        ["0.11068", "0.16311", "-0.17273"],
        ["0.22270", "-0.15677", "0.04430"],
        ["0.05817", "-0.11802", "-0.14687"],
    ]

    for row in range(3):
        for column in range(3):
            cell_text = dialog.ub_matrix_table.cellWidget(row, column).text()
            assert cell_text == ub_matrix_data[row][column]

    dialog.close()


def test_help_button(qtbot):
    """Test for pushing the help button"""

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

    # push the Help button
    qtbot.mouseClick(dialog.btn_help, QtCore.Qt.LeftButton)

    dialog.close()


@pytest.mark.skip(reason="This test is not working on Ubuntu_22.04.")
def test_get_data_sample_after_apply(qtbot):
    """Test for retrieving all sample parameters after clicking apply.

    This test is leading to random Fatal Python error:
    Current thread 0x00007f26f4f12740 (most recent call first):
    File "{CONDA}/shiver/lib/python3.8/site-packages/pytestqt/qtbot.py", line 669 in keyClicks
    File "{REPO}/tests/views/test_sample_parameters_buttons.py", line 551 in handle_dialog
    File "{REPO}/src/shiver/views/sample.py", line 298 in btn_load_submit
    File "{CONDA}/shiver/lib/python3.8/site-packages/pytestqt/qtbot.py", line 697 in mouseClick
    File "{REPO}/tests/views/test_sample_parameters_buttons.py", line 562 in test_get_data_sample_after_apply
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/python.py", line 195 in pytest_pyfunc_call
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_callers.py", line 39 in _multicall
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_manager.py", line 80 in _hookexec
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_hooks.py", line 265 in __call__
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/python.py", line 1789 in runtest
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 167 in pytest_runtest_call
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_callers.py", line 39 in _multicall
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_manager.py", line 80 in _hookexec
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_hooks.py", line 265 in __call__
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 260 in <lambda>
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 339 in from_call
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 259 in call_runtest_hook
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 220 in call_and_report
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 131 in runtestprotocol
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/runner.py", line 112 in pytest_runtest_protocol
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_callers.py", line 39 in _multicall
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_manager.py", line 80 in _hookexec
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_hooks.py", line 265 in __call__
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/main.py", line 349 in pytest_runtestloop
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_callers.py", line 39 in _multicall
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_manager.py", line 80 in _hookexec
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_hooks.py", line 265 in __call__
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/main.py", line 324 in _main
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/main.py", line 270 in wrap_session
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/main.py", line 317 in pytest_cmdline_main
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_callers.py", line 39 in _multicall
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_manager.py", line 80 in _hookexec
    File "{CONDA}/shiver/lib/python3.8/site-packages/pluggy/_hooks.py", line 265 in __call__
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/config/__init__.py", line 167 in main
    File "{CONDA}/shiver/lib/python3.8/site-packages/_pytest/config/__init__.py", line 190 in console_main
    File "{CONDA}/shiver/bin/pytest", line 10 in <module>
    Aborted

    Most likely due to extensive usage of qtbot mouse clicking on objects retrieved via findChild by type,
    which does not ensure the correct widget will be found when multiple windows are open.
    """

    # start sample parameters dialog
    completed = False
    sample = SampleView()
    sample_model = SampleModel()
    SamplePresenter(sample, sample_model)

    processed_sample_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/raw/ub_process_nexus.nxs")
    sample_path = str(os.path.abspath(processed_sample_file))

    dialog = sample.start_dialog()
    dialog.show()
    dialog.populate_sample_parameters()

    # This is to handle modal dialogs
    def handle_dialog(sample_path):
        nonlocal completed

        # get a File Name field
        line_edit = dialog.btn_load.findChild(QtWidgets.QLineEdit)
        # Type in file to load and press enter
        qtbot.keyClicks(line_edit, sample_path)

        qtbot.keyClick(line_edit, QtCore.Qt.Key_Enter)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, functools.partial(handle_dialog, str(sample_path)))
    # push the Nexus button
    qtbot.mouseClick(dialog.btn_load, QtCore.Qt.LeftButton)

    qtbot.waitUntil(dialog_completed, timeout=5000)
    # push the apply button
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    # get data
    reduction_data = {}
    reduction_data["sample_parameters"] = sample.get_sample_parameters_dict()

    # check sample parameters lattice parameters
    assert reduction_data["sample_parameters"]["a"] == "3.00000"
    assert reduction_data["sample_parameters"]["b"] == "5.00000"
    assert reduction_data["sample_parameters"]["c"] == "7.00000"

    assert reduction_data["sample_parameters"]["alpha"] == "90.00000"
    assert reduction_data["sample_parameters"]["beta"] == "90.00000"
    assert reduction_data["sample_parameters"]["gamma"] == "120.00000"

    assert reduction_data["sample_parameters"]["u"] == "1.85577,1.85577,0.00000"
    assert reduction_data["sample_parameters"]["v"] == "-0.00000,-0.00000,7.00000"

    # check sample parameters UB matrix
    ub_matrix_data = [
        "0.00000",
        "-0.00000",
        "0.14286",
        "0.14286",
        "-0.14286",
        "0.00000",
        "0.35741",
        "0.18145",
        "0.00000",
    ]

    dict_matrix = reduction_data["sample_parameters"]["matrix_ub"].split(",")
    for index in range(9):
        assert dict_matrix[index] == ub_matrix_data[index]
