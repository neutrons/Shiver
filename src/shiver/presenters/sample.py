"""Presenter for the Sample Parameter tab"""
 

class SamplePresenter:
    """Sample Parameter presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self.model.connect_error_message(self.error_message)
        
        #get model data
        self.view.connect_matrix_data(self.handle_matrix_data_from_workspace) 
        self.view.connect_lattice_data(self.handle_lattice_data_from_workspace) 
               
        #buttons
        self.view.connect_apply_submit(self.handle_apply_button)
        self.view.connect_load_submit(self.handle_load_button)
        self.view.connect_nexus_submit(self.handle_nexus_button)       
        self.view.connect_isaw_submit(self.handle_isaw_button)
        

    @property
    def view(self):
        """Return the view for this presenter"""
        return self._view

    @property
    def model(self):
        """Return the model for this presenter"""
        return self._model

    def handle_lattice_data_from_workspace(self):
        """Get SetUB matrix"""
        return self.model.get_lattice_ub()

    def handle_matrix_data_from_workspace(self):
        """Get SetUB matrix"""
        return self.model.get_matrix_ub()

    def handle_apply_button(self, params_dict):
        """Call SetUB mantid algorithm"""
        self.model.set_ub(params_dict)

    def handle_load_button(self, params_dict):
        """Call handle_load_button"""
        print("handle_load_button from presenter")
        
    def handle_nexus_button(self, filename):
        """Call LoadNexusUB"""
        self.model.load_nexus_ub(filename)    

    def handle_isaw_button(self, filename):
        """Call LoadIsawUB"""
        ol = self.model.load_isaw_ub(filename)
        return ol

    def error_message(self, msg):
        """Pass error message to the view"""
        print("self.view.dialog", self.view.dialog)
        self.view.get_error_message(msg)
