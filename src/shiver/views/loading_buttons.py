"""PyQt widget for the histogram tab"""
import importlib
import os
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QInputDialog,
)


class LoadingButtons(QWidget):
    """Buttons for Loading"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.load_dataset = QPushButton("Load dataset")
        self.gen_dataset = QPushButton("Generate dataset")
        self.load_mde = QPushButton("Load MDE")
        self.load_norm = QPushButton("Load normalization")

        layout = QVBoxLayout()
        layout.addWidget(self.load_dataset)
        layout.addWidget(self.gen_dataset)
        layout.addWidget(self.load_mde)
        layout.addWidget(self.load_norm)
        layout.addStretch()
        self.setLayout(layout)

        self.load_dataset.clicked.connect(self._on_load_dataset_click)
        self.load_mde.clicked.connect(self._on_load_mde_click)
        self.load_norm.clicked.connect(self._on_load_norm_click)

        self.file_load_callback = None
        self.load_dataset_callback = None
        self.error_msg_callback = None

        # disable generate dataset button (not implemented for phase 1)
        self.gen_dataset.setEnabled(False)

    def _on_load_mde_click(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", "", "NeXus file (*.nxs);;All files (*)"
        )
        if filename and self.file_load_callback:
            self.file_load_callback("mde", filename)

    def _on_load_norm_click(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select one or more files to open", "", "NeXus file (*.nxs *.nx5);;All files (*)"
        )
        if filename and self.file_load_callback:
            self.file_load_callback("norm", filename)

    def _on_load_dataset_click(self):
        """Load a dataset from a Python file."""
        # get the file name
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select the Python file defines the dataset",
            "",
            "Python file (*.py);;All files (*)",
        )
        if not filename:
            return

        # import the function dynamically from given Python file
        data_set_list = self.extract_dataset_list(filename)

        if len(data_set_list) == 0:
            return

        if len(data_set_list) == 1:
            # no need to ask the user to select a dataset
            dataset_index = 0
        else:
            # pop up a dialog to ask the user to enter an integer to select a dataset
            # NOTE: pytest cannot find this widget as it is Qt's shortcut to create
            #       a input dialog without making a whole new class.
            dataset_index, success = QInputDialog.getInt(
                self,
                "Enter a dataset index)",  # title
                f"Index [0 - {len(data_set_list) - 1}]",  # label
                0,  # default value
                0,  # min
                len(data_set_list) - 1,  # max
            )
            if not success:
                return

        data_set = data_set_list[dataset_index]
        # import the function from the file
        if self.load_dataset_callback:
            self.load_dataset_callback(data_set)

    def extract_dataset_list(self, filename):
        """extract the dataset list from the given file.

        Parameters
        ----------
        filename : str
            the file name of the Python file that defines the dataset.

        Returns
        -------
        data_set_list : list
            a list of data set.
        """
        # import the function dynamically from given Python file
        module_name = os.path.splitext(os.path.basename(filename))[0]
        spec = importlib.util.spec_from_file_location(
            module_name,
            filename,
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            data_set_list = module.define_data_set()
        except Exception as error:  # pylint: disable=broad-except
            if self.error_msg_callback:
                self.error_msg_callback(f"Error: {error}")
            return []

        return data_set_list

    def connect_load_file(self, callback):
        """connect a function to the selection of a filename"""
        self.file_load_callback = callback

    def connect_load_dataset(self, callback):
        """connect a function to the selection of a dataset.

        Parameters
        ----------
        callback : function
            the function to be called when a dataset is selected.
        """
        self.load_dataset_callback = callback

    def connect_error_msg(self, callback):
        """connect a function to the error message.

        Parameters
        ----------
        callback : function
            the function to be called when an error message is needed.
        """
        self.error_msg_callback = callback
