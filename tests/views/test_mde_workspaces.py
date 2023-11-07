"""UI tests for the MDE list tables"""
from functools import partial
from qtpy.QtWidgets import QMenu, QInputDialog, QLineEdit, QDialog, QPushButton
from qtpy.QtCore import Qt, QTimer
from shiver.views.workspace_tables import MDEList, Frame, get_icon


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

    QTimer.singleShot(100, partial(handle_menu, 8))
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

    QTimer.singleShot(100, partial(handle_menu, 7))
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
    def mock_get_polarization_logs_callback(name):  # pylint: disable=unused-argument
        parameters = {"PolarizationState": "NSF", "FlippingRatio": "", "FlippingRatioSampleLog": "", "PSDA": "1.3"}
        return parameters

    mdelist.get_polarization_logs_callback = mock_get_polarization_logs_callback

    # mock callback to save polarization parameters
    def mock_save_polarization_logs_callback(name, parameters):
        assert name == "mde1"
        assert parameters["PolarizationState"] == "NSF"
        assert parameters["PolarizationDirection"] == "Pz"
        assert parameters["FlippingRatioSampleLog"] == ""
        assert parameters["FlippingRatio"] == "20"
        assert parameters["PSDA"] == "1.3"

    mdelist.save_polarization_logs_callback = mock_save_polarization_logs_callback

    item = mdelist.item(0)

    # This is to handle the mdelist menu
    def handle_menu(action_number):
        menu = mdelist.findChild(QMenu)
        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # This is to handle the polarization dialog
    def handle_polarization_dialog(mdelist):
        dialog = mdelist.findChild(QDialog)
        apply_btn = dialog.findChild(QPushButton)
        flipping_ratio = dialog.findChild(QLineEdit)
        qtbot.keyClicks(flipping_ratio, "20")
        qtbot.keyClick(apply_btn, Qt.Key_Enter)

    # select the item
    item = mdelist.item(0)
    assert item.text() == "mde1"

    # click on the menu and polarization dialog
    QTimer.singleShot(100, partial(handle_menu, 5))
    QTimer.singleShot(400, partial(handle_polarization_dialog, mdelist))
    qtbot.mouseClick(mdelist.viewport(), Qt.MouseButton.LeftButton, pos=mdelist.visualItemRect(item).center())

    # unset data
    assert mdelist._data_nsf is None  # pylint: disable=protected-access
