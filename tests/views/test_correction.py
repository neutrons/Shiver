"""UI tests for the corrections table"""

# pylint: disable=no-name-in-module
import os
import re
from qtpy.QtWidgets import (
    QWidget,
)
from mantid.simpleapi import (
    mtd,
    LoadMD,
)


def test_corrections_table(qtbot, shiver_app):
    """Test the corrections table"""

    color_search = re.compile("border-color: (.*);")

    shiver = shiver_app

    # clear mantid workspace
    mtd.clear()

    # load test MD workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )

    # Happy path
    mde_list = shiver.main_window.histogram.input_workspaces.mde_workspaces
    # right click on the first item in the list
    mde_list.set_corrections("data")

    # locate the corrections table called corrections-data
    corrections_table = shiver.main_window.findChild(QWidget, "Corrections - data")
    assert corrections_table is not None

    # check the cancel button
    cancel_button = corrections_table.findChild(QWidget, "cancel_button")
    cancel_button.click()
    corrections_table = None
    qtbot.wait(100)
    corrections_table = shiver.main_window.findChild(QWidget, "Corrections - data")
    assert corrections_table is None

    # check the apply button
    # case_0: trivial case, no correction selected, widget should be closed
    mde_list.set_corrections("data")
    corrections_table = shiver.main_window.findChild(QWidget, "Corrections - data")
    apply_button = corrections_table.findChild(QWidget, "apply_button")
    apply_button.click()
    corrections_table = None
    qtbot.wait(100)
    corrections_table = shiver.main_window.findChild(QWidget, "Corrections - data")
    assert corrections_table is None
    # case_1: invalid temperature
    # mde_list.set_corrections("data")
    # corrections_table = shiver.main_window.findChild(QWidget, "Corrections - data")
    # corrections_table.detailed_balance.setChecked(True)
    # apply_button = corrections_table.findChild(QWidget, "apply_button")
    # apply_button.click()
    # corrections_table = None
    # qtbot.wait(100)
    assert "data_DB" not in mtd
    # case_2: only one table per mde workspace
    mde_list.set_corrections("data")
    qtbot.wait(100)
    mde_list.set_corrections("data")
    qtbot.wait(100)
    corrections_tables = shiver.main_window.findChildren(QWidget, "Corrections - data")
    assert len(corrections_tables) == 1
    corrections_table = corrections_tables[0]
    corrections_table = None
    qtbot.wait(100)

    # case_3: happy path
    mde_list.set_corrections("data")
    corrections_table = shiver.main_window.findChild(QWidget, "Corrections - data")
    corrections_table.detailed_balance.setChecked(True)

    css_style_temp = corrections_table.temperature.styleSheet()
    bg_color_temp = color_search.search(css_style_temp).group(1)
    assert bg_color_temp == "red"

    assert len(corrections_table.invalid_fields) == 2
    assert corrections_table.apply_button.isEnabled() is False

    # temperature needs to be added
    corrections_table.temperature.setText("SampleTemp")
    corrections_table.hyspec_polarizer_transmission.setChecked(True)

    # set magnetic structure correction
    corrections_table.magnetic_structure_factor.setChecked(True)
    corrections_table.ion_name.setCurrentIndex(42)  # Hf3

    # test debye-waller factor
    corrections_table.debye_waller_correction.setChecked(True)
    corrections_table.u2.setText("1.2")  # <u^2> = 1.2

    apply_button = corrections_table.findChild(QWidget, "apply_button")
    assert apply_button.isEnabled() is True
    assert len(corrections_table.invalid_fields) == 0
    apply_button.click()
    qtbot.wait(100)

    # verify corrected workspace is generated
    assert "data_DB_PT_DWF_MSF" in mtd
    # verify correct algorithms are called
    alg_history = mtd["data_DB_PT_DWF_MSF"].getHistory().getAlgorithmHistories()
    alg_history_names = [alg.name() for alg in alg_history]
    assert "ApplyDetailedBalanceMD" in alg_history_names
    assert "DgsScatteredTransmissionCorrectionMD" in alg_history_names
    assert "MagneticFormFactorCorrectionMD" in alg_history_names
    assert "DebyeWallerFactorCorrectionMD" in alg_history_names

    # verify history can be reflected in the corrections table
    mde_list.set_corrections("data_DB_PT_DWF_MSF")
    corrections_table_2 = shiver.main_window.findChild(QWidget, "Corrections - data_DB_PT_DWF_MSF")
    assert corrections_table_2 is not None
    assert corrections_table_2.detailed_balance.isChecked()
    assert corrections_table_2.temperature.text() == "SampleTemp"
    assert corrections_table_2.hyspec_polarizer_transmission.isChecked()

    assert corrections_table_2.temperature.isEnabled() is False
    assert corrections_table_2.hyspec_polarizer_transmission.isEnabled() is False
    assert corrections_table_2.detailed_balance.isEnabled() is False

    assert corrections_table_2.magnetic_structure_factor.isChecked()
    assert corrections_table_2.ion_name.currentText() == "Hf3"

    assert corrections_table_2.debye_waller_correction.isChecked()
    assert corrections_table_2.u2.text() == "1.2"
    # clean up
    mtd.clear()
