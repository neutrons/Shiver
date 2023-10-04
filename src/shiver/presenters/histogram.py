"""Presenter for the Histogram tab"""
from qtpy.QtWidgets import QWidget
from shiver.views.corrections import Corrections
from shiver.models.corrections import CorrectionsModel
from shiver.models.generate import gather_mde_config_dict


class HistogramPresenter:
    """Histogram presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self.view.histogram_parameters.connect_histogram_submit(self.handle_button)
        self.view.histogram_parameters.histogram_btn.clicked.connect(self.submit_histogram_to_make_slice)
        self.view.connect_plot_display_name_callback(self.model.get_plot_display_name)

        self.view.buttons.connect_load_dataset(self.load_dataset)
        self.view.buttons.connect_load_file(self.load_file)
        self.view.connect_delete_workspace(self.delete_workspace)
        self.view.connect_rename_workspace(self.rename_workspace)
        self.view.connect_save_workspace(self.save_workspace)
        self.view.connect_save_workspace_to_ascii(self.save_workspace_to_ascii)
        self.view.connect_save_script_workspace(self.save_workspace_history)
        self.view.input_workspaces.mde_workspaces.connect_save_polarization_state_workspace(
            self.model.save_polarization_state
        )
        self.view.input_workspaces.mde_workspaces.connect_get_polarization_state_workspace(
            self.model.get_polarization_state
        )
        self.view.connect_corrections_tab(self.create_corrections_tab)
        self.view.connect_do_provenance_callback(self.do_provenance)
        self.model.connect_error_message(self.error_message)
        self.model.connect_makeslice_finish(self.makeslice_finish)

        self.model.ws_change_call_back(self.ws_changed)

        # initialize tables with workspaces already loaded
        for name, ws_type, frame, ndims in self.model.get_all_valid_workspaces():
            self.view.add_ws(name, ws_type, frame, ndims)

        # connect for populating UI when a histogram workspace is selected
        self.view.histogram_workspaces.histogram_selected_signal.connect(self.populate_ui_from_selected_histogram)

    def load_file(self, file_type, filename):
        """Call model to load the filename from the UI file dialog"""
        self.model.load(filename, file_type)

    def load_dataset(self, dataset: dict):
        """Call model to perform dataset loading with the given parameters."""
        data, background, norm = self.model.load_dataset(dataset)

        self.view.unset_all()

        # set the data in the view
        # default state
        pol_state = "unpolarized"
        if data:
            self.view.set_data(data, pol_state)
        # set the background in the view
        if background:
            self.view.set_background(background)
        # select the normalization in the view
        if norm:
            # NOTE: this is a bit of a hack to get around the fact that sometime the
            #      normalization is not set in the view until the next event loop
            while self.view.get_selected_normalization() != norm:
                self.view.select_normalization(norm)

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
        symmetry = params_dict["SymmetryOperations"]
        return self.model.symmetry_operations(symmetry)

    def error_message(self, msg, **kwargs):
        """Pass error message to the view"""
        self.view.show_error_message(msg, **kwargs)

    def makeslice_finish(self, ws_name, ndims, error=False):
        """Handle the makeslice algorithm finishing"""

        # re-enable histogram UI elements
        self.view.disable_while_running(False)

        # plot the newly generated histogram
        if not error:
            self.view.make_slice_finish(ws_name, ndims)

    def ws_changed(self, action, name, ws_type, frame=None, ndims=0):
        """Pass the workspace change to the view"""
        if action == "add":
            self.view.add_ws(name, ws_type, frame, ndims)
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

    def save_workspace(self, name, filename):
        """Called by the view to save a workspace"""
        self.model.save(name, filename)

    def save_workspace_to_ascii(self, name, filename):
        """Called by the view to save a workspace to ascii."""
        self.model.save_to_ascii(name, filename)

    def save_workspace_history(self, name, filename):
        """Called by the view to rename a workspace"""
        self.model.save_history(name, filename)

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
                corrections_tab_view.temperature.setEnabled(False)
            if has_scattered_transmission_correction:
                corrections_tab_view.hyspec_polarizer_transmission.setChecked(True)
                corrections_tab_view.hyspec_polarizer_transmission.setEnabled(False)

            # inline functions
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
            corrections_tab_view.apply_button.clicked.connect(_apply)
            corrections_tab_view.cancel_button.clicked.connect(_cancel)
            #
            tab_widget.addTab(corrections_tab_view, tab_name)
            tab_widget.setCurrentWidget(corrections_tab_view)

    def do_provenance(self, workspace_name: str):
        """Called by the view to show provenance"""
        # get the MDE config dict
        config_dict = gather_mde_config_dict(workspace_name)

        # pop up a warning message if the config dict is empty
        # NOTE: when mde is note generated with Shiver, there will be no config
        #       dictionary in the workspace log, therefore the provenance will
        #       not work.
        if not config_dict:
            self.error_message(f"No provenance information found in workspace: {workspace_name}.")
            return

        # switch to the Generate tab
        self.view.parent().parent().setCurrentIndex(1)

        # get the handle of the current generate tab
        generate_tab = self.view.parent().parent().currentWidget()

        # populate the Generate tab with the MDE config dict
        generate_tab.populate_from_dict(config_dict)

    def submit_histogram_to_make_slice(self):
        """Submit the histogram to the model"""
        # only submit if the view is valid
        if self.ready_for_histogram():
            # disable Histogram button while running
            self.view.disable_while_running(True)

            # gather the parameters from the view for MakeSlice
            config = self.build_config_for_make_slice()

            # send to model for processing
            self.model.do_make_slice(config)

            # update the plot name in the histogram parameters view
            self.view.histogram_parameters.update_plot_num()

    def build_config_for_make_slice(self) -> dict:
        """Gather parameters from view for MakeSlice.

        Returns
        -------
        config : dict
            Dictionary of parameters for MakeSlice.
        """
        config = {}
        # gather inputs
        config["InputWorkspace"] = self.view.gather_workspace_data()
        if self.view.gather_workspace_background():
            config["BackgroundWorkspace"] = self.view.gather_workspace_background()
        if self.view.gather_workspace_normalization():
            config["NormalizationWorkspace"] = self.view.gather_workspace_normalization()

        # get the parameters from the view
        config.update(self.view.histogram_parameters.gather_histogram_parameters())

        output_name = config.get("Name", None)
        if output_name:
            config["OutputWorkspace"] = output_name.replace(" ", "_")
        else:
            config["OutputWorkspace"] = "output_ws"

        return config

    def ready_for_histogram(self):
        """Check if the view is ready to submit a histogram"""
        # messages from models are passed to views
        if self.view.gather_workspace_data() is None or not self.view.histogram_parameters.is_valid:
            return False
        return True

    def populate_ui_from_selected_histogram(self, name):
        """Populate the UI from the selected histogram"""
        # step 0: ask model to get the history of MakeSlice from selected
        #         workspace as a dictionary
        history_dict = self.model.get_make_slice_history(name)

        # step 0: if nothing, skip
        if history_dict == {}:
            return

        # reset mde workspaces
        self.view.input_workspaces.mde_workspaces.unset_all()
        # reset norm workspaces
        self.view.input_workspaces.norm_workspaces.deselect_all()

        # step 1: try to set the data workspace if it exists
        if history_dict["InputWorkspace"] != "":
            # default value
            pol_state = "unpolarized"
            self.view.input_workspaces.mde_workspaces.set_data(history_dict["InputWorkspace"], pol_state)

        # step 2: try to set the background workspace if it exists
        if history_dict["BackgroundWorkspace"] != "":
            self.view.input_workspaces.mde_workspaces.set_background(history_dict["BackgroundWorkspace"])

        # step 3: try to select the normalization workspace if it exists
        if history_dict["NormalizationWorkspace"] != "":
            self.view.input_workspaces.norm_workspaces.set_selected(history_dict["NormalizationWorkspace"])

        # step 4: populate the histogram parameters widget based on given
        #         dictionary
        self.view.histogram_parameters.populate_histogram_parameters(history_dict)
