"""
Adapter for the Polarized view to connect the presenter to the Trame state.
"""

class TramePolarizedAdapter:
    """
    An adapter that mimics the PyQt PolarizedView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._apply_submit_callback = None
        self._populate_polarized_options_callback = None

    def connect_apply_submit(self, callback):
        self._apply_submit_callback = callback

    def connect_populate_polarized_options(self, callback):
        self._populate_polarized_options_callback = callback

    def get_error_message(self, msg):
        self.state.error_message = msg

    def get_polarized_options_dict(self):
        return self.state.polarized_options

    def set_polarized_options_dict(self, options):
        self.state.polarized_options = options
