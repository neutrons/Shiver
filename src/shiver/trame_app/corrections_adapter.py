"""
Adapter for the Corrections view to connect the presenter to the Trame state.
"""

class TrameCorrectionsAdapter:
    """
    An adapter that mimics the PyQt CorrectionsView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._apply_callback = None

    def connect_apply_callback(self, callback):
        self._apply_callback = callback

    def apply(self, ws_name, detailed_balance, hyspec_polarizer_transmission, temperature, debye_waller_factor, u2, magnetic_structure_factor, ion_name):
        if self._apply_callback:
            self._apply_callback(
                ws_name,
                detailed_balance,
                hyspec_polarizer_transmission,
                temperature,
                debye_waller_factor,
                u2,
                magnetic_structure_factor,
                ion_name,
            )

    def show_error_message(self, msg):
        self.state.error_message = msg
