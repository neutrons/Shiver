import sys
from pathlib import Path

# Add src directory to python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from trame.app import get_server
from shiver.models.configuration import ConfigurationModel
from shiver.presenters.configuration import ConfigurationPresenter
from shiver.trame_app.configuration_adapter import TrameConfigurationViewAdapter
from shiver.configuration import Configuration
from shiver.models.sample import SampleModel
from shiver.presenters.sample import SamplePresenter
from shiver.trame_app.sample_adapter import TrameSampleViewAdapter
from shiver.models.generate import GenerateModel
from shiver.presenters.generate import GeneratePresenter
from shiver.trame_app.generate_adapter import TrameGenerateViewAdapter
from shiver.models.histogram import HistogramModel
from shiver.presenters.histogram import HistogramPresenter
from shiver.trame_app.histogram_adapter import TrameHistogramViewAdapter
from shiver.models.corrections import CorrectionsModel, get_ions_list
from shiver.trame_app.corrections_adapter import TrameCorrectionsAdapter
from shiver.models.refine_ub import RefineUBModel
from shiver.trame_app.refine_ub_adapter import TrameRefineUbAdapter
from shiver.models.polarized import PolarizedModel
from shiver.presenters.polarized import PolarizedPresenter
from shiver.trame_app.polarized_adapter import TramePolarizedAdapter
from shiver.trame_app.ui import create_ui

# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server(name="Shiver")
state, ctrl = server.state, server.controller

def main():
    """
    Launch the Trame application.
    """
    # Initialize the configuration
    config = Configuration()

    # Initialize the configuration presenter
    config_model = ConfigurationModel()
    config_adapter = TrameConfigurationViewAdapter(state)
    config_presenter = ConfigurationPresenter(view=config_adapter, model=config_model, config=config)
    config_adapter.connect_get_settings_callback(config_presenter.get_settings)
    config_adapter.connect_apply_submit(config_presenter.handle_apply_submit)
    config_adapter.connect_reset_submit(config_presenter.handle_reset_submit)
    config_adapter.populate_fields()

    # Initialize the sample presenter
    sample_model = SampleModel()
    sample_adapter = TrameSampleViewAdapter(state)
    sample_presenter = SamplePresenter(view=sample_adapter, model=sample_model)
    sample_adapter.connect_sample_data(sample_presenter.handle_sample_data_init)
    sample_adapter.connect_matrix_state(sample_presenter.handle_matrix_state)
    sample_adapter.connect_lattice_state(sample_presenter.handle_lattice_state)
    sample_adapter.connect_ub_matrix_from_lattice(sample_presenter.handle_ub_matrix_from_lattice)
    sample_adapter.connect_lattice_from_ub_matrix(sample_presenter.handle_lattice_from_ub_matrix)
    sample_adapter.connect_apply_submit(sample_presenter.handle_apply_button)
    sample_adapter.connect_load_submit(sample_presenter.handle_load_button)
    sample_adapter.connect_nexus_submit(sample_presenter.handle_nexus_button)
    sample_adapter.connect_isaw_submit(sample_presenter.handle_isaw_button)
    sample_adapter.connect_btn_save_isaw_callback(sample_presenter.handle_save_isaw_button)

    # Initialize the generate presenter
    generate_model = GenerateModel()
    generate_adapter = TrameGenerateViewAdapter(state)
    generate_presenter = GeneratePresenter(view=generate_adapter, model=generate_model)
    generate_adapter.connect_generate_mde_callback(generate_presenter.do_generate_mde)
    generate_adapter.connect_save_configuration_callback(generate_presenter.do_save_configuration)
    generate_model.connect_error_message(generate_adapter.show_error_message)
    generate_model.connect_generate_mde_finish_callback(generate_adapter.generate_mde_finish_callback)

    # Initialize the histogram presenter
    histogram_model = HistogramModel()
    histogram_adapter = TrameHistogramViewAdapter(state)
    histogram_presenter = HistogramPresenter(view=histogram_adapter, model=histogram_model)
    histogram_adapter.connect_histogram_submit(histogram_presenter.handle_button)
    histogram_adapter.connect_plot_display_name_callback(histogram_presenter.model.get_plot_display_name)
    histogram_model.connect_error_message(histogram_adapter.show_error_message)
    histogram_model.connect_warning_message(histogram_adapter.show_warning_message)
    histogram_model.connect_makeslice_finish(histogram_adapter.makeslice_finish)

    # Initialize the corrections model
    corrections_model = CorrectionsModel()
    corrections_adapter = TrameCorrectionsAdapter(state)
    corrections_model.connect_error_message(corrections_adapter.show_error_message)
    state.ions_list = get_ions_list()

    # Initialize the refine UB model
    refine_ub_model = RefineUBModel(mdh=None, mde=None) # Will be updated when dialog is opened
    refine_ub_adapter = TrameRefineUbAdapter(state)
    refine_ub_model.connect_error_message(refine_ub_adapter.show_error_message)
    state.lattice_types = ["", "Cubic", "Hexagonal", "Rhombohedral", "Tetragonal", "Orthorhombic", "Monoclinic", "Triclinic"]

    # Initialize the polarized presenter
    polarized_model = PolarizedModel()
    polarized_adapter = TramePolarizedAdapter(state)
    polarized_presenter = PolarizedPresenter(view=polarized_adapter, model=polarized_model)
    polarized_adapter.connect_apply_submit(polarized_presenter.handle_apply_button)
    polarized_adapter.connect_populate_polarized_options(polarized_presenter.get_polarization_logs)
    polarized_model.connect_error_message(polarized_adapter.get_error_message)

    # Set up controller methods
    @ctrl.set("on_config_apply_clicked")
    def on_config_apply_clicked():
        config_adapter.apply_submit()

    @ctrl.set("on_config_reset_clicked")
    def on_config_reset_clicked():
        config_adapter.reset_submit()

    @ctrl.set("on_sample_apply_clicked")
    def on_sample_apply_clicked():
        params = sample_adapter.get_sample_parameters()
        sample_presenter.handle_apply_button(params)

    @ctrl.set("on_sample_load_processed_nexus")
    def on_sample_load_processed_nexus(filename):
        params = sample_presenter.handle_load_button(filename)
        sample_adapter.set_sample_parameters(params)

    @ctrl.set("on_sample_load_unprocessed_nexus")
    def on_sample_load_unprocessed_nexus(filename):
        params = sample_presenter.handle_nexus_button(filename)
        sample_adapter.set_sample_parameters(params)

    @ctrl.set("on_sample_load_isaw")
    def on_sample_load_isaw(filename):
        params = sample_presenter.handle_isaw_button(filename)
        sample_adapter.set_sample_parameters(params)

    @ctrl.set("on_sample_save_isaw")
    def on_sample_save_isaw(filename):
        sample_presenter.handle_save_isaw_button(filename)

    @ctrl.set("on_generate_mde_clicked")
    def on_generate_mde_clicked():
        generate_presenter.do_generate_mde()

    @ctrl.set("on_save_configuration_clicked")
    def on_save_configuration_clicked():
        generate_presenter.do_save_configuration()

    @ctrl.set("on_make_slice_clicked")
    def on_make_slice_clicked():
        histogram_presenter.submit_histogram_to_make_slice()

    @ctrl.set("on_apply_corrections_clicked")
    def on_apply_corrections_clicked():
        corrections_model.apply(
            state.selected_workspace,
            state.corrections.get("detailed_balance"),
            state.corrections.get("hyspec_polarizer_transmission"),
            state.corrections.get("temperature"),
            state.corrections.get("debye_waller_factor"),
            state.corrections.get("u2"),
            state.corrections.get("magnetic_structure_factor"),
            state.corrections.get("ion_name"),
        )
        state.show_corrections_dialog = False

    @ctrl.set("on_predict_peaks_clicked")
    def on_predict_peaks_clicked():
        refine_ub_model.predict_peaks()
        refine_ub_adapter.set_peaks(refine_ub_model.get_peaks_table_model().ws)

    @ctrl.set("on_recenter_peaks_clicked")
    def on_recenter_peaks_clicked():
        refine_ub_model.get_peaks_table_model().recenter_rows(refine_ub_adapter.selected_rows())

    @ctrl.set("on_refine_clicked")
    def on_refine_clicked():
        refine_ub_model.get_peaks_table_model().refine(refine_ub_adapter.selected_rows(), refine_ub_adapter.get_lattice_type())
        refine_ub_adapter.set_lattice(refine_ub_model.get_peaks_table_model().get_lattice_parameters())

    @ctrl.set("on_refine_orientation_clicked")
    def on_refine_orientation_clicked():
        refine_ub_model.get_peaks_table_model().refine_orientation(refine_ub_adapter.selected_rows())
        refine_ub_adapter.set_lattice(refine_ub_model.get_peaks_table_model().get_lattice_parameters())

    @ctrl.set("on_undo_clicked")
    def on_undo_clicked():
        if refine_ub_model.get_peaks_table_model().undo():
            refine_ub_adapter.set_lattice(refine_ub_model.get_peaks_table_model().get_lattice_parameters())

    @ctrl.set("on_apply_polarized_options_clicked")
    def on_apply_polarized_options_clicked():
        polarized_presenter.handle_apply_button(polarized_adapter.get_polarized_options_dict())
        state.show_polarized_dialog = False
    
    @ctrl.set("on_open_corrections_dialog")
    def on_open_corrections_dialog():
        state.selected_workspace = state.histogram_parameters.get("InputWorkspace")
        if state.selected_workspace:
            state.show_corrections_dialog = True

    @ctrl.set("on_open_refine_ub_dialog")
    def on_open_refine_ub_dialog():
        mdh = state.histogram_parameters.get("InputWorkspace")
        mde = state.histogram_parameters.get("InputWorkspace") # This should be the MDE workspace
        if mdh and mde:
            refine_ub_model.update_workspaces(mdh, mde)
            refine_ub_adapter.set_lattice(refine_ub_model.get_peaks_table_model().get_lattice_parameters())
            state.show_refine_ub_dialog = True

    @ctrl.set("on_open_polarized_dialog")
    def on_open_polarized_dialog():
        polarized_model.workspace = state.histogram_parameters.get("InputWorkspace")
        options = polarized_presenter.get_polarization_logs()
        polarized_adapter.set_polarized_options_dict(options)
        state.show_polarized_dialog = True

    # Populate initial sample data
    initial_sample_params = sample_presenter.handle_sample_data_init()
    sample_adapter.set_sample_parameters(initial_sample_params)

    server.ui.set_main_layout(create_ui())
    server.start()

if __name__ == "__main__":
    main()
