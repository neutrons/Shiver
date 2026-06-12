"""PyQt widget for the raw data selection"""

import glob
import os
import re

from qtpy.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .invalid_styles import INVALID_QLINEEDIT, INVALID_QLISTWIDGET


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

        self.manual_selection = QLineEdit()
        self.manual_selection.setToolTip(
            "Select runs by number pattern, e.g. '1-3, 5:20:3' selects runs 1,2,3,5,8,11,14,17,20."
        )
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Manual selection"))
        manual_layout.addWidget(self.manual_selection)
        self.manual_select = QPushButton("Select")
        self.manual_select.setEnabled(False)
        self.manual_select.clicked.connect(self._manual_selection_apply)
        manual_layout.addWidget(self.manual_select)
        self.manual_deselect = QPushButton("Deselect")
        self.manual_deselect.setEnabled(False)
        self.manual_deselect.clicked.connect(self._manual_selection_deselect)
        manual_layout.addWidget(self.manual_deselect)
        manual_selection_widget = QWidget()
        manual_selection_widget.setLayout(manual_layout)

        layout = QVBoxLayout()
        layout.addWidget(path_line)
        layout.addWidget(self.files)
        layout.addWidget(manual_selection_widget)
        self.setLayout(layout)

        self.selected_list_from_oncat = None

        # mandatory field check its state
        # at least one item should be selected
        self.files.itemSelectionChanged.connect(self.check_file_input)
        self.manual_selection.textChanged.connect(self._on_manual_selection_changed)

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

    def _on_manual_selection_changed(self):
        text = self.manual_selection.text().strip()
        if not text:
            self.manual_select.setEnabled(False)
            self.manual_deselect.setEnabled(False)
            self.manual_selection.setStyleSheet("")
            return
        valid, _ = parse_run_numbers(text)
        self.manual_select.setEnabled(valid)
        self.manual_deselect.setEnabled(valid)
        if valid:
            self.manual_selection.setStyleSheet("")
        else:
            self.manual_selection.setStyleSheet(INVALID_QLINEEDIT)

    def _manual_selection_apply(self):
        text = self.manual_selection.text().strip()
        valid, run_numbers = parse_run_numbers(text)
        if not valid:
            return
        run_set = set(run_numbers)
        self.files.clearSelection()
        for i in range(self.files.count()):
            item = self.files.item(i)
            run_number = _extract_run_number(item.text())
            if run_number is not None and run_number in run_set:
                item.setSelected(True)

    def _manual_selection_deselect(self):
        text = self.manual_selection.text().strip()
        valid, run_numbers = parse_run_numbers(text)
        if not valid:
            return
        run_set = set(run_numbers)
        for i in range(self.files.count()):
            item = self.files.item(i)
            run_number = _extract_run_number(item.text())
            if run_number is not None and run_number in run_set:
                item.setSelected(False)

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
            self.files.clearSelection()
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


def _extract_run_number(filename):
    """Return the integer run number from a filename like INST_12345.nxs.h5, or None.

    Strips all extensions first (e.g. .nxs.h5), then returns the last underscore-
    delimited digit group, which is the run number in names like INST_12345 or
    INST_12345_event.
    """
    stem = filename
    while "." in stem:
        stem = stem.rsplit(".", 1)[0]
    matches = re.findall(r"_(\d+)", stem)
    return int(matches[-1]) if matches else None


def parse_run_numbers(text):
    """Parse a run-number pattern string.

    Supports single numbers, dash ranges (1-3), colon ranges with optional step
    (1:10:2), and comma-separated combinations.

    Returns (is_valid: bool, run_numbers: list[int]).
    """
    try:
        result = []
        for token in text.split(","):
            token = token.strip()
            if not token:
                continue
            if ":" in token:
                parts = [int(p) for p in token.split(":")]
                if len(parts) == 2:
                    result.extend(range(parts[0], parts[1] + 1))
                elif len(parts) == 3:
                    result.extend(range(parts[0], parts[1] + 1, parts[2]))
                else:
                    return False, []
            elif "-" in token:
                parts = [int(p) for p in token.split("-")]
                if len(parts) != 2:
                    return False, []
                result.extend(range(parts[0], parts[1] + 1))
            else:
                result.append(int(token))
        if not result:
            return False, []
        return True, result
    except (ValueError, TypeError):
        return False, []


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
