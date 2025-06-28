"""
Trame view for the Refine UB dialog.
"""
from trame.widgets import vuetify, html
from trame.app import get_server

server = get_server()
state, ctrl = server.state, server.controller

def refine_ub_dialog():
    """
    Creates the Trame UI for the Refine UB dialog.
    """
    with vuetify.VDialog(
        v_model=("show_refine_ub_dialog", False),
        max_width="800px",
    ):
        with vuetify.VCard():
            vuetify.VCardTitle("Refine UB")
            with vuetify.VCardText():
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VBtn("Predict Peaks", click=ctrl.on_predict_peaks_clicked)
                        vuetify.VBtn("Recenter", click=ctrl.on_recenter_peaks_clicked)
                        vuetify.VBtn("Refine", click=ctrl.on_refine_clicked)
                        vuetify.VBtn("Refine Orientation", click=ctrl.on_refine_orientation_clicked)
                        vuetify.VBtn("Undo", click=ctrl.on_undo_clicked)
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VDataTable(
                            headers=("refine_ub_headers", []),
                            items=("refine_ub_peaks", []),
                            show_select=True,
                            v_model="selected_peaks",
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="a",
                            v_model="lattice_parameters.a",
                            readonly=True,
                        )
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="b",
                            v_model="lattice_parameters.b",
                            readonly=True,
                        )
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="c",
                            v_model="lattice_parameters.c",
                            readonly=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="alpha",
                            v_model="lattice_parameters.alpha",
                            readonly=True,
                        )
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="beta",
                            v_model="lattice_parameters.beta",
                            readonly=True,
                        )
                    with vuetify.VCol():
                        vuetify.VTextField(
                            label="gamma",
                            v_model="lattice_parameters.gamma",
                            readonly=True,
                        )
                with vuetify.VRow():
                    with vuetify.VCol():
                        vuetify.VSelect(
                            label="Lattice Type",
                            items=("lattice_types", []),
                            v_model="lattice_type",
                        )

            with vuetify.VCardActions():
                vuetify.VSpacer()
                vuetify.VBtn(
                    "Close",
                    click="show_refine_ub_dialog = false",
                )
