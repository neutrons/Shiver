"""
Main Qt window for shiver
"""

from qtpy.QtWidgets import QVBoxLayout, QWidget, QTabWidget
from mantidqt.widgets.algorithmprogress import AlgorithmProgressWidget


class MainWindow(QWidget):
    """Main shiver widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        tabs = QTabWidget()

        histogram = QWidget()
        tabs.addTab(histogram, "Main")

        generate = QWidget()
        tabs.addTab(generate, "Generate")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(AlgorithmProgressWidget(self))
        self.setLayout(layout)
