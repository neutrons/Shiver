from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html

from .configuration import configuration_view
from .sample import sample_view
from .generate import generate_view
from .histogram import histogram_view
from .corrections import corrections_dialog
from .refine_ub import refine_ub_dialog
from .polarized import polarized_dialog

def create_ui(server):
    state, ctrl = server.state, server.controller
    state.tab_index = 0
    with SinglePageLayout(server) as layout:
        layout.title.set_text("Shiver")
        with layout.content:
            with vuetify.VContainer():
                with vuetify.VTabs(v_model="tab_index", vertical=True):
                    vuetify.VTab(html.P("Configuration"))
                    vuetify.VTab(html.P("Sample"))
                    vuetify.VTab(html.P("Generate"))
                    vuetify.VTab(html.P("Histogram"))

                with vuetify.VTabsItems(v_model="tab_index"):
                    with vuetify.VTabItem():
                        configuration_view(server)
                    with vuetify.VTabItem():
                        sample_view(server)
                    with vuetify.VTabItem():
                        generate_view(server)
                    with vuetify.VTabItem():
                        histogram_view(server)

                corrections_dialog(server)
                refine_ub_dialog(server)
                polarized_dialog(server)
        return layout
