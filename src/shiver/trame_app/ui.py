from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, html

from .configuration import configuration_view
from .sample import sample_view
from .generate import generate_view
from .histogram import histogram_view
from .corrections import corrections_dialog
from .refine_ub import refine_ub_dialog
from .polarized import polarized_dialog

server = get_server()
state, ctrl = server.state, server.controller

def create_ui():
    state.tab_index = 0
    with SinglePageLayout(server) as layout:
        layout.title.set_text("Shiver")
        with layout.content:
            with vuetify.VContainer():
                with vuetify.VTabs(v_model=("tab_index", 0), vertical=True):
                    vuetify.VTab(html.P("Configuration"))
                    vuetify.VTab(html.P("Sample"))
                    vuetify.VTab(html.P("Generate"))
                    vuetify.VTab(html.P("Histogram"))

                with vuetify.VTabsItems(v_model=("tab_index", 0)):
                    with vuetify.VTabItem():
                        configuration_view()
                    with vuetify.VTabItem():
                        sample_view()
                    with vuetify.VTabItem():
                        generate_view()
                    with vuetify.VTabItem():
                        histogram_view()

                corrections_dialog()
                refine_ub_dialog()
                polarized_dialog()
        return layout
