from trame.widgets import vuetify, html

class GenerateForm(html.Div):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server
        self._server.state.change("generate_parameters")(self.on_state_change)
        self.update()

    def on_state_change(self, generate_parameters, **kwargs):
        self.update()

    def update(self):
        if not self._server.state.generate_parameters:
            self._server.state.generate_parameters = {
                "mde_name": "mde",
                "output_dir": "/tmp",
                "mde_type": "Data",
                "filename": "",
                "instrument": "HYS",
                "ipts": "",
                "e_min": "-0.5",
                "e_max": "0.5",
                "e_step": "0.01",
            }

        with self:
            self.clear()
            with vuetify.VTextField(
                label="MDE Name",
                v_model="generate_parameters.mde_name",
                dense=True, hide_details=True,
            ):
                with vuetify.VTooltip(
                    "The name of the multi-dimensional event workspace.",
                    bottom=True,
                    v_slot_activator="{ on, attrs }",
                ):
                    vuetify.VIcon("mdi-help-circle-outline", v_on=("on",), v_bind=("attrs",))
            with vuetify.VTextField(
                label="Output Directory",
                v_model="generate_parameters.output_dir",
                dense=True, hide_details=True,
            ):
                with vuetify.VTooltip(
                    "The location where the multi-dimensional event workspace will be saved.",
                    bottom=True,
                    v_slot_activator="{ on, attrs }",
                ):
                    vuetify.VIcon("mdi-help-circle-outline", v_on=("on",), v_bind=("attrs",))
            vuetify.VRadioGroup(
                v_model="generate_parameters.mde_type",
                row=True,
                children=[
                    vuetify.VRadio(label="Data", value="Data"),
                    vuetify.VRadio(label="Background (angle integrated)", value="Background (angle integrated)"),
                    vuetify.VRadio(label="Background (minimized by angle and energy)", value="Background (minimized by angle and energy)"),
                ],
            )
            vuetify.VTextField(
                label="File Names",
                v_model="generate_parameters.filename",
                dense=True, hide_details=True,
            )
            vuetify.VTextField(
                label="Incident Energy (Ei)",
                v_model="generate_parameters.e_min",
                dense=True, hide_details=True,
            )

def generate_view(server):
    """
    Creates the Trame UI for the Generate tab.
    """
    with vuetify.VContainer():
        with vuetify.VRow():
            with vuetify.VCol():
                vuetify.VCard(
                    children=[
                        vuetify.VCardTitle("Generate MDE"),
                        vuetify.VCardText(
                            GenerateForm(server)
                        ),
                        vuetify.VCardActions(
                            children=[
                                vuetify.VBtn(
                                    "Generate",
                                    click=server.controller.on_generate_mde_clicked,
                                    disabled=("generate_mde_in_progress", False),
                                ),
                                vuetify.VBtn(
                                    "Save Configuration",
                                    click=server.controller.on_save_configuration_clicked,
                                ),
                            ]
                        ),
                    ]
                )
