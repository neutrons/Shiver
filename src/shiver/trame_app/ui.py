from trame.widgets import html
from trame.ui.vuetify import VApp, VMain, VAppBar, VContainer, VToolbarTitle, VTabs, VTab, VTabItem, VTabsItems
from trame.app import get_server
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
    with VApp() as app:
        VAppBar(app_flat=True, children=[VToolbarTitle("Shiver")])
        with VMain():
            with VContainer():
                with VTabs(v_model=("tab_index", 0), vertical=True):
                    VTab(html.P("Configuration"))
                    VTab(html.P("Sample"))
                    VTab(html.P("Generate"))
                    VTab(html.P("Histogram"))
                
                with VTabsItems(v_model=("tab_index", 0)):
                    with VTabItem():
                        configuration_view()
                    with VTabItem():
                        sample_view()
                    with VTabItem():
                        generate_view()
                    with VTabItem():
                        histogram_view()
                
                corrections_dialog()
                refine_ub_dialog()
                polarized_dialog()

        return app
