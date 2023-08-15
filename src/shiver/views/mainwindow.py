"""
Main Qt window for shiver
"""

from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget, QTabWidget, QPushButton, QMessageBox
from mantidqt.widgets.algorithmprogress import AlgorithmProgressWidget
from shiver.presenters.histogram import HistogramPresenter
from shiver.models.histogram import HistogramModel
from shiver.views.histogram import Histogram
from shiver.presenters.generate import GeneratePresenter
from shiver.models.generate import GenerateModel
from shiver.views.generate import Generate
from shiver.views.corrections import Corrections
from shiver.models.help import help_function
from shiver.models.configuration import ConfigurationModel


class MainWindow(QWidget):
    """Main shiver widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.config = ConfigurationModel()
        if not self.config.is_valid():
            conf_dialog = QMessageBox(self)
            conf_dialog.setWindowTitle("Error with configuration settings!")
            msg = (
                f"Check and update your file: {self.config.config_file_path}",
                "with the latest settings found here:",
                f"{self.config.template_file_path} and start the application again.",
            )
            conf_dialog.setText(" ".join(msg))
            conf_dialog.exec()
            return

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
        """
        get current tab type and open the corresponding help page
        """
        open_tab = self.tabs.currentWidget()
        if isinstance(open_tab, Histogram):
            context = "histogram"
        elif isinstance(open_tab, Generate):
            context = "generate"
        elif isinstance(open_tab, Corrections):
            context = "corrections"
        else:
            context = ""
        help_function(context=context)
