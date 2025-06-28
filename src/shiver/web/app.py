from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session

from mantid.kernel import Logger
from mantidqt.gui_helper import set_matplotlib_backend

# make sure matplotlib is correctly set before we import shiver
set_matplotlib_backend()

import mantid.simpleapi


# Need to import the new algorithms so they are registered with mantid
import shiver.models.makeslice  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position
import shiver.models.makeslices  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position
import shiver.models.convert_dgs_to_single_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position
import shiver.models.generate_dgs_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-position

from shiver.models.configuration import ConfigurationModel
from shiver.presenters.configuration import ConfigurationPresenter
from shiver.configuration import Configuration
from shiver.models.sample import SampleModel
from shiver.presenters.sample import SamplePresenter
from shiver.models.generate import GenerateModel
from shiver.presenters.generate import CONFIG_TEMPLATE, translate_filelist_to_string
from shiver.models.histogram import HistogramModel
from shiver.models.refine_ub import RefineUBModel
from shiver.models.polarized import PolarizedModel
from shiver.views.plots import do_colorfill_plot
import os
import json
from werkzeug.utils import secure_filename
import matplotlib
matplotlib.use('Agg')

# A dummy view that satisfies the Presenter's constructor but does nothing.
class DummyView:
    def connect_get_settings_callback(self, callback): pass
    def connect_apply_submit(self, callback): pass
    def connect_reset_submit(self, callback): pass
    def connect_sample_data(self, callback): pass
    def connect_matrix_state(self, callback): pass
    def connect_lattice_state(self, callback): pass
    def connect_ub_matrix_from_lattice(self, callback): pass
    def connect_lattice_from_ub_matrix(self, callback): pass
    def connect_load_submit(self, callback): pass
    def connect_nexus_submit(self, callback): pass
    def connect_isaw_submit(self, callback): pass
    def connect_btn_save_isaw_callback(self, callback): pass
    def get_error_message(self, msg):
        flash(msg, 'error')
    def show_error_message(self, msg, **kwargs):
        flash(msg, 'error')
    def generate_mde_finish_callback(self, activate):
        flash(f"Generate MDE Finished: {activate}", 'success')
    def makeslice_finish(self, workspace_dimensions, error=False):
        if not error:
            output_ws = list(workspace_dimensions.keys())[0]
            plot_path = generate_plot(output_ws)
            session['last_plot'] = plot_path
            flash(f"MakeSlice finished successfully for {output_ws}.", 'success')
        else:
            flash("MakeSlice finished with an error.", 'error')


# --- Global Application Objects ---
app = Flask(__name__)
app.secret_key = 'super secret key'
UPLOAD_FOLDER = '/tmp/shiver_uploads'
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

config = Configuration()
config_model = ConfigurationModel()
config_view = DummyView()
config_presenter = ConfigurationPresenter(config_view, config_model, config)

sample_model = SampleModel()
sample_view = DummyView()
sample_presenter = SamplePresenter(sample_view, sample_model)

generate_model = GenerateModel()
generate_model.connect_error_message(flash)
generate_model.connect_generate_mde_finish_callback(lambda activate: flash(f"Generation finished: {activate}", 'success'))

histogram_model = HistogramModel()
histogram_model.connect_error_message(flash)
histogram_model.connect_warning_message(flash)
histogram_model.connect_makeslice_finish(DummyView().makeslice_finish)

# These models require a workspace, so they are instantiated on demand.
refine_ub_model = None
polarized_model = None
# ------------------------------------

def generate_plot(workspace_name):
    """Generate a plot for the given workspace and save it to a file."""
    try:
        fig = do_colorfill_plot([workspace_name])
        if fig:
            plot_filename = f"{workspace_name}.png"
            plot_path = os.path.join(STATIC_FOLDER, plot_filename)
            fig.savefig(plot_path)
            matplotlib.pyplot.close(fig)
            return plot_filename
    except Exception as e:
        flash(f"Could not generate plot: {e}", 'error')
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/configuration', methods=['GET'])
def configuration():
    settings = config_presenter.get_settings()
    return render_template('configuration.html', sectioned_settings=settings)

@app.route('/configuration/apply', methods=['POST'])
def apply_configuration():
    parameters = {}
    all_settings = config_presenter.get_settings()
    flat_settings = {s.name: s for section in all_settings.values() for s in section}
    for key, value in request.form.items():
        if key in flat_settings:
            parameters[key] = {"section": flat_settings[key].section, "value": value}
    config_presenter.handle_apply_submit(parameters)
    flash('Configuration applied successfully.', 'success')
    return redirect(url_for('configuration'))

@app.route('/configuration/reset', methods=['POST'])
def reset_configuration():
    config_presenter.handle_reset_submit()
    flash('Configuration has been reset to defaults.', 'success')
    return redirect(url_for('configuration'))

@app.route('/sample', methods=['GET'])
def sample():
    params = sample_presenter.handle_sample_data_init()
    return render_template('sample.html', params=params)

@app.route('/sample/apply', methods=['POST'])
def apply_sample():
    sample_presenter.handle_apply_button(request.form)
    flash('Sample parameters applied.', 'success')
    return redirect(url_for('sample'))

def handle_file_upload(request, presenter_method):
    if 'file' not in request.files:
        flash('No file part', 'error')
        return False
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return False
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        presenter_method(filepath)
        flash(f'File {filename} loaded successfully.', 'success')
        return True
    return False

@app.route('/sample/load_nexus_processed', methods=['POST'])
def load_nexus_processed():
    handle_file_upload(request, sample_presenter.handle_load_button)
    return redirect(url_for('sample'))

@app.route('/sample/load_nexus_unprocessed', methods=['POST'])
def load_nexus_unprocessed():
    handle_file_upload(request, sample_presenter.handle_nexus_button)
    return redirect(url_for('sample'))

@app.route('/sample/load_isaw', methods=['POST'])
def load_isaw():
    handle_file_upload(request, sample_presenter.handle_isaw_button)
    return redirect(url_for('sample'))

@app.route('/sample/save_isaw', methods=['POST'])
def save_isaw():
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], 'ub_matrix.mat')
    sample_presenter.handle_save_isaw_button(save_path)
    flash(f'Saved ISAW file to {save_path}', 'success')
    return redirect(url_for('sample'))

def get_generate_config_from_form(form):
    config_dict = {}
    config_dict["mde_name"] = form.get("mde_name")
    config_dict["output_dir"] = form.get("output_dir")
    config_dict["mde_type"] = form.get("mde_type")
    filenames_str = form.get('filename', '')
    config_dict["filename"] = [f.strip() for f in filenames_str.split(',') if f.strip()]
    config_dict["incident_energy"] = form.get("incident_energy")
    config_dict["t0"] = form.get("t0")
    config_dict["grouping_file"] = form.get("grouping_file")
    if config_dict["mde_type"] == "Background (minimized by angle and energy)":
        config_dict["MinimizeBackground"] = {
            "percent_min": form.get("percent_min"),
            "percent_max": form.get("percent_max"),
            "group_path": form.get("group_path"),
        }
    config_dict = {k: v for k, v in config_dict.items() if v is not None and v != ''}
    if "MinimizeBackground" in config_dict:
        config_dict["MinimizeBackground"] = {k: v for k, v in config_dict["MinimizeBackground"].items() if v is not None and v != ''}
    config_dict["filename"] = translate_filelist_to_string(config_dict.get("filename", []))
    return config_dict

@app.route('/generate', methods=['GET'])
def generate():
    return render_template('generate.html')

@app.route('/generate/mde', methods=['POST'])
def generate_mde():
    config_dict = get_generate_config_from_form(request.form)
    if not config_dict.get('filename'):
        flash("Error: At least one data file is required.", 'error')
        return redirect(url_for('generate'))
    generate_model.generate_mde(config_dict)
    flash("Generation Started...", 'success')
    return redirect(url_for('generate'))

@app.route('/generate/save_config', methods=['POST'])
def save_config():
    config_dict = get_generate_config_from_form(request.form)
    if not config_dict:
        flash("Cannot save empty configuration", 'error')
        return redirect(url_for('generate'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], config_dict.get("mde_name", "config") + ".py")
    config_dict_str = json.dumps(config_dict, indent=4).replace("null", "None").replace("true", "True").replace("false", "False")
    config_dict_str = config_dict_str[:-1] + "\t}"
    content = CONFIG_TEMPLATE.replace("DATA_SET_TO_BE_REPLACED", config_dict_str)
    with open(filepath, "w", encoding="UTF-8") as config_file:
        config_file.write(content)
    return send_file(filepath, as_attachment=True)

@app.route('/histogram', methods=['GET'])
def histogram():
    workspaces = histogram_model.get_all_valid_workspaces()
    mde_workspaces = [ws for ws in workspaces if ws[1] == 'MDE']
    norm_workspaces = [ws for ws in workspaces if ws[1] == 'Normalization']
    hist_workspaces = [ws for ws in workspaces if ws[1] == 'Histogram']
    last_plot = session.pop('last_plot', None)
    return render_template('histogram.html', mde_workspaces=mde_workspaces, norm_workspaces=norm_workspaces, hist_workspaces=hist_workspaces, plot_file=last_plot)

@app.route('/histogram/makeslice', methods=['POST'])
def make_slice():
    config = {}
    form = request.form
    config['Name'] = form.get('Name')
    config['QDimension0'] = form.get('QDimension0')
    config['QDimension1'] = form.get('QDimension1')
    config['QDimension2'] = form.get('QDimension2')
    config['Dimension0Name'] = form.get('Dimension0Name')
    config['Dimension0Binning'] = form.get('Dimension0Binning')
    config['Dimension1Name'] = form.get('Dimension1Name')
    config['Dimension1Binning'] = form.get('Dimension1Binning')
    config['Dimension2Name'] = form.get('Dimension2Name')
    config['Dimension2Binning'] = form.get('Dimension2Binning')
    config['Dimension3Name'] = form.get('Dimension3Name')
    config['Dimension3Binning'] = form.get('Dimension3Binning')
    config['SymmetryOperations'] = form.get('SymmetryOperations')
    config['Smoothing'] = form.get('Smoothing')
    config['InputWorkspace'] = form.get('data_unp')
    config['BackgroundWorkspace'] = form.get('background')
    config['NormalizationWorkspace'] = form.get('normalization')
    config = {k: v for k, v in config.items() if v is not None and v != ''}
    if not config.get('InputWorkspace'):
        flash("Error: An input workspace is required.", 'error')
        return redirect(url_for('histogram'))
    config["OutputWorkspace"] = config.get('Name', 'output_ws').replace(" ", "_")
    config["Algorithm"] = "MakeSlice"
    histogram_model.do_make_slice(config)
    return redirect(url_for('histogram'))

@app.route('/refine_ub', methods=['GET', 'POST'])
def refine_ub():
    global refine_ub_model
    if request.method == 'POST':
        mdh_ws = request.form.get('mdh_workspace')
        mde_ws = request.form.get('mde_workspace')
        if mdh_ws and mde_ws:
            try:
                refine_ub_model = RefineUBModel(mdh_ws, mde_ws)
                flash(f"RefineUBModel initialized for MDH: {mdh_ws} and MDE: {mde_ws}", 'success')
            except Exception as e:
                flash(f"Error initializing RefineUBModel: {e}", 'error')
                refine_ub_model = None
        else:
            flash("Please select both an MDH and MDE workspace.", 'error')
        return redirect(url_for('refine_ub'))
    workspaces = histogram_model.get_all_valid_workspaces()
    mde_workspaces = [ws for ws in workspaces if ws[1] == 'MDE']
    hist_workspaces = [ws for ws in workspaces if ws[1] == 'Histogram']
    lattice_params = {}
    peaks = []
    if refine_ub_model:
        lattice_params = refine_ub_model.get_lattice_parameters()
        peaks_table = refine_ub_model.get_peaks_table_model()
        for i in range(peaks_table.get_number_of_rows()):
            peaks.append([peaks_table.get_cell(i, j) for j in range(1, 4)])
    return render_template('refine_ub.html', mde_workspaces=mde_workspaces, hist_workspaces=hist_workspaces, lattice_params=lattice_params, peaks=peaks)

@app.route('/refine_ub/predict', methods=['POST'])
def predict_peaks():
    if refine_ub_model:
        refine_ub_model.predict_peaks()
        flash("Peak prediction started.", 'success')
    else:
        flash("Initialize the Refine UB model first.", 'error')
    return redirect(url_for('refine_ub'))

@app.route('/refine_ub/refine', methods=['POST'])
def refine_ub_action():
    flash("Refine functionality is not implemented in the web interface.", 'info')
    return redirect(url_for('refine_ub'))

@app.route('/polarized', methods=['GET', 'POST'])
def polarized():
    global polarized_model
    if request.method == 'POST':
        ws_name = request.form.get('workspace')
        if ws_name:
            try:
                polarized_model = PolarizedModel(ws_name)
                flash(f"PolarizedModel initialized for workspace: {ws_name}", 'success')
            except Exception as e:
                flash(f"Error initializing PolarizedModel: {e}", 'error')
                polarized_model = None
        else:
            flash("Please select a workspace.", 'error')
        return redirect(url_for('polarized'))
    workspaces = histogram_model.get_all_valid_workspaces()
    mde_workspaces = [ws for ws in workspaces if ws[1] == 'MDE']
    params = {}
    if polarized_model:
        params = polarized_model.get_polarization_logs()
    return render_template('polarized.html', workspaces=mde_workspaces, params=params)

@app.route('/polarized/apply', methods=['POST'])
def apply_polarized():
    if polarized_model:
        logs = {
            "PolarizationState": request.form.get("PolarizationState"),
            "PolarizationDirection": request.form.get("PolarizationDirection"),
            "FlippingRatio": request.form.get("FlippingRatio"),
            "FlippingRatioSampleLog": request.form.get("FlippingRatioSampleLog"),
            "psda": request.form.get("PSDA"),
        }
        polarized_model.save_polarization_logs(logs)
        flash("Polarization logs saved.", 'success')
    else:
        flash("Initialize the Polarized model first.", 'error')
    return redirect(url_for('polarized')
)



