"""PyQt widget for the histogram tab input workspaces"""
from functools import partial
from enum import Enum
from qtpy.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QLabel,
    QMenu,
    QAction,
    QInputDialog,
    QAbstractItemView,
)
from qtpy.QtCore import Qt, QSize, Signal
from qtpy.QtGui import QIcon, QPixmap

Frame = Enum("Frame", {"None": 1000, "QSample": 1001, "QLab": 1002, "HKL": 1003})


class InputWorkspaces(QGroupBox):
    """MDE and Normalization workspace widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Input data in memory")

        self.mde_workspaces = MDEList(parent=self, WStype="mde")
        self.norm_workspaces = NormList(parent=self, WStype="norm")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("MDE name"))
        layout.addWidget(self.mde_workspaces, stretch=2)
        layout.addWidget(QLabel("Normalization"))
        layout.addWidget(self.norm_workspaces, stretch=1)
        self.setLayout(layout)

    def add_ws(self, name, ws_type, frame):
        """Adds a workspace to the list if it is of the correct type"""
        self.mde_workspaces.add_ws(name, ws_type, frame)
        self.norm_workspaces.add_ws(name, ws_type, frame)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.mde_workspaces.del_ws(name)
        self.norm_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.mde_workspaces.clear()
        self.norm_workspaces.clear()


class ADSList(QListWidget):
    """List widget that will add and remove items from the ADS"""

    def __init__(self, parent=None, WStype=None):
        super().__init__(parent)
        self.ws_type = WStype
        self.setSortingEnabled(True)

    def add_ws(self, name, ws_type, frame):  # pylint: disable=unused-argument
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            self.addItem(QListWidgetItem(name))

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        for item in self.findItems(name, Qt.MatchExactly):
            self.takeItem(self.indexFromItem(item).row())


class NormList(ADSList):
    """List widget that will add and remove items from the ADS"""

    def __init__(self, parent=None, WStype=None):
        super().__init__(parent, WStype)
        self.rename_workspace_callback = None
        self.delete_workspace_callback = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def contextMenu(self, pos):  # pylint: disable=invalid-name
        """right-click event handler"""
        selected_ws = self.itemAt(pos)
        if selected_ws is None:
            return

        selected_ws = selected_ws.text()

        menu = QMenu(self)

        rename = QAction("Rename")
        rename.triggered.connect(partial(self.rename_ws, selected_ws))

        menu.addAction(rename)

        delete = QAction("Delete")
        delete.triggered.connect(partial(self.delete_ws, selected_ws))

        menu.addAction(delete)

        menu.exec_(self.mapToGlobal(pos))
        menu.setParent(None)  # Allow this QMenu instance to be cleaned up

    def rename_ws(self, name):
        """method to rename the currently selected workspace"""
        dialog = QInputDialog(self)
        dialog.setLabelText(f"Rename {name} to:")
        dialog.setTextValue(name)
        dialog.setOkButtonText("Rename")
        if not dialog.exec_():
            return

        if self.rename_workspace_callback:
            self.rename_workspace_callback(name, dialog.textValue())  # pylint: disable=not-callable

    def delete_ws(self, name):
        """method to delete the currently selected workspace"""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable

    def set_selected(self, name):
        """method to set the selected workspace as selected

        Parameters
        ----------
        name : str
            Name of the workspace to select
        """
        item = self.findItems(name, Qt.MatchExactly)[0]
        self.setCurrentItem(item)

    def deselect_all(self):
        """reset the list"""
        for item in self.selectedItems():
            item.setSelected(False)


class MDEList(ADSList):
    """Special workspace list widget so that we can add a menu to each item"""

    def __init__(self, parent=None, WStype=None):
        super().__init__(parent, WStype)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self._data = None
        self._background = None
        self.rename_workspace_callback = None
        self.delete_workspace_callback = None
        self.create_corrections_tab_callback = None
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

    def add_ws(self, name, ws_type, frame):
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            frame_type = Frame[frame]
            item = QListWidgetItem(name, type=frame_type.value)
            self._set_q_icon(item)
            self.addItem(item)

    def contextMenu(self, pos):  # pylint: disable=invalid-name
        """right-click event handler"""
        selected_ws = self.itemAt(pos)
        if selected_ws is None:
            return

        frame_value = selected_ws.type()
        selected_ws = selected_ws.text()

        menu = QMenu(self)

        if selected_ws != self._data and frame_value == Frame.QSample.value:
            set_data = QAction("Set as data")
            set_data.triggered.connect(partial(self.set_data, selected_ws))
            menu.addAction(set_data)

        if selected_ws == self._background:
            background = QAction("Unset as background")
            background.triggered.connect(partial(self.unset_background, selected_ws))
        else:
            background = QAction("Set as background")
            background.triggered.connect(partial(self.set_background, selected_ws))

        menu.addAction(background)
        menu.addSeparator()

        # data properties
        provenance = QAction("Provenance")  # To be implemented
        parameters = QAction("Set sample parameters")  # To be implemented
        corrections = QAction("Set corrections")
        corrections.triggered.connect(partial(self.set_corrections, selected_ws))

        menu.addAction(provenance)
        menu.addAction(parameters)
        menu.addAction(corrections)
        menu.addSeparator()

        # data manipulation
        rename = QAction("Rename")
        rename.triggered.connect(partial(self.rename_ws, selected_ws))
        menu.addAction(rename)

        delete = QAction("Delete")
        delete.triggered.connect(partial(self.delete_ws, selected_ws))
        menu.addAction(delete)

        menu.exec_(self.mapToGlobal(pos))
        menu.setParent(None)  # Allow this QMenu instance to be cleaned up

    def set_data(self, name):
        """method to set the selected workspace as 'data'"""
        if self._data:
            self._set_q_icon(self.findItems(self._data, Qt.MatchExactly)[0])

        if self._background == name:
            self._background = None
        self._data = name
        item = self.findItems(name, Qt.MatchExactly)[0]
        item.setIcon(get_icon("data"))

    def set_background(self, name):
        """method to set the selected workspace as 'background'"""
        if self._background:
            self._set_q_icon(self.findItems(self._background, Qt.MatchExactly)[0])

        self._background = name
        if self._data == name:
            self._data = None
        self.findItems(name, Qt.MatchExactly)[0].setIcon(get_icon("background"))

    def unset_background(self, name):
        """method to unset the selected workspace as 'background'"""
        self._set_q_icon(self.findItems(name, Qt.MatchExactly)[0])

        self._background = None

    def set_corrections(self, name):
        """method to open the correction tab to apply correction for given workspace"""
        if self.create_corrections_tab_callback:
            self.create_corrections_tab_callback(name)  # pylint: disable=not-callable

    def rename_ws(self, name):
        """method to rename the currently selected workspace"""
        dialog = QInputDialog(self)
        dialog.setLabelText(f"Rename {name} to:")
        dialog.setTextValue(name)
        dialog.setOkButtonText("Rename")
        if not dialog.exec_():
            return

        if self.rename_workspace_callback:
            self.rename_workspace_callback(name, dialog.textValue())  # pylint: disable=not-callable

        if self._data == name:
            self._data = None
        if self._background == name:
            self._background = None

    def delete_ws(self, name):
        """method to delete the currently selected workspace"""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable

        if self._data == name:
            self._data = None
        if self._background == name:
            self._background = None

    def _set_q_icon(self, item):
        item.setIcon(get_icon(Frame(item.type()).name))

    @property
    def data(self):
        """return the workspace name set as data"""
        return self._data

    @property
    def background(self):
        """return the workspace name set as background (optional, may be None)"""
        return self._background

    def unset_all(self):
        """reset the list"""
        # NOTE: DO NOT change the order, this is the correct logic to unset
        #       the data and background
        if self.data is not None:
            self.set_background(self.data)

        if self.background is not None:
            self.unset_background(self.background)


class HistogramWorkspaces(QGroupBox):
    """Histogram workspaces widget"""

    histogram_selected_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram data in memory")

        self.histogram_workspaces = ADSList(parent=self, WStype="mdh")
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)

        self.histogram_workspaces.itemClicked.connect(self.on_item_clicked)

    def add_ws(self, name, ws_type, frame):
        """Adds a workspace to the list if it is of the correct type"""
        self.histogram_workspaces.add_ws(name, ws_type, frame)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.histogram_workspaces.clear()

    def on_item_clicked(self, item):
        """method to emit a signal when a workspace is selected"""
        self.histogram_selected_signal.emit(item.text())


def get_icon(name: str) -> QIcon:
    """return a icon for the given name"""
    if name == "data":
        return QIcon(
            QPixmap(
                ["5 7 2 1", "N c None", ". c #0000FF", "...NN", ".NN.N", ".NNN.", ".NNN.", ".NNN.", ".NN.N", "...NN"]
            ).scaled(QSize(10, 14))
        )

    if name == "background":
        return QIcon(
            QPixmap(
                [
                    "5 7 2 1",
                    "N c None",
                    ". c #0000FF",
                    "....N",
                    ".NNN.",
                    ".NNN.",
                    "....N",
                    ".NNN.",
                    ".NNN.",
                    "....N",
                ]
            ).scaled(QSize(10, 14))
        )

    if name == "QSample":
        return QIcon(
            QPixmap(
                [
                    "10 7 2 1",
                    "N c None",
                    ". c #000000",
                    "N...NNNNNN",
                    ".NNN.NNNNN",
                    ".NNN.NN...",
                    ".NNN.N.NNN",
                    ".N.N.NN..N",
                    ".NN.NNNNN.",
                    "N..N.N...N",
                ]
            ).scaled(QSize(20, 14))
        )

    if name == "QLab":
        return QIcon(
            QPixmap(
                [
                    "10 7 2 1",
                    "N c None",
                    ". c #000000",
                    "N...NNNNNN",
                    ".NNN.NNNNN",
                    ".NNN.N.NNN",
                    ".NNN.N.NNN",
                    ".N.N.N.NNN",
                    ".NN.NN.NNN",
                    "N..N.N....",
                ]
            ).scaled(QSize(20, 14))
        )

    raise ValueError(f"{name} doesn't correspond to a valid icon")
