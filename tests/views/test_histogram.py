"""UI test for the histogram tab"""
import os
from functools import partial
import pytest
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QContextMenuEvent
from qtpy.QtWidgets import QErrorMessage, QTextEdit, QApplication, QMenu, QLineEdit, QInputDialog
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    mtd,
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
    norm_table = NormList()
    qtbot.addWidget(norm_table)
    norm_table.show()

    norm_table.add_ws("norm1", "norm", "None", 0)
    norm_table.add_ws("norm2", "norm", "None", 0)
    norm_table.add_ws("norm3", "norm", "None", 0)

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


def test_make_histogram_button(shiver_app, qtbot):
    """Test the make histogram button."""
    shiver = shiver_app
    histogram = shiver.main_window.histogram
    histogram_presenter = shiver.main_window.histogram_presenter
    mde_list = shiver.main_window.histogram.input_workspaces.mde_workspaces
    norm_list = shiver.main_window.histogram.input_workspaces.norm_workspaces
    histogram_parameters = shiver.main_window.histogram.histogram_parameters
    histogram_workspaces = shiver.main_window.histogram.histogram_workspaces.histogram_workspaces

    call_backs = []

    def callback(msg):
        call_backs.append(msg)

    histogram.show_error_message = callback
    # button is not enabled in the beginning
    assert not histogram_parameters.histogram_btn.isEnabled()
    # Case 0: trivial case with no workspaces
    # NOTE: nothing should happen
    mtd.clear()
    histogram_presenter.submit_histogram_to_make_slice()
    assert norm_list.count() == 0

    # Case 1: happy path
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    qtbot.wait(200)
    # make sure the workspace is in the list
    assert mde_list.count() == 1
    # set data and background
    mde_list.set_data("data", "unpolarized")
    # configure the histogram parameters widget
    qtbot.mouseClick(histogram_parameters.cut_1d, Qt.LeftButton)
    histogram_parameters.name.clear()
    qtbot.keyClicks(histogram_parameters.name, "output")
    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()
    qtbot.keyClicks(histogram_parameters.projection_u, "1,0,0")
    qtbot.keyClicks(histogram_parameters.projection_v, "0,1,0")
    qtbot.keyClicks(histogram_parameters.projection_w, "0,0,1")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "0.5")
    qtbot.keyClicks(histogram_parameters.symmetry_operations, "x,y,z")
    histogram_parameters.smoothing.clear()
    qtbot.keyClicks(histogram_parameters.smoothing, "3.45")
    assert len(histogram.field_errors) == 0
    qtbot.mouseClick(histogram_parameters.histogram_btn, Qt.LeftButton)
    # check that widgets are disabled
    assert not histogram_parameters.isEnabled()
    assert not mde_list.isEnabled()
    assert not norm_list.isEnabled()

    # check that output is in the histogram list
    qtbot.wait(3000)
    assert histogram_workspaces.count() == 1
    assert histogram_workspaces.item(0).text() == "output"

    # check that widgets are re-enabled
    assert histogram_parameters.isEnabled()
    assert mde_list.isEnabled()
    assert norm_list.isEnabled()


def test_populate_ui_from_history_dict(shiver_app):
    """Test the populate ui from history dict method."""
    shiver = shiver_app
    histogram_presenter = shiver.main_window.histogram_presenter

    # load mde workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="data",
    )
    # call make slice
    MakeSlice(
        InputWorkspace="data",
        BackgroundWorkspace=None,
        NormalizationWorkspace=None,
        QDimension0="1,0,0",
        QDimension1="0,1,0",
        QDimension2="0,0,1",
        Dimension0Name="DeltaE",
        Dimension0Binning="0.1",
        Dimension1Name="QDimension0",
        Dimension1Binning="",
        Dimension2Name="QDimension1",
        Dimension2Binning="",
        Dimension3Name="QDimension2",
        Dimension3Binning="",
        SymmetryOperations=None,
        Smoothing=1,
        OutputWorkspace="line",
    )

    # populate the ui
    histogram_presenter.populate_ui_from_selected_histogram("line")

    # gather the config dict from current ui
    config_dict = histogram_presenter.build_config_for_make_slice()

    # verify
    ref_dict = {
        "InputWorkspace": "data",
        "Name": "line",
        "QDimension0": "1,0,0",
        "QDimension1": "0,1,0",
        "QDimension2": "0,0,1",
        "Dimension0Name": "DeltaE",
        "Dimension0Binning": "0.1",
        "Dimension1Name": "QDimension0",
        "Dimension1Binning": "",
        "Dimension2Name": "QDimension1",
        "Dimension2Binning": "",
        "Dimension3Name": "QDimension2",
        "Dimension3Binning": "",
        "SymmetryOperations": "",
        "Smoothing": "1.00",
        "OutputWorkspace": "line",
    }

    assert config_dict == ref_dict


def test_load_dataset_presenter(shiver_app):
    """Test the load dataset presenter."""
    shiver = shiver_app
    histogram_presenter = shiver.main_window.histogram_presenter
    histogram_view = shiver.main_window.histogram

    # make the dataset dict
    mde_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "mde",
    )
    norm_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "normalization",
    )
    dataset_dict = {
        "MdeName": "merged_mde_MnO_25meV_5K_unpol_178921-178926",
        "MdeFolder": mde_folder,
        "BackgroundMdeName": None,
        "NormalizationDataFile": os.path.join(norm_folder, "TiZr.nxs"),
    }

    # load the dataset
    histogram_presenter.load_dataset(dataset_dict)

    # verify
    assert histogram_view.gather_workspace_data() == "merged_mde_MnO_25meV_5K_unpol_178921-178926"
    assert histogram_view.gather_workspace_background() is None
    assert histogram_view.get_selected_normalization() == "TiZr"


if __name__ == "__main__":
    pytest.main([__file__])
