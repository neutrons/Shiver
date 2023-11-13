from mantidqt.widgets.sliceviewer.presenters.presenter import SliceViewer
from mantidqt.widgets.workspacedisplay.table.presenter import TableWorkspaceDisplay
from mantidqt.widgets.workspacedisplay.table.view import TableWorkspaceDisplayView
from mantidqt.widgets.workspacedisplay.table.presenter_base import TableWorkspaceDataPresenterBase

from shiver.views.refine_ub import RefineUBView, PeaksTableModel
from shiver.models.refine_ub import RefineUBModel


class PeaksTableWorkspaceDataPresenterStandard(TableWorkspaceDataPresenterBase):
    def load_data(self, table):
        table.model().load_data(self.model)

    def update_column_headers(self):
        self.view.model().setHorizontalHeaderLabels(["Refine", "Recenter", "H", "K", "L"])


class PeaksTableWorkspaceDisplay(TableWorkspaceDisplay):
    def __init__(self, ws, model, view=None, parent=None):
        super().__init__(ws, parent, model=model, view=view)

    def create_table(self, ws, parent, window_flags, model, view, batch):
        table_model = PeaksTableModel(parent=parent, data_model=model)

        view = (
            view
            if view
            else TableWorkspaceDisplayView(
                presenter=self, parent=parent, window_flags=window_flags, table_model=table_model
            )
        )
        self.presenter = PeaksTableWorkspaceDataPresenterStandard(model, view)
        view.set_context_menu_actions(view)
        return view, model


class RefineUB:
    def __init__(self, mdh, mde, model=None, view=None, parent=None):
        self.model = model if model else RefineUBModel(mdh, mde)
        self.sv = SliceViewer(self.model.get_mdh())
        self.peaks_table = PeaksTableWorkspaceDisplay(
            self.model.get_peaks_ws(), model=self.model.get_PeaksTableWorkspaceDisplayModel()
        )
        self.view = view if view else RefineUBView(self.sv, self.peaks_table, parent)

        self.view.recenter_peaks.clicked.connect(self.recenter)
        self.view.populate_peaks.clicked.connect(self.populate)

    def recenter(self):
        self.peaks_table.model.recenter_rows(self.peaks_table.view.model().recenter_rows())

    def populate(self, checked):
        if checked:
            self.sv._create_peaks_presenter_if_necessary().overlay_peaksworkspaces([self.model.get_peaks_ws_name()])
        else:
            self.sv._create_peaks_presenter_if_necessary().overlay_peaksworkspaces([])
