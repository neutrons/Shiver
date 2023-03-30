"""Presenter for the Histogram tab"""
import webbrowser
from qtpy.QtWidgets import QWidget
from shiver.views.corrections import Corrections
from shiver.models.corrections import CorrectionsModel


class HistogramPresenter:
    """Histogram presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model
        self.view.histogram_parameters.connect_histogram_submit(self.handle_button)

        self.view.buttons.connect_load_file(self.load_file)
        self.view.connect_delete_workspace(self.delete_workspace)
        self.view.connect_rename_workspace(self.rename_workspace)
        self.view.connect_corrections_tab(self.create_corrections_tab)
        self.model.connect_error_message(self.error_message)

        self.model.ws_change_call_back(self.ws_changed)

    def load_file(self, file_type, filename):
        """Call model to load the filename from the UI file dialog"""
        self.model.load(filename, file_type)

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def handle_button(self, params_dict):
        """Validate symmetry histogram parameter"""
        symmetry = params_dict["Symmetry"]
        self.model.symmetry_operations(symmetry)

    def error_message(self, msg):
        """Pass error message to the view"""
        self.view.show_error_message(msg)

    def ws_changed(self, action, name, ws_type, frame=None):
        """Pass the workspace change to the view"""
        if action == "add":
            self.view.add_ws(name, ws_type, frame)
        elif action == "del":
            self.view.del_ws(name)
        elif action == "clear":
            self.view.clear_ws()

    def delete_workspace(self, name):
        """Called by the view to delete a workspace"""
        self.model.delete(name)

    def rename_workspace(self, old_name, new_name):
        """Called by the view to rename a workspace"""
        self.model.rename(old_name, new_name)

    def create_corrections_tab(self, name):
        """Create a corrections tab"""
        tab_name = f"Corrections - {name}"
        tab_widget = self.view.parent().parent()

        # check if tab already exists
        tab_idx = tab_widget.indexOf(tab_widget.findChild(QWidget, tab_name))
        if tab_idx != -1:
            tab_widget.setCurrentIndex(tab_idx)
        else:
            # create a new tab
            corrections_tab_view = Corrections(parent=self.view, name=name)
            corrections_tab_view.setObjectName(tab_name)
            # create a new model
            corrections_tab_model = CorrectionsModel()

            # populate initial values
            has_detailed_balance, temperature = corrections_tab_model.has_apply_detailed_balance(name)
            has_scattered_transmission_correction = corrections_tab_model.has_scattered_transmission_correction(name)
            if has_detailed_balance:
                corrections_tab_view.detailed_balance.setChecked(True)
                corrections_tab_view.temperature.setText(str(temperature))
                corrections_tab_view.detailed_balance.setEnabled(False)
            if has_scattered_transmission_correction:
                corrections_tab_view.hyspec_polarizer_transmission.setChecked(True)
                corrections_tab_view.hyspec_polarizer_transmission.setEnabled(False)

            # inline functions
            def _help():
                """Show the help for the corrections tab"""
                webbrowser.open("https://neutrons.github.io/Shiver/")

            def _apply():
                """Apply the corrections"""
                do_detail_balance = (
                    corrections_tab_view.detailed_balance.isChecked()
                    and corrections_tab_view.detailed_balance.isEnabled()
                )
                do_polarizer_transmission = (
                    corrections_tab_view.hyspec_polarizer_transmission.isChecked()
                    and corrections_tab_view.hyspec_polarizer_transmission.isEnabled()
                )
                corrections_tab_model.apply(
                    name,
                    do_detail_balance,
                    do_polarizer_transmission,
                    corrections_tab_view.temperature.text(),
                )
                # clean up
                tab_widget.setCurrentWidget(self._view)
                corrections_tab_view.deleteLater()

            def _cancel():
                """Cancel the corrections tab"""
                tab_widget.setCurrentWidget(self._view)
                corrections_tab_view.deleteLater()

            # connect inline functions to view
            corrections_tab_model.connect_error_message(self.error_message)
            corrections_tab_view.help_button.clicked.connect(_help)
            corrections_tab_view.apply_button.clicked.connect(_apply)
            corrections_tab_view.cancel_button.clicked.connect(_cancel)
            #
            tab_widget.addTab(corrections_tab_view, tab_name)
            tab_widget.setCurrentWidget(corrections_tab_view)
