"""UI tests for the corrections table"""
import os
from qtpy.QtWidgets import (
    QWidget,
)
from mantid.simpleapi import (
    mtd,
    LoadMD,
)
from shiver import Shiver


def test_corrections_table(qtbot):
    """Test the corrections table"""
    shiver = Shiver()
    qtbot.addWidget(shiver)
    shiver.show()

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
    corrections_table = shiver.main_window.findChild(
        QWidget, "Corrections - data")
    assert corrections_table is not None

    # trigger the help button to open the browser
    corrections_table.help()

    # check the cancel button
    corrections_table.cancel()
    corrections_table = None
    qtbot.wait(100)
    corrections_table = shiver.main_window.findChild(
        QWidget, "Corrections - data")
    assert corrections_table is None

    # check the apply button
    # case_0: trival case, no correction selected, widget should be closed
    mde_list.set_corrections("data")
    corrections_table = shiver.main_window.findChild(
        QWidget, "Corrections - data")
    corrections_table.apply()
    corrections_table = None
    qtbot.wait(100)
    corrections_table = shiver.main_window.findChild(
        QWidget, "Corrections - data")
    assert corrections_table is None
    # case_1: incorrect input
    mde_list.set_corrections("data")
    corrections_table = shiver.main_window.findChild(
        QWidget, "Corrections - data")
    corrections_table.detailed_balance.setChecked(True)
    err_msg = corrections_table.apply()
    assert err_msg != ""
    corrections_table = None
    qtbot.wait(100)
    # case_2: only one table per mde workspace
    mde_list.set_corrections("data")
    qtbot.wait(100)
    mde_list.set_corrections("data")
    qtbot.wait(100)
    corrections_tables = shiver.main_window.findChildren(
        QWidget, "Corrections - data")
    assert len(corrections_tables) == 1
    corrections_table = corrections_tables[0]
    corrections_table = None
    qtbot.wait(100)
    # case_3: happy path
    mde_list.set_corrections("data")
    corrections_table = shiver.main_window.findChild(
        QWidget, "Corrections - data")
    corrections_table.detailed_balance.setChecked(True)
    corrections_table.temperature.setText("SampleTemp")
    corrections_table.hyspec_polarizer_transmission.setChecked(True)
    corrections_table.apply()
    qtbot.wait(100)
    # verify corrected workspace is generated
    assert "data_correction" in mtd
    # verify correct algorithms are called
    alg_history = mtd["data_correction"].getHistory().getAlgorithmHistories()
    alg_history_names = [alg.name() for alg in alg_history]
    assert "ApplyDetailedBalanceMD" in alg_history_names
    assert "DgsScatteredTransmissionCorrectionMD" in alg_history_names
    # verify history can be reflected in the corrections table
    mde_list.set_corrections("data_correction")
    corrections_table_2 = shiver.main_window.findChild(
        QWidget, "Corrections - data_correction")
    assert corrections_table_2 is not None
    assert corrections_table_2.detailed_balance.isChecked()
    assert corrections_table_2.temperature.text() == "SampleTemp"
    assert corrections_table_2.hyspec_polarizer_transmission.isChecked()

    # clean up
    mtd.clear()
