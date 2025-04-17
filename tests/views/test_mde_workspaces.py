"""UI tests for the MDE list tables"""

import enum
import os
from functools import partial
import pytest
from qtpy.QtWidgets import QMenu, QInputDialog, QFileDialog, QLineEdit
from qtpy.QtCore import Qt, QTimer
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    mtd,
    LoadMD,
)

from shiver.views.workspace_tables import MDEList, Frame, get_icon


class ACTIONNUMBERS(enum.IntEnum):
    """The order of MDE Workspace options"""

    SETASDATA = enum.auto()
    SETASBACKGROUND = enum.auto()
    PROVENANCE = enum.auto()
    SETSAMPLEPARAMETERS = enum.auto()
    REFINESAMPLEPARAMETERS = enum.auto()
    SETPOLARIZATIONOPTIONS = enum.auto()
    SETCORRECTIONS = enum.auto()
    CLONE = enum.auto()
    SCALE = enum.auto()
    SAVEWORKSPACE = enum.auto()
    RENAME = enum.auto()
    DELETE = enum.auto()


def test_mde_workspaces_data_menu(qtbot):
    """Test the data submenu"""
    mde_table = MDEList()
    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("mde1", "mde", "QSample", 0)

    # This is to handle the menu
    def handle_menu():
        menu = mde_table.findChild(QMenu)
        qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)
        # check the submenu
        sub_menu = menu.findChild(QMenu)
        assert len(sub_menu.actions()) == 3
        assert sub_menu.actions()[0].text() == "Set as unpolarized data <--"
        assert sub_menu.actions()[1].text() == "Set as polarized NSF data "
        assert sub_menu.actions()[2].text() == "Set as polarized SF data "
        qtbot.keyClick(sub_menu, Qt.Key_Enter)

    # right-click first item and select "Set as data"
    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, handle_menu)
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())
    qtbot.wait(100)


def test_mde_workspaces_menu(qtbot):
    """Test the mde and norm lists"""
    mde_table = MDEList()
    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("mde1", "mde", "QSample", 0)
    mde_table.add_ws("mde2", "mde", "QSample", 0)
    mde_table.add_ws("mde3", "mde", "QSample", 0)

    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None

    qtbot.wait(100)

    assert len(mde_table.selectedItems()) == 0

    # This is to handle the menu
    def handle_menu(action_number):
        menu = mde_table.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)
        # set as data has a submenu
        if action_number == 1:
            # click set as unpolarized data
            sub_menu = menu.findChild(QMenu)
            qtbot.keyClick(sub_menu, Qt.Key_Enter)

    # right-click first item and select "Set as data"
    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, 1))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde1"
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde1"

    # right-click second item and select "Set as data"
    item = mde_table.item(1)
    assert item.text() == "mde2"

    QTimer.singleShot(100, partial(handle_menu, 1))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde2"
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde2"

    # right-click third item and select "Set as background"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    # "set as background" is at 7th place
    QTimer.singleShot(100, partial(handle_menu, 2))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde2"
    assert mde_table.background == "mde3"
    assert len(mde_table.selectedItems()) == 2
    assert mde_table.selectedItems()[0].text() == "mde2"
    assert mde_table.selectedItems()[1].text() == "mde3"

    # right-click third item and select "Set as data"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 1))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde3"
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde3"

    # right-click third item and select "Set as background"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 2))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background == "mde3"
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde3"

    # right-click third item and select "Unset as background"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 2))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 0

    # right-click first item and select "Delete"
    deleted = []

    def delete_callback(name):
        deleted.append(name)

    mde_table.delete_workspace_callback = delete_callback

    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, ACTIONNUMBERS.DELETE))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert len(deleted) == 1
    assert deleted[0] == "mde1"

    # right-click first item and select "Rename"
    rename = []

    def rename_callback(old, new):
        rename.append((old, new))

    mde_table.rename_workspace_callback = rename_callback

    def handle_dialog():
        dialog = mde_table.findChild(QInputDialog)
        line_edit = dialog.findChild(QLineEdit)
        qtbot.keyClicks(line_edit, "new_ws_name")
        qtbot.wait(100)
        qtbot.keyClick(line_edit, Qt.Key_Enter)

    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, ACTIONNUMBERS.RENAME))
    QTimer.singleShot(200, handle_dialog)
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(500)
    assert len(rename) == 1
    assert rename[0] == ("mde1", "new_ws_name")


def test_mde_workspaces_menu_nsf(qtbot):
    """Test the mde and norm lists"""
    mde_table = MDEList()
    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("mde1", "mde", "QSample", 0)
    mde_table.add_ws("mde2", "mde", "QSample", 0)
    mde_table.add_ws("mde3", "mde", "QSample", 0)

    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None

    qtbot.wait(100)

    assert len(mde_table.selectedItems()) == 0

    # This is to handle the menu
    def handle_menu(action_number):
        menu = mde_table.findChild(QMenu)
        qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)
        # set as data has a submenu
        sub_menu = menu.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(sub_menu, Qt.Key_Down)
        qtbot.keyClick(sub_menu, Qt.Key_Enter)

    # right-click first item and select "Set as NSF data"
    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, 1))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    assert mde_table.count() == 3
    assert mde_table.data_nsf == "mde1"
    assert mde_table.data_u is None
    assert mde_table.data_sf is None
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde1"

    # right-click second item and select "Set as unpolarized data"
    item = mde_table.item(1)
    assert item.text() == "mde2"

    QTimer.singleShot(100, partial(handle_menu, 0))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data_u == "mde2"
    assert mde_table.data_nsf is None
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde2"


def test_mde_workspaces_menu_pol(qtbot):
    """Test the mde and norm lists"""
    mde_table = MDEList()
    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("mde1", "mde", "QSample", 0)
    mde_table.add_ws("mde2", "mde", "QSample", 0)
    mde_table.add_ws("mde3", "mde", "QSample", 0)

    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None

    qtbot.wait(100)

    assert len(mde_table.selectedItems()) == 0

    # This is to handle the menu
    def handle_menu(action_number):
        menu = mde_table.findChild(QMenu)
        qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)
        # set as data has a submenu
        sub_menu = menu.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(sub_menu, Qt.Key_Down)
        qtbot.keyClick(sub_menu, Qt.Key_Enter)

    # right-click first item and select "Set as NSF data"
    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, 1))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data_nsf == "mde1"
    assert mde_table.data_u is None
    assert mde_table.data_sf is None
    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde1"

    # right-click second item and select "Set as SF data"
    item = mde_table.item(1)
    assert item.text() == "mde2"

    QTimer.singleShot(100, partial(handle_menu, 2))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data_u is None
    assert mde_table.data_sf == "mde2"
    assert mde_table.data_nsf == "mde1"
    # test that proteced data are the same as the properties
    assert mde_table._data_nsf == mde_table.data_nsf  # pylint: disable=W0212
    assert mde_table._data_sf == mde_table.data_sf  # pylint: disable=W0212
    assert mde_table._data_u == mde_table.data_u  # pylint: disable=W0212

    assert mde_table.background is None
    assert len(mde_table.selectedItems()) == 2
    assert mde_table.selectedItems()[0].text() == "mde1"
    assert mde_table.selectedItems()[1].text() == "mde2"


def test_mde_workspaces_menu_background(qtbot):
    """Test the mde and norm lists"""
    mde_table = MDEList()
    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("mde1", "mde", "QSample", 0)
    mde_table.add_ws("mde2", "mde", "QSample", 0)
    mde_table.add_ws("mde3", "mde", "QSample", 0)

    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None

    assert len(mde_table.selectedItems()) == 0

    # This is to handle the menu
    def handle_menu(action_number):
        menu = mde_table.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # right-click first item and select "Set as background"
    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, 2))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background == "mde1"
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde1"

    # right-click second item and select "Set as background"
    item = mde_table.item(1)
    assert item.text() == "mde2"

    QTimer.singleShot(100, partial(handle_menu, 2))
    qtbot.mouseClick(mde_table.viewport(), Qt.MouseButton.LeftButton, pos=mde_table.visualItemRect(item).center())

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background == "mde2"
    assert len(mde_table.selectedItems()) == 1
    assert mde_table.selectedItems()[0].text() == "mde2"


def test_mde_workspaces_icon(qtbot):
    """test the changing of icons for q_sample, q_lab, data and background"""
    # here
    mde_table = MDEList()

    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("qlab", "mde", "QLab", 0)
    mde_table.add_ws("qsample", "mde", "QSample", 0)

    item0 = mde_table.item(0)
    assert item0.text() == "qlab"
    assert item0.type() == Frame.QLab.value
    assert item0.icon().pixmap(20, 14).toImage() == get_icon("QLab").pixmap(20, 14).toImage()

    item1 = mde_table.item(1)
    assert item1.text() == "qsample"
    assert item1.type() == Frame.QSample.value
    assert item1.icon().pixmap(20, 14).toImage() == get_icon("QSample").pixmap(20, 14).toImage()

    mde_table.set_data("qsample1", "UNP")
    mde_table.set_data("qsample", "UNP")
    item1 = mde_table.item(1)
    assert item1.icon().pixmap(10, 14).toImage() == get_icon("UNP").pixmap(10, 14).toImage()

    mde_table.set_background("qsample")
    item1 = mde_table.item(1)
    assert item1.icon().pixmap(10, 14).toImage() == get_icon("background").pixmap(10, 14).toImage()

    mde_table.unset_background("qsample")
    item1 = mde_table.item(1)
    assert item1.icon().pixmap(20, 14).toImage() == get_icon("QSample").pixmap(20, 14).toImage()

    mde_table.set_background("qlab")
    item0 = mde_table.item(0)
    assert item0.icon().pixmap(10, 14).toImage() == get_icon("background").pixmap(10, 14).toImage()

    mde_table.unset_background("qlab")
    item0 = mde_table.item(0)
    assert item0.icon().pixmap(20, 14).toImage() == get_icon("QLab").pixmap(20, 14).toImage()


@pytest.fixture
def mde_data(monkeypatch):
    """mock unrelated set_data functions so we can check if they are run or not"""
    mde_test_data = MDEList()
    mde_test_data.save_polarization_state_callback = None

    monkeypatch.setattr(mde_test_data, "get_data_workspaces_not_allowed", lambda state: [])
    monkeypatch.setattr(
        mde_test_data,
        "unset_selected_states_with_name",
        lambda name: setattr(mde_test_data, "unset_states_called", True),
    )
    monkeypatch.setattr(
        mde_test_data, "unset_selected_data", lambda ws: setattr(mde_test_data, "unset_data_called", True)
    )
    monkeypatch.setattr(
        mde_test_data, "set_field_valid_state", lambda self_arg: setattr(mde_test_data, "valid_state_set", True)
    )
    return mde_test_data


def test_set_data_index_error(mde_data):  # pylint: disable=redefined-outer-name
    """generate an empty list and test the try - except workflow passes"""
    mde = mde_data
    mde.findItems = lambda name, flag: []
    mde.set_data("ws1", "NSF")

    # before try - except block
    assert mde._data_nsf == "ws1"  # pylint: disable=protected-access
    assert getattr(mde, "valid_state_set")
    assert getattr(mde, "unset_data_called")
    # after try - except block
    assert getattr(mde, "unset_states_called")


@pytest.fixture
def mde_background(monkeypatch):
    """mock unrelated set_background functions so we can check if they are run or not"""
    mde_test_background = MDEList()

    mde_test_background._background = None  # pylint: disable=protected-access
    monkeypatch.setattr(
        mde_test_background,
        "unset_selected_states_with_name",
        lambda name: setattr(mde_test_background, "unset_states_called", True),
    )
    monkeypatch.setattr(
        mde_test_background, "validate_data_workspace_state", lambda: setattr(mde_test_background, "validated", True)
    )
    return mde_test_background


def test_set_background_index_error(mde_background):  # pylint: disable=redefined-outer-name
    """generate an empty list and test the try - except workflow passes"""
    mde = mde_background
    mde.findItems = lambda name, flag: []

    mde.set_background("bg_ws")

    assert mde._background == "bg_ws"  # pylint: disable=protected-access
    assert getattr(mde, "validated")
    assert getattr(mde, "unset_states_called")


def test_mde_workspaces_all_data():
    """test all_data"""

    mdelist = MDEList()

    mdelist._data_u = "unpol_workspace"  # pylint: disable=protected-access
    mdelist._data_nsf = "nsf_workspace"  # pylint: disable=protected-access
    mdelist._data_sf = "sf_workspace"  # pylint: disable=protected-access

    data = mdelist.all_data()
    assert len(data) == 3
    assert data[0] == "unpol_workspace"
    assert data[1] == "nsf_workspace"
    assert data[2] == "sf_workspace"


def test_mde_workspaces_menu_polarization_dialog(qtbot):
    """Test the polarization dialog workflow from mde list"""
    mdelist = MDEList()
    qtbot.addWidget(mdelist)
    mdelist.show()

    # add workspace and set as data
    mdelist.add_ws("mde1", "mde", "QSample", 0)
    mdelist._data_nsf = "mde1"  # pylint: disable=protected-access

    qtbot.wait(100)

    # mock callback to retrieve polarization parameters
    def mock_get_polarization_logs_callback():  # pylint: disable=unused-argument
        parameters = {"PolarizationState": "UNP", "FlippingRatio": "", "FlippingRatioSampleLog": "", "PSDA": "1.3"}
        return parameters

    # mock callback to save polarization parameters
    def mock_apply_submit_callback(parameters):
        assert parameters["PolarizationState"] == "UNP"
        assert parameters["PolarizationDirection"] == "Pz"
        assert parameters["FlippingRatioSampleLog"] == ""
        assert parameters["FlippingRatio"] == "20"
        assert parameters["PSDA"] is None
        return True

    # This is to handle the mdelist menu
    def handle_menu(action_number):
        menu = mdelist.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # This is to handle the polarization dialog
    def handle_polarization_dialog(mdelist):
        dialog = mdelist.active_dialog
        # define mock callback functions
        dialog.parent.apply_submit_callback = mock_apply_submit_callback
        dialog.parent.get_polarization_logs_callback = mock_get_polarization_logs_callback
        apply_btn = dialog.btn_apply
        flipping_ratio = dialog.ratio_input
        qtbot.keyClicks(flipping_ratio, "20")
        qtbot.keyClick(apply_btn, Qt.Key_Enter)

    # select the item
    item = mdelist.item(0)
    assert item.text() == "mde1"

    # click on the menu and polarization dialog
    QTimer.singleShot(100, partial(handle_menu, 6))
    QTimer.singleShot(500, partial(handle_polarization_dialog, mdelist))
    qtbot.mouseClick(mdelist.viewport(), Qt.MouseButton.LeftButton, pos=mdelist.visualItemRect(item).center())

    # unset data
    assert mdelist._data_nsf is None  # pylint: disable=protected-access


def test_mde_workspaces_menu_sample_dialog(qtbot):
    """Test the sample parameters dialog workflow from mde list"""
    mdelist = MDEList()
    qtbot.addWidget(mdelist)
    mdelist.show()

    # clear mantid workspace
    mtd.clear()

    # load test MD workspace
    LoadMD(
        Filename=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "../data/mde/merged_mde_MnO_25meV_5K_unpol_178921-178926.nxs"
        ),
        OutputWorkspace="mde1",
    )
    # add workspace and set as data
    mdelist.add_ws("mde1", "mde", "QSample", 0)
    mdelist._data_nsf = "mde1"  # pylint: disable=protected-access

    qtbot.wait(100)

    # mock callback to retrieve sample parameters
    def mock_sample_data_callback():
        parameters = {
            "a": 4.44000,
            "b": 4.44000,
            "c": 4.44000,
            "alpha": 90.00000,
            "beta": 90.00000,
            "gamma": 90.00000,
            "ux": 0.00000,
            "uy": 0.00000,
            "uz": 1.00000,
            "vx": 1.00000,
            "vy": 0.00000,
            "vz": -0.00000,
            "ub_matrix": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        return parameters

    # mock callback to save sample parameters
    def mock_btn_apply_callback(parameters):
        assert parameters["a"] == "20"
        assert parameters["b"] == "4.44000"
        assert parameters["c"] == "4.44000"
        assert parameters["alpha"] == "90.00000"
        assert parameters["beta"] == "90.00000"
        assert parameters["gamma"] == "90.00000"
        assert parameters["u"] == "0.00000,0.00000,4.44000"
        assert parameters["v"] == "3.13955,3.13955,-0.00000"
        assert parameters["matrix_ub"] == "0.01084,0.21987,0.00000,-0.04881,0.04881,0.00000,0.00000,-0.00000,0.22523"
        return True

    # This is to handle the mdelist menu
    def handle_menu(action_number):
        menu = mdelist.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # This is to handle the polarization dialog
    def handle_sample_dialog(mdelist):
        dialog = mdelist.active_dialog
        # define mock callback functions
        dialog.parent.sample_data_callback = mock_sample_data_callback
        dialog.parent.btn_apply_callback = mock_btn_apply_callback
        apply_btn = dialog.btn_apply
        dialog.lattice_parameters.latt_a.clear()
        latt_a = dialog.lattice_parameters.latt_a
        qtbot.keyClicks(latt_a, "20")
        qtbot.mouseClick(apply_btn, Qt.LeftButton)

    # select the item
    item = mdelist.item(0)
    assert item.text() == "mde1"

    # click on the menu and sample parameter dialog
    QTimer.singleShot(100, partial(handle_menu, 4))
    QTimer.singleShot(400, partial(handle_sample_dialog, mdelist))
    qtbot.mouseClick(mdelist.viewport(), Qt.MouseButton.LeftButton, pos=mdelist.visualItemRect(item).center())

    # unset data
    assert mdelist._data_nsf is None  # pylint: disable=protected-access


def test_mde_workspaces_clone_workspace(qtbot):
    """Test the clone workspace workflow from mde list"""
    mdelist = MDEList()
    qtbot.addWidget(mdelist)
    mdelist.show()

    # add workspace and set as data
    mdelist.add_ws("mde1", "mde", "QSample", 0)

    # right-click first item and select "Clone workspace"
    did_clone = False
    clone_name = ""

    def mock_clone_callback(_, name_clone):
        nonlocal did_clone
        nonlocal clone_name
        did_clone = True
        clone_name = name_clone

    mdelist.clone_workspace_callback = mock_clone_callback

    def handle_menu(action_number):
        menu = mdelist.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    def handle_dialog(mdelist):
        dialog = mdelist.active_dialog
        lineedit = dialog.findChild(QLineEdit)
        qtbot.keyClicks(lineedit, "clone_test")
        qtbot.keyClick(dialog, Qt.Key_Enter)

    item = mdelist.item(0)

    QTimer.singleShot(100, partial(handle_menu, ACTIONNUMBERS.CLONE))
    QTimer.singleShot(500, partial(handle_dialog, mdelist))
    qtbot.mouseClick(mdelist.viewport(), Qt.MouseButton.LeftButton, pos=mdelist.visualItemRect(item).center())

    assert did_clone is True
    assert clone_name == "clone_test"


def test_mde_workspaces_scale_workspace(qtbot):
    """Test the scale workspace workflow from mde list"""
    mdelist = MDEList()
    qtbot.addWidget(mdelist)
    mdelist.show()

    # add workspace and set as data
    mdelist.add_ws("mde1", "mde", "QSample", 0)

    # right-click first item and select "Scale workspace"
    did_scale = False
    scale_name = ""
    scale_factor = 0

    def mock_scale_callback(_, out_name, sf_in):
        nonlocal did_scale
        nonlocal scale_name
        nonlocal scale_factor

        did_scale = True
        scale_name = out_name
        scale_factor = sf_in

    mdelist.scale_workspace_callback = mock_scale_callback

    def handle_menu(action_number):
        menu = mdelist.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    def handle_dialog(mdelist):
        dialog = mdelist.active_dialog

        scale_field = dialog.findChild(QLineEdit, "scale_factor_input")
        scale_field.clear()
        qtbot.keyClicks(scale_field, "2.5")

        name_field = dialog.findChild(QLineEdit, "output_workspace_input")
        name_field.clear()
        qtbot.keyClicks(name_field, "ws_scaled")

        qtbot.keyClick(dialog, Qt.Key_Enter)

    item = mdelist.item(0)

    QTimer.singleShot(100, partial(handle_menu, ACTIONNUMBERS.SCALE))
    QTimer.singleShot(500, partial(handle_dialog, mdelist))
    qtbot.mouseClick(mdelist.viewport(), Qt.MouseButton.LeftButton, pos=mdelist.visualItemRect(item).center())

    assert did_scale is True
    assert scale_name == "ws_scaled"
    assert scale_factor == "2.5"


def test_mde_workspaces_menu_save_workspace(qtbot):
    """Test the save workspace workflow from mde list"""
    mdelist = MDEList()
    qtbot.addWidget(mdelist)
    mdelist.show()

    # add workspace and set as data
    mdelist.add_ws("mde1", "mde", "QSample", 0)

    # right-click first item and select "Save workspace"
    save_ws = False
    name = ""
    filename = ""

    def mock_save_callback(ws_name, folder):
        nonlocal save_ws
        nonlocal name
        nonlocal filename
        save_ws = True
        name = ws_name
        filename = folder

    mdelist.save_mde_workspace_callback = mock_save_callback

    # This is to handle the menu
    def handle_menu(action_number):
        menu = mdelist.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # file dialog
    def handle_dialog():
        dialog = mdelist.findChild(QFileDialog)
        line_edit = dialog.findChild(QLineEdit)
        qtbot.keyClicks(line_edit, "/test_folder")
        qtbot.keyClick(line_edit, Qt.Key_Enter)

    item = mdelist.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, ACTIONNUMBERS.SAVEWORKSPACE))
    QTimer.singleShot(500, handle_dialog)
    qtbot.mouseClick(mdelist.viewport(), Qt.MouseButton.LeftButton, pos=mdelist.visualItemRect(item).center())

    assert save_ws is True
    assert name == "mde1"
    assert filename == "/test_folder"
