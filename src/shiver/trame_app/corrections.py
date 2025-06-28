from trame.widgets import vuetify

def corrections_dialog(server):
    """
    Creates the Trame UI for the Corrections dialog.
    """
    with vuetify.VDialog(
        v_model=("show_corrections_dialog", False),
        max_width="500px",
    ) as dialog:
        with vuetify.VCard():
            with vuetify.VCardTitle():
                vuetify.VToolbarTitle("Corrections")
            with vuetify.VCardText():
                vuetify.VCheckbox(
                    v_model="corrections.detailed_balance",
                    label="Detailed balance",
                )
                vuetify.VTextField(
                    v_model="corrections.temperature",
                    label="Temperature",
                    disabled=("!corrections.detailed_balance",),
                )
                vuetify.VCheckbox(
                    v_model="corrections.hyspec_polarizer_transmission",
                    label="Hyspec polarizer transmission",
                )
                vuetify.VCheckbox(
                    v_model="corrections.debye_waller_factor",
                    label="Debye-Waller Correction",
                )
                vuetify.VTextField(
                    v_model="corrections.u2",
                    label="Mean squared displacement",
                    disabled=("!corrections.debye_waller_factor",),
                )
                vuetify.VCheckbox(
                    v_model="corrections.magnetic_structure_factor",
                    label="Magnetic structure factor",
                )
                vuetify.VSelect(
                    v_model="corrections.ion_name",
                    label="Ion Name",
                    items=("ions_list", []),
                    disabled=("!corrections.magnetic_structure_factor",),
                )
            with vuetify.VCardActions():
                vuetify.VSpacer()
                vuetify.VBtn(
                    "Cancel",
                    click="show_corrections_dialog = false",
                )
                vuetify.VBtn(
                    "Apply",
                    click=server.controller.on_apply_corrections_clicked,
                )
        dialog.add_child(vuetify.VCard())
    return dialog
