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
from shiver.views.refine_ub import RefineUBView
from shiver.models.help import help_function
from shiver.views.configuration import ConfigurationView
from shiver.presenters.configuration import ConfigurationPresenter
from shiver.models.configuration import ConfigurationModel


class MainWindow(QWidget):
    """Main shiver widget"""

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config
        self.tabs = QTabWidget()
        histogram = Histogram(self)
        histogram_model = HistogramModel()
        self.histogram_presenter = HistogramPresenter(histogram, histogram_model)
        self.tabs.addTab(histogram, "Main")

        generate = Generate(self)
        generate_model = GenerateModel()
        self.generate_presenter = GeneratePresenter(generate, generate_model)
        self.tabs.addTab(generate, "Generate")

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        # Help button
        conf_button = QPushButton("Configuration Settings")
        conf_button.clicked.connect(self.conf_button)

        # Help button
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.handle_help)

        # AlgorithmProgress with custom button text
        apw = AlgorithmProgressWidget(self)
        apw.findChild(QPushButton).setText("Algorithm progress details")

        hor_layout = QHBoxLayout()
        hor_layout.addWidget(conf_button)
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
        elif isinstance(open_tab, RefineUBView):
            context = "refine_ub"
        else:
            context = ""
        help_function(context=context)

    def conf_button(self):
        """
        start the configuration variable form
        """

        config_view = ConfigurationView()
        config_model = ConfigurationModel()
        ConfigurationPresenter(config_view, config_model, self.config)

        # open the dialog
        dialog = config_view.start_dialog()
        # for testing
        # self.active_dialog = dialog
        dialog.exec_()
