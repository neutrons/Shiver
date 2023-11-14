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
        self.view = view if view else RefineUBView(self.sv, self.peaks_table, self, parent)
        self.update_lattice()

        self.view.connect_recenter_peaks(self.recenter)
        self.view.connect_populate_peaks(self.populate)
        self.view.connect_predict_peaks(self.predict)
        self.view.connect_refine(self.refine)
        self.view.connect_refine_orientation(self.refine_orientation)

        self.remake_slice_callback = None

    def update_workspaces(self, mdh, mde):
        self.view.remove_sv()
        self.model.update_workspaces(mdh, mde)
        self.sv = SliceViewer(self.model.get_mdh())
        self.view.set_sv(self.sv)

    def recenter(self):
        self.peaks_table.model.recenter_rows(self.peaks_table.view.model().recenter_rows())

    def refine_orientation(self):
        self.peaks_table.model.refine_orientation(self.peaks_table.view.model().refine_rows())
        self.update_lattice()
        self.model.update_mde_with_new_ub()
        self.view.remove_sv()
        self.remake_slice()

    def refine(self):
        self.peaks_table.model.refine(self.peaks_table.view.model().refine_rows())
        self.update_lattice()
        self.model.update_mde_with_new_ub()
        self.view.remove_sv()
        self.remake_slice()

    def populate(self, checked):
        if checked:
            self.sv._create_peaks_presenter_if_necessary().overlay_peaksworkspaces([self.model.get_peaks_ws_name()])
        else:
            self.sv._create_peaks_presenter_if_necessary().overlay_peaksworkspaces([])

    def predict(self):
        self.model.predict_peaks()

    def update_lattice(self):
        self.view.set_lattice(self.peaks_table.model.get_lattice_parameters())

    def remake_slice(self):
        if self.remake_slice_callback:
            self.remake_slice_callback()
