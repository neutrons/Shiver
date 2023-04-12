"""PyQt widget for the histogram tab"""
from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
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

        self.load_mde.clicked.connect(self._on_load_mde_click)
        self.load_norm.clicked.connect(self._on_load_norm_click)

        self.file_load_callback = None

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

    def connect_load_file(self, callback):
        """connect a function to the selection of a filename"""
        self.file_load_callback = callback
