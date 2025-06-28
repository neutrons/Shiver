"""
Adapter for the Generate view to connect the presenter to the Trame state.
"""

class TrameGenerateViewAdapter:
    """
    An adapter that mimics the PyQt GenerateView interface for the presenter,
    but updates the Trame state instead of a GUI.
    """

    def __init__(self, state):
        self.state = state
        self._generate_mde_callback = None
        self._save_configuration_callback = None

    def connect_generate_mde_callback(self, callback):
        self._generate_mde_callback = callback

    def connect_save_configuration_callback(self, callback):
        self._save_configuration_callback = callback

    def show_error_message(self, msg):
        self.state.error_message = msg

    def generate_mde_finish_callback(self, activate):
        self.state.generate_mde_in_progress = not activate

    def as_dict(self):
        return self.state.generate_parameters

    def get_save_configuration_filepath(self, default_filename, default_output_dir):
        # This will need to be handled differently in Trame.
        # For now, we will just return a hardcoded value.
        # In a real application, we would use a file dialog.
        return f"{default_output_dir}/{default_filename}.py"
