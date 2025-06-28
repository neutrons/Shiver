from trame.app import get_server
from trame.widgets import vuetify, html
from trame_plotly.widgets import plotly

server = get_server()
state, ctrl = server.state, server.controller

class HistogramForm(html.Div):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        state.add_change_listener("histogram_parameters", self.on_state_change)
        self.update()

    def on_state_change(self, histogram_parameters, **kwargs):
        self.update()

    def update(self):
        if not state.histogram_parameters:
            state.histogram_parameters = {
                "InputWorkspace": "",
                "QDimension0": "1,0,0",
                "QDimension1": "0,1,0",
                "QDimension2": "0,0,1",
                "Dimension0Name": "QDimension0",
                "Dimension0Binning": ",,",
                "Dimension1Name": "QDimension1",
                "Dimension1Binning": ",,",
                "Dimension2Name": "QDimension2",
                "Dimension2Binning": ",,",
                "Dimension3Name": "DeltaE",
                "Dimension3Binning": "-0.5,0.5",
                "SymmetryOperations": "",
                "Smoothing": "0",
                "Name": "slice",
            }

        with self:
            self.clear()
            vuetify.VTextField(
                label="Input Workspace",
                v_model="histogram_parameters.InputWorkspace",
                dense=True, hide_details=True,
            )
            vuetify.VTextField(
                label="Output Name",
                v_model="histogram_parameters.Name",
                dense=True, hide_details=True,
            )
            # Add more fields for other parameters as needed

class PlotView(html.Div):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        state.add_change_listener("plot_data", self.on_state_change)
        self.update()

    def on_state_change(self, plot_data, **kwargs):
        self.update()

    def update(self):
        if state.plot_data:
            with self:
                self.clear()
                plotly.Plotly(
                    data=("plot_data",),
                )

def histogram_view():
    """
    Creates the Trame UI for the Histogram tab.
    """
    with vuetify.VContainer():
        with vuetify.VRow():
            with vuetify.VCol():
                vuetify.VCard(
                    vuetify.VCardTitle("Histogram"),
                    vuetify.VCardText(
                        HistogramForm()
                    ),
                    vuetify.VCardActions(
                        vuetify.VBtn(
                            "Polarized",
                            click=ctrl.on_open_polarized_dialog,
                        ),
                        vuetify.VBtn(
                            "Refine UB",
                            click=ctrl.on_open_refine_ub_dialog,
                        ),
                        vuetify.VBtn(
                            "Corrections",
                            click=ctrl.on_open_corrections_dialog,
                        ),
                        vuetify.VBtn(
                            "Make Slice",
                            click=ctrl.on_make_slice_clicked,
                            disabled=("makeslice_in_progress", False),
                        ),
                    ),
                )
        with vuetify.VRow():
            with vuetify.VCol():
                vuetify.VCard(
                    vuetify.VCardTitle("Plot"),
                    vuetify.VCardText(
                        PlotView()
                    ),
                )
