"""Presenter for the Histogram tab"""

# pylint: disable=invalid-name
import os
from qtpy.QtWidgets import QWidget
from shiver.views.corrections import Corrections
from shiver.models.corrections import CorrectionsModel, get_ions_list
from shiver.models.generate import gather_mde_config_dict, save_mde_config_dict

from shiver.models.generate import GenerateModel
from shiver.presenters.generate import GeneratePresenter
from shiver.views.generate import Generate

from shiver.models.polarized import PolarizedModel
from shiver.presenters.polarized import create_dictionary_polarized_options

from shiver.models.sample import SampleModel
from shiver.presenters.sample import get_sample_parameters_from_workspace

from shiver.presenters.refine_ub import RefineUB


class HistogramPresenter:  # pylint: disable=too-many-public-methods
    """Histogram presenter"""

    REFINEMENT_UB_WS_NAME = "UB_refinement_workspace"

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self.view.histogram_parameters.connect_histogram_submit(self.handle_button)
        self.view.histogram_parameters.histogram_btn.clicked.connect(self.submit_histogram_to_make_slice)
        self.view.connect_plot_display_name_callback(self.model.get_plot_display_name)

        self.view.buttons.connect_load_dataset(self.load_dataset)
        self.view.buttons.connect_load_file(self.load_file)

        self.view.connect_clone_workspace(self.clone_workspace)
        self.view.connect_scale_workspace(self.scale_workspace)

        self.view.connect_delete_workspace(self.delete_workspace)
        self.view.connect_rename_workspace(self.rename_workspace)
        self.view.input_workspaces.mde_workspaces.connect_save_mde_workspace_callback(self.save_mde_workspace)
        self.view.connect_save_workspace(self.save_workspace)
        self.view.connect_save_workspace_to_ascii(self.save_workspace_to_ascii)
        self.view.connect_save_script_workspace(self.save_workspace_history)
        self.view.input_workspaces.mde_workspaces.connect_save_polarization_state_workspace(
            self.save_polarization_state
        )
        self.view.input_workspaces.mde_workspaces.connect_get_polarization_state_workspace(self.get_polarization_state)

        self.view.connect_corrections_tab(self.create_corrections_tab)
        self.view.connect_refine_ub(self.refine_ub)
        self.view.connect_refine_ub_tab(self.create_refine_ub_tab)
        self.view.connect_do_provenance_callback(self.do_provenance)
        self.model.connect_error_message(self.error_message)
        self.model.connect_warning_message(self.warning_message)
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
        # default state: unpolarized
        pol_state = "UNP"
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
        validations = {}
        symmetry = params_dict["SymmetryOperations"]
        validations["symmetry_validation"] = self.model.symmetry_operations(symmetry)

        # gather input data workspaces
        all_data = self.view.gather_workspace_data()
        # validate sample log and flipping ratio for workspaces
        validations["multi_sample_log_validation"] = True
        if len(all_data) == 2:
            config = {}
            config["NSFInputWorkspace"] = all_data[0]
            config["SFInputWorkspace"] = all_data[1]
            validations["multi_sample_log_validation"] = self.model.validate_workspace_logs(config)
            if validations["multi_sample_log_validation"] is False:
                self.view.input_workspaces.mde_workspaces.set_field_invalid_state(
                    self.view.input_workspaces.mde_workspaces
                )
        return validations

    def error_message(self, msg, **kwargs):
        """Pass error message to the view"""
        self.view.show_error_message(msg, **kwargs)

    def warning_message(self, msg, **kwargs):
        """Pass warning message to the view"""
        user_input = self.view.show_warning_message(msg, **kwargs)
        return user_input

    def makeslice_finish(self, workspace_dimesions, error=False):
        """Handle the makeslice algorithm finishing"""

        # re-enable histogram UI elements
        self.view.disable_while_running(False)
        # plot the newly generated histogram
        if not error:
            # each workspace
            for ws_name, ndims in workspace_dimesions.items():
                self.view.make_slice_finish(ws_name, ndims)

    def ws_changed(self, action, name, ws_type, frame=None, ndims=0):
        """Pass the workspace change to the view"""
        if action == "add":
            self.view.add_ws(name, ws_type, frame, ndims)
        elif action == "del":
            self.view.del_ws(name)
            self.remove_provenance_tab(name)
        elif action == "clear":
            self.view.clear_ws()

    def clone_workspace(self, name, clone_name):
        """Called by the view to clone a workspace"""
        self.model.clone(name, clone_name)

    def scale_workspace(self, name, output_name, scale_factor):
        """Called by the view to scale a workspace"""
        self.model.scale(name, output_name, scale_factor)

    def delete_workspace(self, name):
        """Called by the view to delete a workspace"""
        self.model.delete(name)

    def rename_workspace(self, old_name, new_name):
        """Called by the view to rename a workspace"""
        self.model.rename(old_name, new_name)

    def save_mde_workspace(self, name, filepath):
        """Called by the view to save a workspace"""
        # save config
        config_dict = gather_mde_config_dict(name)
        # in case there is not MDE config saved in the workspace
        # set these fields to None
        if len(config_dict) == 0:
            config_dict["MaskingDataFile"] = None
            config_dict["NormalizationDataFile"] = None
            config_dict["Ei"] = None
            config_dict["T0"] = None
            config_dict["AdvancedOptions"] = {}
            config_dict["filename"] = None

        # collect the values from the workspace
        config_dict["mde_name"] = name
        config_dict["output_dir"] = os.path.dirname(filepath)
        config_dict["mde_type"] = "Data"

        # init SampleModel
        sample_model = SampleModel(name)
        # sample logs are stored as separate sample logs
        config_dict["SampleParameters"] = get_sample_parameters_from_workspace(sample_model.get_lattice_ub())
        # init PolarizedModel
        polarized_model = PolarizedModel(name)
        # get logs
        config_dict["PolarizedOptions"] = create_dictionary_polarized_options(
            polarized_model.get_polarization_logs_for_workspace()
        )
        save_mde_config_dict(name, config_dict)
        self.save_workspace(name, filepath)

    def save_workspace(self, name, filename):
        """Called by the view to save a workspace"""
        self.model.save(name, filename)

    def save_workspace_to_ascii(self, name, filename):
        """Called by the view to save a workspace to ascii."""
        self.model.save_to_ascii(name, filename)

    def save_workspace_history(self, name, filename):
        """Called by the view to rename a workspace"""
        self.model.save_history(name, filename)

    def create_refine_ub_tab(self):
        """UB refinement tab"""
        tab_name = "Refine UB"
        tab_widget = self.view.parent().parent()

        input_mde = self.model.get_make_slice_history(self.REFINEMENT_UB_WS_NAME)["InputWorkspace"]

        # check if tab already exists
        tab_idx = tab_widget.indexOf(tab_widget.findChild(QWidget, tab_name))
        if tab_idx != -1:
            tab_widget.setCurrentIndex(tab_idx)
            refine_ub_tab = tab_widget.currentWidget()
            refine_ub_tab.presenter.update_workspaces(self.REFINEMENT_UB_WS_NAME, input_mde)
        else:
            refine_ub_tab = RefineUB(self.REFINEMENT_UB_WS_NAME, input_mde, parent=self.view)
            refine_ub_tab.view.setObjectName(tab_name)
            refine_ub_tab.remake_slice_callback = self.remake_slice
            refine_ub_tab.model.connect_error_message(self.error_message)

            def _close():
                """Close the Refine UB tab"""
                tab_widget.setTabEnabled(0, True)
                tab_widget.setTabEnabled(1, True)
                tab_widget.setCurrentWidget(self._view)
                # cleanup ads observers and delete tab
                refine_ub_tab.sliceviewer.view.emit_close()
                refine_ub_tab.peaks_table.ads_observer = None
                refine_ub_tab.view.deleteLater()
                # make sure the correct workspace is still selected after it was modified
                self.view.input_workspaces.mde_workspaces.set_data(input_mde, "UNP")

            refine_ub_tab.view.close_btn.clicked.connect(_close)
            tab_widget.addTab(refine_ub_tab.view, tab_name)
            tab_widget.setCurrentWidget(refine_ub_tab.view)
            tab_widget.setTabEnabled(0, False)
            tab_widget.setTabEnabled(1, False)

    def remake_slice(self):
        """Remake the HKL volume after UB was updated"""
        config = self.model.get_make_slice_history(self.REFINEMENT_UB_WS_NAME)
        self.model.do_make_slice(config)

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

            # populate valid ions
            ions = get_ions_list()
            if ions:
                corrections_tab_view.ion_name.addItems(ions)
            else:
                # disable the magnetic structure factor correction if MagneticFormFactorCorrectionMD is not available
                corrections_tab_view.magnetic_structure_factor.setEnabled(False)
                corrections_tab_view.ion_name.setEnabled(False)

            # populate initial values
            has_detailed_balance, temperature = corrections_tab_model.has_apply_detailed_balance(name)
            has_scattered_transmission_correction = corrections_tab_model.has_scattered_transmission_correction(name)
            has_magnetic_form_factor, ion_name = corrections_tab_model.has_magnetic_form_factor_correction(name)
            has_debye_waller_factor, u2 = corrections_tab_model.has_debye_waller_factor_correction(name)
            if has_detailed_balance:
                corrections_tab_view.detailed_balance.setChecked(True)
                corrections_tab_view.temperature.setText(str(temperature))
                corrections_tab_view.detailed_balance.setEnabled(False)
                corrections_tab_view.temperature.setEnabled(False)
            if has_scattered_transmission_correction:
                corrections_tab_view.hyspec_polarizer_transmission.setChecked(True)
                corrections_tab_view.hyspec_polarizer_transmission.setEnabled(False)
            if has_magnetic_form_factor:
                corrections_tab_view.magnetic_structure_factor.setChecked(True)
                idx = corrections_tab_view.ion_name.findText(ion_name)
                if idx != -1:
                    corrections_tab_view.ion_name.setCurrentIndex(idx)
                corrections_tab_view.magnetic_structure_factor.setEnabled(False)
                corrections_tab_view.ion_name.setEnabled(False)
            if has_debye_waller_factor:
                corrections_tab_view.debye_waller_correction.setChecked(True)
                corrections_tab_view.u2.setText(str(u2))
                corrections_tab_view.debye_waller_correction.setEnabled(False)
                corrections_tab_view.u2.setEnabled(False)

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
                do_debye_waller = (
                    corrections_tab_view.debye_waller_correction.isChecked()
                    and corrections_tab_view.debye_waller_correction.isEnabled()
                )
                corrections_tab_model.apply(
                    name,
                    do_detail_balance,
                    do_polarizer_transmission,
                    corrections_tab_view.temperature.text(),
                    do_debye_waller,
                    corrections_tab_view.u2.text(),
                    corrections_tab_view.magnetic_structure_factor.isChecked(),
                    corrections_tab_view.ion_name.currentText(),
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

    def refine_ub(self, ws_name):
        """Set the histogram parameters needed for UB refinement"""
        if (e_initial := self.model.get_ei(ws_name)) is None:
            return

        self.view.input_workspaces.mde_workspaces.set_data(ws_name, "UNP")

        params = {
            "QDimension0": "1,0,0",
            "QDimension1": "0,1,0",
            "QDimension2": "0,0,1",
            "Dimension0Name": "QDimension0",
            "Dimension0Binning": ",,",
            "Dimension1Name": "QDimension1",
            "Dimension1Binning": ",,",
            "Dimension2Name": "QDimension2",
            "Dimension2Binning": ",,",
            "Dimension3Name": "DeltaE",
            "Dimension3Binning": f"{-e_initial*0.05},{e_initial*0.05}",
            "SymmetryOperations": "",
            "Smoothing": "0",
            "name": self.REFINEMENT_UB_WS_NAME,
        }
        self.view.histogram_parameters.populate_histogram_parameters(params)

    def do_provenance(self, workspace_name: str):
        """Called by the view to show provenance"""
        # get the MDE config dict
        config_dict = gather_mde_config_dict(workspace_name)
        # include the current workspace name
        config_dict["mde_name"] = workspace_name
        # pop up a warning message if the config dict is empty
        # NOTE: when mde is note generated with Shiver, there will be no config
        #       dictionary in the workspace log, therefore the provenance will
        #       not work.
        if not config_dict:
            self.error_message(f"No provenance information found in workspace: {workspace_name}.")
            return

        # polarization logs are stored as separate sample logs
        # init PolarizedModel
        polarized_model = PolarizedModel(workspace_name)
        # get logs
        config_dict["PolarizedOptions"] = create_dictionary_polarized_options(
            polarized_model.get_polarization_logs_for_workspace()
        )

        # init SampleModel
        sample_model = SampleModel(workspace_name)
        # sample logs are stored as separate sample logs
        config_dict["SampleParameters"] = get_sample_parameters_from_workspace(sample_model.get_lattice_ub())

        # switch to the Generate tab
        self.view.parent().parent().setCurrentIndex(1)

        # get the handle of the current generate tab
        generate_tab = self.view.parent().parent().currentWidget()

        # populate the Generate tab with the MDE config dict
        generate_tab.populate_from_dict(config_dict)

    def remove_provenance_tab(self, workspace_name):
        """remove provenance tab for a workspace, if it exists"""

        # access tab pages
        main_window = self.view.parent().parent().parent()
        current_tab = self.view.parent().parent().currentWidget()
        widget_tab = main_window.tabs
        tab_name = f"Generate - {workspace_name}"

        for i in range(widget_tab.count()):
            if widget_tab.tabText(i) == tab_name and current_tab != widget_tab.widget(i):
                generate_tab_index = i
                # remove current tab
                widget_tab.removeTab(generate_tab_index)
                # add a new tab
                main_window.generate = Generate(main_window)
                generate_model = GenerateModel()
                main_window.generate_presenter = GeneratePresenter(main_window.generate, generate_model)
                widget_tab.addTab(main_window.generate, "Generate")

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

        # get the parameters from the view
        config.update(self.view.histogram_parameters.gather_histogram_parameters())

        output_name = config.get("Name", None)
        if output_name:
            output_workspace = output_name.replace(" ", "_")
        else:
            output_workspace = "output_ws"
        # gather inputs
        all_data = self.view.gather_workspace_data()
        # data workspaces incluced: data_u, _data_nsf, _data_sf:
        # output workspaces defined
        if len(all_data) == 1:
            config["InputWorkspace"] = all_data[0]
            config["OutputWorkspace"] = output_workspace
            config["Algorithm"] = "MakeSlice"
        else:
            config["NSFInputWorkspace"] = all_data[0]
            config["SFInputWorkspace"] = all_data[1]
            config["NSFOutputWorkspace"] = output_workspace + "_NSF"
            config["SFOutputWorkspace"] = output_workspace + "_SF"
            config["Algorithm"] = "MakeSFCorrectedSlices"

        if self.view.gather_workspace_background():
            config["BackgroundWorkspace"] = self.view.gather_workspace_background()
        if self.view.gather_workspace_normalization():
            config["NormalizationWorkspace"] = self.view.gather_workspace_normalization()

        return config

    def ready_for_histogram(self):
        """Check if the view is ready to submit a histogram"""
        # messages from models are passed to views
        if not self.view.is_valid() or not self.view.histogram_parameters.is_valid:
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

        # get input/output workspaces
        output_workspace = history_dict.get("OutputWorkspace", None)

        # set histogram name
        history_dict["name"] = output_workspace

        input_workspace = history_dict.get("InputWorkspace", None)
        nsf_input_workspace = history_dict.get("NSFOutputWorkspace", None)
        sf_input_workspace = history_dict.get("SFOutputWorkspace", None)

        # step 1: try to set the data workspace if it exists
        if input_workspace is not None and output_workspace == name:
            # default value
            pol_state = "UNP"
            self.view.input_workspaces.mde_workspaces.set_data(history_dict["InputWorkspace"], pol_state)

        if nsf_input_workspace is not None:
            # non spinflip workspace
            pol_state = "NSF"
            self.view.input_workspaces.mde_workspaces.set_data(history_dict["NSFInputWorkspace"], pol_state)
            if history_dict["NSFOutputWorkspace"] == name:
                history_dict["OutputWorkspace"] = history_dict["NSFOutputWorkspace"]
                history_dict["InputWorkspace"] = history_dict["NSFInputWorkspace"]
                history_dict["name"] = name.replace("_NSF", "")

        if sf_input_workspace is not None:
            # spinflip workspace
            pol_state = "SF"
            self.view.input_workspaces.mde_workspaces.set_data(history_dict["SFInputWorkspace"], pol_state)
            if history_dict["SFOutputWorkspace"] == name:
                history_dict["OutputWorkspace"] = history_dict["SFOutputWorkspace"]
                history_dict["InputWorkspace"] = history_dict["SFInputWorkspace"]
                history_dict["name"] = name.replace("_SF", "")

        # step 2: try to set the background workspace if it exists
        if history_dict["BackgroundWorkspace"] != "":
            self.view.input_workspaces.mde_workspaces.set_background(history_dict["BackgroundWorkspace"])

        # step 3: try to select the normalization workspace if it exists
        if history_dict["NormalizationWorkspace"] != "":
            self.view.input_workspaces.norm_workspaces.set_selected(history_dict["NormalizationWorkspace"])

        # step 4: populate the histogram parameters widget based on given
        #         dictionary
        self.view.histogram_parameters.populate_histogram_parameters(history_dict)

    def save_polarization_state(self, name, pol_state):
        """save polarization state with polarized model"""

        # init PolarizedModel
        polarized_model = PolarizedModel(name)
        # save state
        polarized_model.save_polarization_state(pol_state)

    def get_polarization_state(self, name):
        """get polarization state from polarized model"""

        # init PolarizedModel
        polarized_model = PolarizedModel(name)
        # get state
        state = polarized_model.get_polarization_state()
        return state
