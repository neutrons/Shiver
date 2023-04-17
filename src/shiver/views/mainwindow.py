"""
Main Qt window for shiver
"""

from qtpy.QtWidgets import QVBoxLayout, QWidget, QTabWidget
from mantidqt.widgets.algorithmprogress import AlgorithmProgressWidget
from shiver.presenters.histogram import HistogramPresenter
from shiver.models.histogram import HistogramModel
from shiver.views.histogram import Histogram
from shiver.presenters.generate import GeneratePresenter
from shiver.models.generate import GenerateModel
from shiver.views.generate import Generate


class MainWindow(QWidget):
    """Main shiver widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        tabs = QTabWidget()

        histogram = Histogram(self)
        histogram_model = HistogramModel()
        self.histogram_presenter = HistogramPresenter(histogram, histogram_model)
        tabs.addTab(histogram, "Main")

        generate = Generate(self)
        generate_model = GenerateModel()
        GeneratePresenter(generate, generate_model)
        tabs.addTab(generate, "Generate")

        # Disable unfinished tab for first release
        tabs.setTabVisible(1, False)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(AlgorithmProgressWidget(self))
        self.setLayout(layout)

        # register child widgets to make testing easier
        self.histogram = histogram
        self.generate = generate
