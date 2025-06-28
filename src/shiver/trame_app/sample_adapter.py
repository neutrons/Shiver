"""
Adapter for the Sample view to connect the presenter to the Trame state.
"""

class TrameSampleViewAdapter:
    """
    An adapter that mimics the PyQt SampleView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._sample_data_callback = None
        self._matrix_state_callback = None
        self._lattice_state_callback = None
        self._ub_matrix_from_lattice_callback = None
        self._lattice_from_ub_matrix_callback = None
        self._apply_submit_callback = None
        self._load_submit_callback = None
        self._nexus_submit_callback = None
        self._isaw_submit_callback = None
        self._save_isaw_callback = None

    def connect_sample_data(self, callback):
        self._sample_data_callback = callback

    def connect_matrix_state(self, callback):
        self._matrix_state_callback = callback

    def connect_lattice_state(self, callback):
        self._lattice_state_callback = callback

    def connect_ub_matrix_from_lattice(self, callback):
        self._ub_matrix_from_lattice_callback = callback

    def connect_lattice_from_ub_matrix(self, callback):
        self._lattice_from_ub_matrix_callback = callback

    def connect_apply_submit(self, callback):
        self._apply_submit_callback = callback

    def connect_load_submit(self, callback):
        self._load_submit_callback = callback

    def connect_nexus_submit(self, callback):
        self._nexus_submit_callback = callback

    def connect_isaw_submit(self, callback):
        self._isaw_submit_callback = callback

    def connect_btn_save_isaw_callback(self, callback):
        self._save_isaw_callback = callback

    def get_error_message(self, msg):
        self.state.error_message = msg

    def get_sample_parameters(self):
        return self.state.sample_parameters

    def set_sample_parameters(self, params):
        self.state.sample_parameters = params

    def get_ub_matrix(self):
        return self.state.ub_matrix

    def set_ub_matrix(self, matrix):
        self.state.ub_matrix = matrix
