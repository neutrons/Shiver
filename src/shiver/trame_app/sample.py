from trame.app import get_server
from trame.widgets import vuetify, html

server = get_server()
state, ctrl = server.state, server.controller

class SampleForm(html.Div):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        state.add_change_listener("sample_parameters", self.on_state_change)
        self.update()

    def on_state_change(self, sample_parameters, **kwargs):
        self.update()

    def update(self):
        if not state.sample_parameters:
            return

        with self:
            self.clear()
            with vuetify.VRow():
                with vuetify.VCol(cols=6):
                    vuetify.VTextField(
                        label="a",
                        v_model="sample_parameters.a",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=6):
                    vuetify.VTextField(
                        label="b",
                        v_model="sample_parameters.b",
                        dense=True, hide_details=True,
                    )
            with vuetify.VRow():
                with vuetify.VCol(cols=6):
                    vuetify.VTextField(
                        label="c",
                        v_model="sample_parameters.c",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=6):
                    vuetify.VTextField(
                        label="alpha",
                        v_model="sample_parameters.alpha",
                        dense=True, hide_details=True,
                    )
            with vuetify.VRow():
                with vuetify.VCol(cols=6):
                    vuetify.VTextField(
                        label="beta",
                        v_model="sample_parameters.beta",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=6):
                    vuetify.VTextField(
                        label="gamma",
                        v_model="sample_parameters.gamma",
                        dense=True, hide_details=True,
                    )
            with vuetify.VRow():
                with vuetify.VCol(cols=4):
                    vuetify.VTextField(
                        label="ux",
                        v_model="sample_parameters.ux",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=4):
                    vuetify.VTextField(
                        label="uy",
                        v_model="sample_parameters.uy",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=4):
                    vuetify.VTextField(
                        label="uz",
                        v_model="sample_parameters.uz",
                        dense=True, hide_details=True,
                    )
            with vuetify.VRow():
                with vuetify.VCol(cols=4):
                    vuetify.VTextField(
                        label="vx",
                        v_model="sample_parameters.vx",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=4):
                    vuetify.VTextField(
                        label="vy",
                        v_model="sample_parameters.vy",
                        dense=True, hide_details=True,
                    )
                with vuetify.VCol(cols=4):
                    vuetify.VTextField(
                        label="vz",
                        v_model="sample_parameters.vz",
                        dense=True, hide_details=True,
                    )
            with vuetify.VRow():
                with vuetify.VCol():
                    vuetify.VDataTable(
                        headers=[
                            {"text": " ", "value": "c1"},
                            {"text": " ", "value": "c2"},
                            {"text": " ", "value": "c3"},
                        ],
                        items=("ub_matrix", []),
                        hide_default_header=True,
                        hide_default_footer=True,
                    )


def sample_view():
    """
    Creates the Trame UI for the sample parameters.
    """
    with vuetify.VContainer():
        with vuetify.VRow():
            with vuetify.VCol():
                vuetify.VCard(
                    vuetify.VCardTitle("UB Setup"),
                    vuetify.VCardText(
                        SampleForm()
                    ),
                    vuetify.VCardActions(
                        vuetify.VBtn("Apply", click=ctrl.on_sample_apply_clicked),
                        vuetify.VBtn("Load Processed Nexus", click=ctrl.on_sample_load_processed_nexus),
                        vuetify.VBtn("Load Unprocessed Nexus", click=ctrl.on_sample_load_unprocessed_nexus),
                        vuetify.VBtn("Load ISAW", click=ctrl.on_sample_load_isaw),
                        vuetify.VBtn("Save ISAW", click=ctrl.on_sample_save_isaw),
                    ),
                )
