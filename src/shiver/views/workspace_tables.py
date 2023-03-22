"""PyQt widget for the histogram tab"""
from functools import partial
from qtpy.QtWidgets import (
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QLabel,
    QStyle,
    QMenu,
    QAction,
    QInputDialog,
    QAbstractItemView,
)
from qtpy.QtCore import Qt


class InputWorkspaces(QGroupBox):
    """MDE and Normalization workspace widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Input data in memory")

        self.mde_workspaces = MDEList(parent=self, WStype="mde")
        self.norm_workspaces = ADSList(parent=self, WStype="norm")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("MDE name"))
        layout.addWidget(self.mde_workspaces, stretch=2)
        layout.addWidget(QLabel("Normalization"))
        layout.addWidget(self.norm_workspaces, stretch=1)
        self.setLayout(layout)

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        self.mde_workspaces.add_ws(name, ws_type)
        self.norm_workspaces.add_ws(name, ws_type)

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

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        if ws_type == self.ws_type and name != "None":
            self.addItem(QListWidgetItem(name))

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        for item in self.findItems(name, Qt.MatchExactly):
            self.takeItem(self.indexFromItem(item).row())


class MDEList(ADSList):
    """Special workpace list widget so that we can add a menu to each item"""

    def __init__(self, parent=None, WStype=None):
        super().__init__(parent, WStype)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self._data = None
        self._background = None
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

        if selected_ws != self._data:
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
            self.findItems(self._data, Qt.MatchExactly)[0].setIcon(self.style().standardIcon(QStyle.SP_CustomBase))
        if self._background == name:
            self._background = None
        self._data = name
        self.findItems(name, Qt.MatchExactly)[0].setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))

    def set_background(self, name):
        """method to set the selected workspace as 'background'"""
        if self._background:
            self.findItems(self._background, Qt.MatchExactly)[0].setIcon(
                self.style().standardIcon(QStyle.SP_CustomBase)
            )
        self._background = name
        if self._data == name:
            self._data = None
        self.findItems(name, Qt.MatchExactly)[0].setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def unset_background(self, name):
        """method to unset the selected workspace as 'background'"""
        self.findItems(name, Qt.MatchExactly)[0].setIcon(self.style().standardIcon(QStyle.SP_CustomBase))
        self._background = None

    def rename_ws(self, name):
        """methed to rename the currently selected workspace"""
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
        """methed to delete the currently selected workspace"""
        if self.delete_workspace_callback:
            self.delete_workspace_callback(name)  # pylint: disable=not-callable

        if self._data == name:
            self._data = None
        if self._background == name:
            self._background = None

    @property
    def data(self):
        """return the workspace name set as data"""
        return self._data

    @property
    def background(self):
        """return the workspace name set as background (optional, may be None)"""
        return self._background


class HistogramWorkspaces(QGroupBox):
    """Histogram workspaces widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Histogram data in memory")

        self.histogram_workspaces = ADSList(parent=self, WStype="mdh")
        layout = QVBoxLayout()
        layout.addWidget(self.histogram_workspaces)
        self.setLayout(layout)

    def add_ws(self, name, ws_type):
        """Adds a workspace to the list if it is of the correct type"""
        self.histogram_workspaces.add_ws(name, ws_type)

    def del_ws(self, name):
        """Removes a workspace from the list if it is of the correct type"""
        self.histogram_workspaces.del_ws(name)

    def clear_ws(self):
        """Clears all workspaces from the lists"""
        self.histogram_workspaces.clear()
