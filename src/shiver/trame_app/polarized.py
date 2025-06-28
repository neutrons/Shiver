"""
Trame view for the Polarized Options dialog.
"""
from trame.widgets import vuetify, html
from trame.app import get_server

server = get_server()
state, ctrl = server.state, server.controller

def polarized_dialog():
    """
    Creates the Trame UI for the Polarized Options dialog.
    """
    with vuetify.VDialog(
        v_model=("show_polarized_dialog", False),
        max_width="600px",
    ):
        with vuetify.VCard():
            vuetify.VCardTitle("Polarization Options")
            with vuetify.VCardText():
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VRadioGroup(
                            label="Polarization State",
                            v_model="polarized_options.PolarizationState",
                            row=True,
                            children=[
                                vuetify.VRadio(label="Unpolarized", value="UNP"),
                                vuetify.VRadio(label="Spin Flip", value="SF"),
                                vuetify.VRadio(label="Non Spin Flip", value="NSF"),
                            ],
                        )
                with vuetify.VRow(v_if="polarized_options.PolarizationState !== 'UNP'"):
                    with vuetify.VCol():
                        vuetify.VRadioGroup(
                            label="Polarization Direction",
                            v_model="polarized_options.PolarizationDirection",
                            row=True,
                            children=[
                                vuetify.VRadio(label="Pz (vertical)", value="Pz"),
                                vuetify.VRadio(label="Px", value="Px"),
                                vuetify.VRadio(label="Py", value="Py"),
                            ],
                        )
                with vuetify.VRow(v_if="polarized_options.PolarizationState !== 'UNP'"):
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Flipping Ratio",
                            v_model="polarized_options.FlippingRatio",
                        )
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="Flipping Ratio Sample Log",
                            v_model="polarized_options.FlippingRatioSampleLog",
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="PSDA",
                            v_model="polarized_options.PSDA",
                        )
            with vuetify.VCardActions():
                vuetify.VSpacer()
                vuetify.VBtn("Cancel", click="show_polarized_dialog = false")
                vuetify.VBtn("Apply", click=ctrl.on_apply_polarized_options_clicked)
