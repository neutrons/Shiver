from trame.widgets import vuetify, html

class ConfigurationForm(html.Div):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server
        self._server.state.change("configuration_settings")(self.on_state_change)
        self.update()

    def on_state_change(self, configuration_settings, **kwargs):
        self.update()

    def update(self):
        sections = {}
        if self._server.state.configuration_settings:
            for name, setting_data in self._server.state.configuration_settings.items():
                section_name = setting_data.get("section")
                if section_name not in sections:
                    sections[section_name] = []
                sections[section_name].append({"name": name, **setting_data})

        with self:
            self.clear()
            with vuetify.VExpansionPanels(multiple=True, value=list(sections.keys())):
                for section_name, settings_in_section in sorted(sections.items()):
                    with vuetify.VExpansionPanel():
                        with vuetify.VExpansionPanelHeader():
                            vuetify.VToolbarTitle(section_name)
                        with vuetify.VExpansionPanelContent():
                            for setting in settings_in_section:
                                setting_name = setting["name"]
                                with vuetify.VRow(align="center", dense=True):
                                    with vuetify.VCol(cols=4):
                                        with vuetify.VTooltip(bottom=True):
                                            with html.Template(v_slot_activator="{ on, attrs }"):
                                                html.Div(
                                                    setting_name,
                                                    v_on=("on",),
                                                    v_bind=("attrs",),
                                                )
                                            html.Div(setting["comments"])
                                    with vuetify.VCol(cols=8):
                                        v_model_binding = f"configuration_settings.{setting_name}.value"
                                        if len(setting.get("allowed_values", [])) > 0:
                                            vuetify.VSelect(
                                                v_model=v_model_binding,
                                                items=setting["allowed_values"],
                                                disabled=setting["readonly"],
                                                dense=True, hide_details=True,
                                            )
                                        elif setting.get("type") == "bool":
                                            vuetify.VCheckbox(
                                                v_model=v_model_binding,
                                                disabled=setting["readonly"],
                                                dense=True, hide_details=True,
                                            )
                                        else:
                                            vuetify.VTextField(
                                                v_model=v_model_binding,
                                                disabled=setting["readonly"],
                                                dense=True, hide_details=True,
                                            )

def configuration_view(server):
    """
    Creates the Trame UI for the configuration settings.
    """
    with vuetify.VContainer():
        vuetify.VRow(
            vuetify.VCol(
                vuetify.VCard(
                    children=[
                        vuetify.VCardTitle("Configuration Settings"),
                        vuetify.VCardText(
                            ConfigurationForm(server)
                        ),
                        vuetify.VCardActions(
                            children=[
                                vuetify.VBtn("Apply", click=server.controller.on_config_apply_clicked),
                                vuetify.VBtn("Reset", click=server.controller.on_config_reset_clicked),
                            ]
                        ),
                    ]
                )
            )
        )

