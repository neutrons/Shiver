"""UI test for the histogram tab"""
import os
from functools import partial
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QContextMenuEvent
from qtpy.QtWidgets import QErrorMessage, QTextEdit, QApplication, QMenu, QLineEdit, QInputDialog
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    LoadMD,
    MakeSlice,
    CreateSampleWorkspace,
)
from shiver.views.histogram import Histogram
from shiver.views.workspace_tables import NormList


def test_histogram(shiver_app):
    """Test the mde and norm lists"""
    shiver = shiver_app

    # mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    # check
    med_list = shiver.main_window.histogram.input_workspaces.mde_workspaces
    assert med_list.count() == 1
    assert med_list.item(0).text() == "data"

    # norm workspace
    CreateSampleWorkspace(OutputWorkspace="ws2d", BinWidth=20000)
    # check
    norm_list = shiver.main_window.histogram.input_workspaces.norm_workspaces
    assert norm_list.count() == 1
    assert norm_list.item(0).text() == "ws2d"

    # mdh workspace
    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="0,0,1",
        QDimension1="1,1,0",
        QDimension2="-1,1,0",
        Dimension0Name="QDimension1",
        Dimension0Binning="0.35,0.025,0.65",
        Dimension1Name="QDimension0",
        Dimension1Binning="0.45,0.55",
        Dimension2Name="QDimension2",
        Dimension2Binning="-0.2,0.2",
        Dimension3Name="DeltaE",
        Dimension3Binning="-0.5,0.5",
        SymmetryOperations=None,
        Smoothing=1,
        OutputWorkspace="line",
    )
    # check that the workspace
    histogram_list = shiver.main_window.histogram.histogram_workspaces.histogram_workspaces
    assert histogram_list.count() == 1
    assert histogram_list.item(0).text() == "line"


def test_msg_dialog(qtbot):
    """Test the error message dialog in the histogram widget"""
    histo = Histogram()
    qtbot.addWidget(histo)
    histo.show()

    def test_dialog():
        dialog = histo.findChild(QErrorMessage)
        text_edit = dialog.findChild(QTextEdit)
        dialog.close()
        text = text_edit.toPlainText()
        assert text == "This is only a test!"

    QTimer.singleShot(100, test_dialog)

    histo.show_error_message("This is only a test!")


def test_norm_workspaces_menu(qtbot):
    """Test the mde and norm lists"""
    norm_table = NormList(WStype="norm")
    qtbot.addWidget(norm_table)
    norm_table.show()

    norm_table.add_ws("norm1", "norm", "None")
    norm_table.add_ws("norm2", "norm", "None")
    norm_table.add_ws("norm3", "norm", "None")

    assert norm_table.count() == 3

    qtbot.wait(100)

    # This is to handle the menu
    def handle_menu(action_number):
        menu = norm_table.findChild(QMenu)

        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # right-click first item and select "Delete"
    deleted = []

    def delete_callback(name):
        deleted.append(name)

    norm_table.delete_workspace_callback = delete_callback

    item = norm_table.item(0)
    assert item.text() == "norm1"

    QTimer.singleShot(100, partial(handle_menu, 2))

    QApplication.postEvent(
        norm_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, norm_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert len(deleted) == 1
    assert deleted[0] == "norm1"

    # right-click first item and select "Rename"
    rename = []

    def rename_callback(old, new):
        rename.append((old, new))

    norm_table.rename_workspace_callback = rename_callback

    def handle_dialog():
        dialog = norm_table.findChild(QInputDialog)
        line_edit = dialog.findChild(QLineEdit)
        qtbot.keyClicks(line_edit, "new_ws_name")
        qtbot.wait(100)
        qtbot.keyClick(line_edit, Qt.Key_Enter)

    item = norm_table.item(0)
    assert item.text() == "norm1"

    QTimer.singleShot(100, partial(handle_menu, 1))
    QTimer.singleShot(200, handle_dialog)

    QApplication.postEvent(
        norm_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, norm_table.visualItemRect(item).center())
    )

    qtbot.wait(500)
    assert len(rename) == 1
    assert rename[0] == ("norm1", "new_ws_name")
