"""
Adapter for the Refine UB view to connect the presenter to the Trame state.
"""

class TrameRefineUbAdapter:
    """
    An adapter that mimics the PyQt RefineUBView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._predict_peaks_callback = None
        self._recenter_peaks_callback = None
        self._refine_callback = None
        self._refine_orientation_callback = None
        self._undo_callback = None

    def connect_predict_peaks(self, callback):
        self._predict_peaks_callback = callback

    def connect_recenter_peaks(self, callback):
        self._recenter_peaks_callback = callback

    def connect_refine(self, callback):
        self._refine_callback = callback

    def connect_refine_orientation(self, callback):
        self._refine_orientation_callback = callback

    def connect_undo(self, callback):
        self._undo_callback = callback

    def show_error_message(self, msg):
        self.state.error_message = msg

    def set_lattice(self, parameters):
        self.state.lattice_parameters = parameters

    def get_lattice_type(self):
        return self.state.lattice_type

    def selected_rows(self):
        return self.state.selected_peaks

    def get_peaks(self):
        return self.state.peaks
