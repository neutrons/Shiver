"""Presenter for the Sample Parameter tab"""
from copy import deepcopy


class SamplePresenter:
    """Sample Parameter presenter"""

    def __init__(self, view, model):
        self._view = view
        self._model = model

        self.model.connect_error_message(self.error_message)

        # get model data
        # self.view.connect_matrix_data(self.handle_matrix_data_from_workspace)
        self.view.connect_sample_data(self.handle_sample_data_from_workspace)

        # update model data
        self.view.connect_lattice_UB_data(self.handle_UB_data_from_lattice)
        self.view.connect_UB_data_lattice(self.handle_lattice_from_UB_data)

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
        ol = self.model.get_lattice_ub()
        params["latt_a"] = ol.a() if (ol) else 0.0000
        params["latt_b"] = ol.b() if (ol) else 0.0000
        params["latt_c"] = ol.c() if (ol) else 0.0000
        params["latt_alpha"] = ol.alpha() if (ol) else 0.0000
        params["latt_beta"] = ol.beta() if (ol) else 0.0000
        params["latt_gamma"] = ol.gamma() if (ol) else 0.0000
        params["latt_ux"] = ol.getuVector()[0] if (ol) else 0.0000
        params["latt_uy"] = ol.getuVector()[1] if (ol) else 0.0000
        params["latt_uz"] = ol.getuVector()[2] if (ol) else 0.0000
        params["latt_vx"] = ol.getvVector()[0] if (ol) else 0.0000
        params["latt_vy"] = ol.getvVector()[1] if (ol) else 0.0000
        params["latt_vz"] = ol.getvVector()[2] if (ol) else 0.0000
        ub_matrix = (
            ol.getUB().tolist()
            if (ol)
            else [[0.0100, 0.0000, 0.0000], [0.0000, 0.0100, 0.0000], [0.0000, 0.0000, 0.0100]]
        )
        params["ub_matrix"] = ub_matrix

        return params

    # def handle_matrix_data_from_workspace(self):
    #    """Get SetUB matrix"""
    #    ub_matrix_dict = {}
    #    matrix_data = self.model.get_matrix_ub()
    #    print("matrix data", matrix_data)
    #    ub_matrix = matrix_data.split(",")
    #    ub_matrix = [ub_matrix[0:3], ub_matrix[3:6], ub_matrix[6::]]
    #    ub_matrix_dict["ub_matrix"] = ub_matrix
    #    return ub_matrix_dict

    def handle_UB_data_from_lattice(self, params):
        """Get SetUB matrix"""
        ub_matrix = self.model.get_UB_data_from_lattice(params)
        if len(ub_matrix) != 0:
            return ub_matrix.tolist()
        return ub_matrix

    def handle_lattice_from_UB_data(self, ub_matrix):
        """Get SetUB matrix"""
        params = {}
        ol = self.model.get_lattice_from_UB_data(ub_matrix)
        if ol:
            params["latt_a"] = ol.a()
            params["latt_b"] = ol.b()
            params["latt_c"] = ol.c()
            params["latt_alpha"] = ol.alpha()
            params["latt_beta"] = ol.beta()
            params["latt_gamma"] = ol.gamma()
            params["latt_ux"] = ol.getuVector()[0]
            params["latt_uy"] = ol.getuVector()[1]
            params["latt_uz"] = ol.getuVector()[2]
            params["latt_vx"] = ol.getvVector()[0]
            params["latt_vy"] = ol.getvVector()[1]
            params["latt_vz"] = ol.getvVector()[2]
        return params

    def handle_apply_button(self, params_dict):
        """Call SetUB mantid algorithm"""
        self.model.set_ub(params_dict)

    def handle_load_button(self, params_dict):
        """Call handle_load_button"""
        print("handle_load_button from presenter")

    def handle_nexus_button(self, filename):
        """Call LoadNexusUB"""
        params = {}
        ol = self.model.load_nexus_ub(filename)
        if ol:
            params["latt_a"] = ol.a()
            params["latt_b"] = ol.b()
            params["latt_c"] = ol.c()
            params["latt_alpha"] = ol.alpha()
            params["latt_beta"] = ol.beta()
            params["latt_gamma"] = ol.gamma()
            params["latt_ux"] = ol.getuVector()[0]
            params["latt_uy"] = ol.getuVector()[1]
            params["latt_uz"] = ol.getuVector()[2]
            params["latt_vx"] = ol.getvVector()[0]
            params["latt_vy"] = ol.getvVector()[1]
            params["latt_vz"] = ol.getvVector()[2]
            params["ub_matrix"] = deepcopy(ol.getUB())
        return params

    def handle_isaw_button(self, filename):
        """Call LoadIsawUB"""
        params = {}
        ol = self.model.load_isaw_ub(filename)
        if ol:
            params["latt_a"] = ol.a()
            params["latt_b"] = ol.b()
            params["latt_c"] = ol.c()
            params["latt_alpha"] = ol.alpha()
            params["latt_beta"] = ol.beta()
            params["latt_gamma"] = ol.gamma()
            params["latt_ux"] = ol.getuVector()[0]
            params["latt_uy"] = ol.getuVector()[1]
            params["latt_uz"] = ol.getuVector()[2]
            params["latt_vx"] = ol.getvVector()[0]
            params["latt_vy"] = ol.getvVector()[1]
            params["latt_vz"] = ol.getvVector()[2]
            params["ub_matrix"] = deepcopy(ol.getUB())
            print(ol)
            print(ol.getUB())
            print('params["ub_matrix"]', params["ub_matrix"])
        return params

    def error_message(self, msg):
        """Pass error message to the view"""
        print("self.view.dialog", self.view.dialog)
        self.view.get_error_message(msg)
