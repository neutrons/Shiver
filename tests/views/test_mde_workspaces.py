"""UI tests for the MDE list tables"""
from functools import partial
from qtpy.QtWidgets import QApplication, QMenu, QInputDialog, QLineEdit
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QContextMenuEvent
from shiver.views.workspace_tables import MDEList, Frame, get_icon


def test_mde_workspaces_menu(qtbot):
    """Test the mde and norm lists"""
    mde_table = MDEList(WStype="mde")
    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("mde1", "mde", "QSample")
    mde_table.add_ws("mde2", "mde", "QSample")
    mde_table.add_ws("mde3", "mde", "QSample")

    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None

    qtbot.wait(100)

    # This is to handle the menu
    def handle_menu(action_number):
        menu = mde_table.findChild(QMenu)

        for _ in range(action_number):
            qtbot.keyClick(menu, Qt.Key_Down)
        qtbot.keyClick(menu, Qt.Key_Enter)

    # right-click first item and select "Set as data"
    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, 1))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde1"
    assert mde_table.background is None

    # right-click second item and select "Set as data"
    item = mde_table.item(1)
    assert item.text() == "mde2"

    QTimer.singleShot(100, partial(handle_menu, 1))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde2"
    assert mde_table.background is None

    # right-click third item and select "Set as background"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 2))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde2"
    assert mde_table.background == "mde3"

    # right-click third item and select "Set as data"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 1))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data == "mde3"
    assert mde_table.background is None

    # right-click third item and select "Set as background"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 1))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background == "mde3"

    # right-click third item and select "Unset as background"
    item = mde_table.item(2)
    assert item.text() == "mde3"

    QTimer.singleShot(100, partial(handle_menu, 2))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(100)
    assert mde_table.count() == 3
    assert mde_table.data is None
    assert mde_table.background is None

    # right-click first item and select "Delete"
    deleted = []

    def delete_callback(name):
        deleted.append(name)

    mde_table.delete_workspace_callback = delete_callback

    item = mde_table.item(0)
    assert item.text() == "mde1"

    QTimer.singleShot(100, partial(handle_menu, 7))

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

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

    QApplication.postEvent(
        mde_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mde_table.visualItemRect(item).center())
    )

    qtbot.wait(500)
    assert len(rename) == 1
    assert rename[0] == ("mde1", "new_ws_name")


def test_mde_workspaces_icon(qtbot):
    """test the changing of icons for q_sample, q_lab, data and background"""

    mde_table = MDEList(WStype="mde")

    qtbot.addWidget(mde_table)
    mde_table.show()

    mde_table.add_ws("qlab", "mde", "QLab")
    mde_table.add_ws("qsample", "mde", "QSample")

    item0 = mde_table.item(0)
    assert item0.text() == "qlab"
    assert item0.type() == Frame.QLab.value
    assert item0.icon().pixmap(20, 14).toImage() == get_icon("QLab").pixmap(20, 14).toImage()

    item1 = mde_table.item(1)
    assert item1.text() == "qsample"
    assert item1.type() == Frame.QSample.value
    assert item1.icon().pixmap(20, 14).toImage() == get_icon("QSample").pixmap(20, 14).toImage()

    mde_table.set_data("qsample")
    item1 = mde_table.item(1)
    assert item1.icon().pixmap(10, 14).toImage() == get_icon("data").pixmap(10, 14).toImage()

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
