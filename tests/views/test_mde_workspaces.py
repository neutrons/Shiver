"""UI tests for the MDE list tables"""
from functools import partial
from qtpy.QtWidgets import QMenu, QInputDialog, QLineEdit
from qtpy.QtCore import Qt, QTimer
from shiver.views.workspace_tables import MDEList, Frame, get_icon


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

    QTimer.singleShot(100, partial(handle_menu, 7))
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

    QTimer.singleShot(100, partial(handle_menu, 6))
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

    qtbot.wait(7000)
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

    mde_table.set_data("qsample", "unpolarized")
    item1 = mde_table.item(1)
    assert item1.icon().pixmap(10, 14).toImage() == get_icon("unpolarized").pixmap(10, 14).toImage()

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
