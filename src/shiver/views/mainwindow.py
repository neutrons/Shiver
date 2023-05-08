"""
Main Qt window for shiver
"""

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QPushButton
from mantidqt.widgets.algorithmprogress import AlgorithmProgressWidget
from shiver.presenters.histogram import HistogramPresenter
from shiver.models.histogram import HistogramModel
from shiver.views.histogram import Histogram
from shiver.presenters.generate import GeneratePresenter
from shiver.models.generate import GenerateModel
from shiver.views.generate import Generate
from shiver.views.corrections import Corrections
from shiver.models.help import help_function


class MainWindow(QWidget):
    """Main shiver widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.tabs = QTabWidget()

        histogram = Histogram(self)
        histogram_model = HistogramModel()
        self.histogram_presenter = HistogramPresenter(histogram, histogram_model)
        self.tabs.addTab(histogram, "Main")

        generate = Generate(self)
        generate_model = GenerateModel()
        GeneratePresenter(generate, generate_model)
        self.tabs.addTab(generate, "Generate")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        # Help button
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.handle_help)

        # AlgorithmProgress with custom button text
        apw = AlgorithmProgressWidget(self)
        apw.findChild(QPushButton).setText("Algorithm progress details")

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(help_button)
        hor_layout.addWidget(apw)

        layout.addLayout(hor_layout)

        self.setLayout(layout)

        # register child widgets to make testing easier
        self.histogram = histogram
        self.generate = generate

    def handle_help(self):
        cw = self.tabs.currentWidget()
        if isinstance(cw, Histogram):
            context = "histogram"
        elif isinstance(cw, Generate):
            context = "generate"
        elif isinstance(cw, Corrections):
            context = "corrections"
        else:
            context = ""
        help_function(context=context)
