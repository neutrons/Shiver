"""PyQt widget for the raw data selection"""

import os
import glob

from qtpy.QtWidgets import (
    QWidget,
    QGroupBox,
    QFileDialog,
    QPushButton,
    QListWidget,
    QLineEdit,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QAbstractItemView,
)
from .invalid_styles import INVALID_QLISTWIDGET


class RawData(QGroupBox):
    """Raw data selection widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Raw data")

        self.directory = None

        self.browse = QPushButton("Browse")
        self.browse.setToolTip("Open dialog to browse to raw data folder.")
        self.browse.clicked.connect(self._browse)

        self.path = QLineEdit()
        self.path.setToolTip("Path to the raw data.")
        self.path.editingFinished.connect(self._path_edited)

        path_line = QWidget()
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path"))
        path_layout.addWidget(self.path)
        path_layout.addWidget(self.browse)
        path_line.setLayout(path_layout)

        self.files = QListWidget()
        self.files.setToolTip("List of raw data files in the current folder.")
        self.files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.files.setSortingEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(path_line)
        layout.addWidget(self.files)
        self.setLayout(layout)

        self.selected_list_from_oncat = None

        # mandatory field check its state
        # at least one item should be selected
        self.files.itemSelectionChanged.connect(self.check_file_input)

    def _path_edited(self):
        if self.path.text() != self.directory:
            self._update_file_list(self.path.text())

    def _browse(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Open Directory", self.directory, options=QFileDialog.DontUseNativeDialog
        )
        if directory:
            self._update_file_list(directory)

    def _update_file_list(self, directory):
        self.directory = directory
        self.path.setText(directory)
        self.files.clear()
        filenames = list(glob.iglob(os.path.join(directory, "*.nxs.h5")))
        # also support legacy format (if present)
        filenames += list(glob.iglob(os.path.join(directory, "*_event.nxs")))
        self.files.addItems([os.path.basename(f) for f in filenames])

    def set_field_invalid_state(self, item):
        """if parent exists then call the corresponding function"""
        if self.parent():
            self.parent().set_field_invalid_state(item)
        item.setStyleSheet(INVALID_QLISTWIDGET)

    def set_field_valid_state(self, item):
        """remove the item from the field_error list and its invalid style, if it was previously invalid
        and enable the corresponding button"""
        if self.parent():
            self.parent().set_field_valid_state(item)
        item.setStyleSheet("")

    def check_file_input(self):
        """check whether any files are selected"""
        state = self.selected_list_from_oncat is not None or len(self.files.selectedItems()) > 0
        # invalid /valid cases
        if state:
            self.set_field_valid_state(self.files)
        else:
            self.set_field_invalid_state(self.files)
        return state

    def get_selected(self, use_grouped=False):
        """Return a list of the full path of the files selected"""
        # if the selection is from oncat, use the oncat one
        if use_grouped:
            return self.selected_list_from_oncat

        # generate a list based on manual selection
        return [os.path.join(self.directory, f.text()) for f in self.files.selectedItems()]

    def set_selected(self, filenames: list):
        """Set the selected files.

        Parameters
        ----------
        filenames : list
            list of filenames with full path.

        Notes
        -----
        1. Expects a list of full file paths
        2. This makes the assumption that all the files for in the same directory.
        """
        # deal with empty list
        if not filenames:
            return

        # extract and set the common path
        self._update_file_list(os.path.dirname(filenames[0]))

        # set the selection
        # NOTE: the nested list should be flatten out before sending in as we are
        #       not supporting grouped files in this widget at the moment.
        selected = {os.path.basename(f) for f in filenames}

        for i in range(self.files.count()):
            item = self.files.item(i)
            if item.text() in selected:
                item.setSelected(True)

    def as_dict(self, use_grouped=False):
        """Return a dictionary of the current state"""
        return {"filename": self.get_selected(use_grouped=use_grouped)}

    def populate_from_dict(self, config_dict: dict):
        """Populate the widget from a dictionary"""
        filenames_str = config_dict.get("filename", "")

        # do nothing if the string is empty
        if not filenames_str:
            return

        # convert string format to list
        filenames_list = filename_str_to_list(filenames_str)

        # flatten the list
        # NOTE: since this widget does not support displaying grouped files at
        #       the moment, we will flatten the list first.
        filename_list_flattened = []
        for filename in filenames_list:
            if isinstance(filename, list):
                filename_list_flattened += filename
            elif isinstance(filename, str):
                filename_list_flattened.append(filename)

        # set the selection
        self.set_selected(filename_list_flattened)


def filename_str_to_list(filenames_str):
    """Convert a string of filenames to a list.

    Parameters
    ----------
    filenames_str : str
        String of filenames separated by a comma. Grouped filenames are connected
        with "+", i.e.
        "file1.nxs.h5,file2.nxs.h5+file3.nxs.h5,file4.nxs.h5"
        to
        ["file1.nxs.h5", ["file2.nxs.h5", "file3.nxs.h5"], "file4.nxs.h5"]
    """
    # check if the string is empty
    if not filenames_str:
        return []

    # process str to list
    filename_list = []

    for filename in filenames_str.split(","):
        if "+" in filename:
            filename_list.append([temp.strip() for temp in filename.split("+")])
        else:
            filename_list.append(filename.strip())

    return filename_list
