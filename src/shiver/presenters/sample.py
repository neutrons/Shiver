"""Presenter for the Sample Parameters dialog"""
from copy import deepcopy


class SamplePresenter:
    """Sample Parameter presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self.model.connect_error_message(self.error_message)

        # get model data
        self.view.connect_sample_data(self.handle_sample_data_from_workspace)

        # check valid data
        self.view.connect_matrix_state(self.handle_matrix_state)
        self.view.connect_lattice_state(self.handle_lattice_state)

        # update model data
        self.view.connect_ub_matrix_from_lattice(self.handle_ub_matrix_from_lattice)
        self.view.connect_lattice_from_ub_matrix(self.handle_lattice_from_ub_matrix)

        # buttons
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

    def handle_sample_data_from_workspace(self):
        """Get SetUB matrix"""
        params = {}
        oriented_lattice = self.model.get_lattice_ub()
        params["latt_a"] = oriented_lattice.a() if (oriented_lattice) else 0.0000
        params["latt_b"] = oriented_lattice.b() if (oriented_lattice) else 0.0000
        params["latt_c"] = oriented_lattice.c() if (oriented_lattice) else 0.0000
        params["latt_alpha"] = oriented_lattice.alpha() if (oriented_lattice) else 0.0000
        params["latt_beta"] = oriented_lattice.beta() if (oriented_lattice) else 0.0000
        params["latt_gamma"] = oriented_lattice.gamma() if (oriented_lattice) else 0.0000
        params["latt_ux"] = oriented_lattice.getuVector()[0] if (oriented_lattice) else 0.0000
        params["latt_uy"] = oriented_lattice.getuVector()[1] if (oriented_lattice) else 0.0000
        params["latt_uz"] = oriented_lattice.getuVector()[2] if (oriented_lattice) else 0.0000
        params["latt_vx"] = oriented_lattice.getvVector()[0] if (oriented_lattice) else 0.0000
        params["latt_vy"] = oriented_lattice.getvVector()[1] if (oriented_lattice) else 0.0000
        params["latt_vz"] = oriented_lattice.getvVector()[2] if (oriented_lattice) else 0.0000
        ub_matrix = (
            oriented_lattice.getUB().tolist()
            if (oriented_lattice)
            else [[0.0100, 0.0000, 0.0000], [0.0000, 0.0100, 0.0000], [0.0000, 0.0000, 0.0100]]
        )
        params["ub_matrix"] = ub_matrix

        return params

    def handle_matrix_state(self, ub_matrix):
        """Validate UB matrix"""
        return self.model.validate_matrix(ub_matrix)

    def handle_lattice_state(self, params):
        """Validate lattices"""
        return self.model.validate_lattice(params)

    def handle_ub_matrix_from_lattice(self, params):
        """Get SetUB matrix"""
        ub_matrix = self.model.get_ub_matrix_from_lattice(params)
        if len(ub_matrix) != 0:
            return ub_matrix.tolist()
        return ub_matrix

    def handle_lattice_from_ub_matrix(self, ub_matrix):
        """Get SetUB matrix"""
        params = {}
        oriented_lattice = self.model.get_lattice_from_ub_matrix(ub_matrix)
        params = self.copy_params_to_dict(oriented_lattice, params)
        return params

    def handle_apply_button(self, params_dict):
        """Call SetUB mantid algorithm"""
        return self.model.set_ub(params_dict)

    def handle_load_button(self, filename):
        """Call LoadNexusProcessed"""
        params = {}
        oriented_lattice = self.model.load_nexus_processed(filename)
        params = self.copy_params_to_dict(oriented_lattice, params)
        return params

    def handle_nexus_button(self, filename):
        """Call LoadNexusUB"""
        params = {}
        oriented_lattice = self.model.load_nexus_ub(filename)
        params = self.copy_params_to_dict(oriented_lattice, params)
        return params

    def handle_isaw_button(self, filename):
        """Call LoadIsawUB"""
        params = {}
        oriented_lattice = self.model.load_isaw_ub(filename)
        params = self.copy_params_to_dict(oriented_lattice, params)
        return params

    def error_message(self, msg):
        """Pass error message to the view"""
        self.view.get_error_message(msg)

    def copy_params_to_dict(self, oriented_lattice, params):
        """Copy all oriented lattice and ub matrix to params dictionary"""
        if oriented_lattice is not None:
            params["latt_a"] = oriented_lattice.a()
            params["latt_b"] = oriented_lattice.b()
            params["latt_c"] = oriented_lattice.c()
            params["latt_alpha"] = oriented_lattice.alpha()
            params["latt_beta"] = oriented_lattice.beta()
            params["latt_gamma"] = oriented_lattice.gamma()
            params["latt_ux"] = oriented_lattice.getuVector()[0]
            params["latt_uy"] = oriented_lattice.getuVector()[1]
            params["latt_uz"] = oriented_lattice.getuVector()[2]
            params["latt_vx"] = oriented_lattice.getvVector()[0]
            params["latt_vy"] = oriented_lattice.getvVector()[1]
            params["latt_vz"] = oriented_lattice.getvVector()[2]
            params["ub_matrix"] = deepcopy(oriented_lattice.getUB())
        return params
