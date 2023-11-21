"""Presenter for the Refine UB widget"""

from mantidqt.widgets.sliceviewer.presenters.presenter import SliceViewer
from mantidqt.widgets.workspacedisplay.table.presenter import TableWorkspaceDisplay
from mantidqt.widgets.workspacedisplay.table.view import TableWorkspaceDisplayView
from mantidqt.widgets.workspacedisplay.table.presenter_base import TableWorkspaceDataPresenterBase
from mantidqt.widgets.observers.ads_observer import WorkspaceDisplayADSObserver

from shiver.views.refine_ub import RefineUBView, PeaksTableModel
from shiver.models.refine_ub import RefineUBModel


class PeaksTableWorkspaceDataPresenterStandard(TableWorkspaceDataPresenterBase):
    """Peaks table presenter"""

    def load_data(self, table):
        """load the peaks workspace in the QTable model"""
        table.model().load_data(self.model)

    def update_column_headers(self):
        """set the table column headers"""
        self.view.model().setHorizontalHeaderLabels(["Refine", "Recenter", "H", "K", "L"])


class PeaksTableWorkspaceDisplay(TableWorkspaceDisplay):
    """Peaks table widget"""

    def __init__(self, ws, model, parent=None):  # pylint: disable=super-init-not-called
        self.model = model
        table_model = PeaksTableModel(parent=parent, data_model=model)
        self.view = TableWorkspaceDisplayView(presenter=self, parent=parent, table_model=table_model)
        self.view.setSelectionBehavior(TableWorkspaceDisplayView.SelectRows)
        self.presenter = PeaksTableWorkspaceDataPresenterStandard(model, self.view)
        self.view.set_context_menu_actions(self.view)

        self.name = model.get_name()
        self.parent = parent
        self.ads_observer = WorkspaceDisplayADSObserver(self)
        self.presenter.refresh()
        self.container = self

    def emit_close(self):
        """To make the ObservingPresenter happy"""


class RefineUB:
    """Refine UB table presenter"""

    def __init__(self, mdh, mde, model=None, view=None, parent=None):
        self.model = model if model else RefineUBModel(mdh, mde)
        self.sliceviewer = SliceViewer(self.model.get_mdh())
        self.peaks_table = PeaksTableWorkspaceDisplay(self.model.peaks, model=self.model.get_peaks_table_model())
        self.view = view if view else RefineUBView(self.sliceviewer, self.peaks_table, self, parent)
        self.update_lattice()

        self.view.connect_recenter_peaks(self.recenter)
        self.view.connect_populate_peaks(self.populate)
        self.view.connect_predict_peaks(self.predict)
        self.view.connect_refine(self.refine)
        self.view.connect_refine_orientation(self.refine_orientation)
        self.view.connect_undo(self.undo)
        self.view.connect_peak_selection(self.peak_selected)

        self.remake_slice_callback = None

    def update_workspaces(self, mdh, mde):
        """update the workspaces used"""
        self.model.update_workspaces(mdh, mde)
        self.sliceviewer = SliceViewer(self.model.get_mdh())
        self.view.set_sliceviewer(self.sliceviewer)
        self.view.select_row(self.view.selected_rows())
        self.view.setEnabled(True)

    def recenter(self):
        """Recenter the selected rows"""
        self.peaks_table.model.recenter_rows(self.peaks_table.view.model().recenter_rows())
        if self.view.selected_rows() is not None:
            self.peak_selected(self.view.selected_rows())

    def undo(self):
        """This will return to UB to the origonal state"""
        if self.peaks_table.model.undo():
            self.view.setEnabled(False)
            self.update_lattice()
            self.model.update_mde_with_new_ub()
            self.view.remove_sliceviewer()
            self.remake_slice()

    def refine_orientation(self):
        """called to refine the UB orientation only"""
        self.view.setEnabled(False)
        try:
            self.peaks_table.model.refine_orientation(self.peaks_table.view.model().refine_rows())
        except (RuntimeError, ValueError):
            self.view.setEnabled(True)
            return
        self.update_lattice()
        self.model.update_mde_with_new_ub()
        self.view.remove_sliceviewer()
        self.remake_slice()

    def refine(self):
        """called to refine the UB"""
        self.view.setEnabled(False)
        try:
            self.peaks_table.model.refine(self.peaks_table.view.model().refine_rows(), self.view.get_lattice_type())
        except (RuntimeError, ValueError):
            self.view.setEnabled(True)
            return
        self.update_lattice()
        self.model.update_mde_with_new_ub()
        self.view.remove_sliceviewer()
        self.remake_slice()

    def populate(self, checked):
        """toggle the peaks overlay in the sliceviewer"""

        # pylint: disable=protected-access
        self.sliceviewer._create_peaks_presenter_if_necessary().overlay_peaksworkspaces(
            [self.model.REFINE_UB_PEAKS_WS_NAME] if checked else []
        )

        self.sliceviewer.view.peaks_view.peak_actions_view.ui.add_peaks_button.setChecked(checked)

    def predict(self):
        """called to predict peaks"""
        self.model.predict_peaks()

    def update_lattice(self):
        """called to update the lattice parameters from the model"""
        self.view.set_lattice(self.peaks_table.model.get_lattice_parameters())

    def remake_slice(self):
        """called after the UB was changed to remake the HKL slice"""
        if self.remake_slice_callback:
            self.remake_slice_callback()  # pylint: disable=not-callable

    def peak_selected(self, peak_row):
        """called when a peak is selected to create the 3 perpendicular slices"""
        self.view.plot_perpendicular_slice(*self.model.get_perpendicular_slices(peak_row))
