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


class RawData(QGroupBox):
    """Raw data selection widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Raw data")

        self.directory = None

        self.browse = QPushButton("Browse")
        self.browse.clicked.connect(self._browse)

        self.path = QLineEdit()
        self.path.editingFinished.connect(self._path_edited)

        path_line = QWidget()
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Path"))
        path_layout.addWidget(self.path)
        path_layout.addWidget(self.browse)
        path_line.setLayout(path_layout)

        self.files = QListWidget()
        self.files.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.files.setSortingEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(path_line)
        layout.addWidget(self.files)
        self.setLayout(layout)

    def _path_edited(self):
        if self.path.text() != self.directory:
            self._update_file_list(self.path.text())

    def _browse(self):
        directory = QFileDialog.getExistingDirectory(self, "Open Directory", self.directory)
        if directory:
            self._update_file_list(directory)

    def _update_file_list(self, directory):
        self.directory = directory
        self.path.setText(directory)
        self.files.clear()
        filenames = glob.iglob(os.path.join(directory, "*.nxs.h5"))
        self.files.addItems([os.path.basename(f) for f in filenames])

    def get_selected(self):
        """Return a list of the full path of the files selected"""
        return [os.path.join(self.directory, f.text()) for f in self.files.selectedItems()]

    def set_selected(self, filenames):
        """Set the selected files

        Expects a list of full file paths

        This makes the assumption that all the files for in the same directory
        """

        if not filenames:
            return

        self._update_file_list(os.path.dirname(filenames[0]))

        selected = {os.path.basename(f) for f in filenames}

        for i in range(self.files.count()):
            item = self.files.item(i)
            if item.text() in selected:
                item.setSelected(True)