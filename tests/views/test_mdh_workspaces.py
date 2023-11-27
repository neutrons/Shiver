"""UI tests for the MDH list tables"""
from functools import partial
from qtpy.QtWidgets import QApplication, QMenu, QFileDialog, QLineEdit
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QContextMenuEvent
from mantid.simpleapi import CreateMDHistoWorkspace  # pylint: disable=no-name-in-module
from mantidqt.widgets.sliceviewer.views.view import SliceViewerView
import matplotlib.pyplot as plt
from shiver.views.workspace_tables import MDHList


def handle_menu(qtbot, widget, action_number):
    """Handle the file menu"""
    menu = widget.findChild(QMenu)

    for _ in range(action_number):
        qtbot.keyClick(menu, Qt.Key_Down)
    qtbot.keyClick(menu, Qt.Key_Enter)


def test_mdh_workspaces_menu(qtbot):
    """Tests the MDHisto table, saving and delete"""
    mdh_table = MDHList()
    qtbot.addWidget(mdh_table)
    mdh_table.show()

    def mock_call(ws_name, ndims):
        return f"full {ws_name}: {ndims}", {"min": None, "max": None}

    mdh_table.get_display_name_and_intensity_limits = mock_call

    mdh_table.add_ws("mdh1", "mdh", "HKL", 1)
    mdh_table.add_ws("mdh2", "mdh", "HKL", 2)
    mdh_table.add_ws("mdh3", "mdh", "HKL", 3)

    assert mdh_table.count() == 3

    qtbot.wait(100)

    # This is to handle the file dialog
    def handle_dialog(filename):
        dialog = mdh_table.findChild(QFileDialog)
        line_edit = dialog.findChild(QLineEdit)
        qtbot.keyClicks(line_edit, filename)
        qtbot.wait(100)
        qtbot.keyClick(line_edit, Qt.Key_Enter)

    # right-click first item and select "Save Script"
    save_script = []

    def save_script_callback(name, filename):
        save_script.append((name, filename))

    mdh_table.save_script_callback = save_script_callback

    item = mdh_table.item(0)
    assert item.text() == "mdh1"

    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 5))
    QTimer.singleShot(200, partial(handle_dialog, "script.py"))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    qtbot.wait(500)
    assert len(save_script) == 1
    assert save_script[0][0] == "mdh1"
    assert save_script[0][1].endswith("script.py")

    # right-click first item and select "Save NEXUS Data"
    save = []

    def save_callback(name, filename):
        save.append((name, filename))

    mdh_table.save_callback = save_callback

    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 6))
    QTimer.singleShot(200, partial(handle_dialog, "workspace.nxs"))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    qtbot.wait(500)
    assert len(save) == 1
    assert save[0][0] == "mdh1"
    assert save[0][1].endswith("workspace.nxs")

    # right-click first item and select "Save ASCII data"
    save_ascii = []

    def save_ascii_callback(name, filename):
        save_ascii.append((name, filename))

    mdh_table.save_ascii_callback = save_ascii_callback

    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 7))
    QTimer.singleShot(200, partial(handle_dialog, "workspace.txt"))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    # right-click first item and select "Delete"
    deleted = []

    def delete_callback(name):
        deleted.append(name)

    mdh_table.delete_workspace_callback = delete_callback

    item = mdh_table.item(0)
    assert item.text() == "mdh1"

    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 8))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    qtbot.wait(200)
    assert len(deleted) == 1
    assert deleted[0] == "mdh1"

    qtbot.wait(100)


def test_mdh_plotting_1d(qtbot):
    """Tests the 1D plotting"""

    # Create workspaces in mantid, needed for plots
    CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-10,10,-1,1,-1,1,-1,1",
        SignalInput=range(10),
        ErrorInput=[1] * 10,
        NumberOfBins="10,1,1,1",
        Names=["[H,0,0]", "[0,K,L]", "[0,0,L]", "DeltaE"],
        Units="in 1 A^-1,in 1 A^-1,in 1 A^-1,meV",
        Frames="HKL,HKL,HKL,General Frame",
        OutputWorkspace="Plot 1D",
    )

    mdh_table = MDHList()

    def mock_call(ws_name, ndims):
        return f"full {ws_name}: {ndims}", {"min": None, "max": None}

    mdh_table.get_display_name_and_intensity_limits = mock_call

    qtbot.addWidget(mdh_table)
    mdh_table.show()

    mdh_table.add_ws("Plot 1D", "mdh", "HKL", 1)
    assert mdh_table.count() == 1

    qtbot.wait(100)

    item = mdh_table.item(0)
    assert item.text() == "Plot 1D"

    # Select "Plot 1D"
    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 1))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )
    qtbot.wait(500)

    figure = plt.gcf()

    assert len(figure.axes) == 1
    assert len(figure.axes[0].lines) == 1

    # Select "Overplot 1D"
    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 2))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )
    qtbot.wait(500)

    assert len(figure.axes[0].lines) == 2

    qtbot.wait(100)

    # Select "Plot 1D with Errors"
    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 3))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )
    qtbot.wait(100)

    figure2 = plt.gcf()
    assert figure is not figure2

    assert len(figure2.axes) == 1
    assert len(figure2.axes[0].lines) == 1

    # Select "Overplot 1D with Errors"
    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 4))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )
    qtbot.wait(100)

    assert len(figure2.axes[0].lines) == 2


def test_mdh_plotting_2d(qtbot):
    """Tests the 2D plotting, colorfill plot or sliceviewer"""
    CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-10,10,-1,1,-1,1,-2,2",
        SignalInput=range(16),
        ErrorInput=[1] * 16,
        NumberOfBins="4,1,1,4",
        Names=["[H,0,0]", "[0,K,L]", "[0,0,L]", "DeltaE"],
        Units="in 1 A^-1,in 1 A^-1,in 1 A^-1,meV",
        Frames="HKL,HKL,HKL,General Frame",
        OutputWorkspace="Plot 2D",
    )

    mdh_table = MDHList()

    def mock_call(ws_name, ndims):
        return f"full {ws_name}: {ndims}", {"min": None, "max": None}

    mdh_table.get_display_name_and_intensity_limits = mock_call

    qtbot.addWidget(mdh_table)
    mdh_table.show()

    mdh_table.add_ws("Plot 2D", "mdh", "HKL", 2)
    assert mdh_table.count() == 1

    qtbot.wait(100)

    item = mdh_table.item(0)
    assert item.text() == "Plot 2D"

    # colorfill
    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 1))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    qtbot.wait(500)

    figure = plt.gcf()
    assert len(figure.axes) == 2  # pcolormesh and colorbar
    assert figure.axes[0].pcolormesh

    # sliceviewer
    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 2))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    qtbot.wait(200)

    slice_viewer = mdh_table.findChild(SliceViewerView)
    assert slice_viewer is not None
    assert slice_viewer.isVisible()
    slice_viewer.close()


def test_mdh_plotting_3d(qtbot):
    """Tests the 3D plotting, should just open sliceviewer"""

    CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-10,10,-10,10,-1,1,-2,2",
        SignalInput=range(8),
        ErrorInput=[1] * 8,
        NumberOfBins="2,2,1,2",
        Names=["[H,0,0]", "[0,K,L]", "[0,0,L]", "DeltaE"],
        Units="in 1 A^-1,in 1 A^-1,in 1 A^-1,meV",
        Frames="HKL,HKL,HKL,General Frame",
        OutputWorkspace="Plot 3D",
    )

    mdh_table = MDHList()

    def mock_call(ws_name, ndims):
        return f"full {ws_name}: {ndims}", {"min": None, "max": None}

    mdh_table.get_display_name_and_intensity_limits = mock_call

    qtbot.addWidget(mdh_table)
    mdh_table.show()

    mdh_table.add_ws("Plot 3D", "mdh", "HKL", 3)
    assert mdh_table.count() == 1

    qtbot.wait(100)

    item = mdh_table.item(0)
    assert item.text() == "Plot 3D"

    QTimer.singleShot(100, partial(handle_menu, qtbot, mdh_table, 1))

    QApplication.postEvent(
        mdh_table.viewport(), QContextMenuEvent(QContextMenuEvent.Mouse, mdh_table.visualItemRect(item).center())
    )

    qtbot.wait(200)

    slice_viewer = mdh_table.findChild(SliceViewerView)
    assert slice_viewer is not None
    assert slice_viewer.isVisible()
    slice_viewer.close()
