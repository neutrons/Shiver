from trame.widgets import vuetify, html
from trame_plotly.widgets import plotly

class HistogramForm(html.Div):
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server
        self._server.state.change("histogram_parameters")(self.on_state_change)
        self.update()

    def on_state_change(self, histogram_parameters, **kwargs):
        self.update()

    def update(self):
        if not self._server.state.histogram_parameters:
            self._server.state.histogram_parameters = {
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
    def __init__(self, server, **kwargs):
        super().__init__(**kwargs)
        self._server = server
        self._server.state.change("plot_data")(self.on_state_change)
        self.update()

    def on_state_change(self, plot_data, **kwargs):
        self.update()

    def update(self):
        if self._server.state.plot_data:
            with self:
                self.clear()
                plotly.Plotly(
                    data=("plot_data",),
                )

def histogram_view(server):
    """
    Creates the Trame UI for the Histogram tab.
    """
    with vuetify.VContainer():
        with vuetify.VRow():
            with vuetify.VCol():
                vuetify.VCard(
                    children=[
                        vuetify.VCardTitle("Histogram"),
                        vuetify.VCardText(
                            HistogramForm(server)
                        ),
                        vuetify.VCardActions(
                            children=[
                                vuetify.VBtn(
                                    "Polarized",
                                    click=server.controller.on_open_polarized_dialog,
                                ),
                                vuetify.VBtn(
                                    "Refine UB",
                                    click=server.controller.on_open_refine_ub_dialog,
                                ),
                                vuetify.VBtn(
                                    "Corrections",
                                    click=server.controller.on_open_corrections_dialog,
                                ),
                                vuetify.VBtn(
                                    "Make Slice",
                                    click=server.controller.on_make_slice_clicked,
                                    disabled=("makeslice_in_progress", False),
                                ),
                            ]
                        ),
                    ]
                )
        with vuetify.VRow():
            with vuetify.VCol():
                vuetify.VCard(
                    children=[
                        vuetify.VCardTitle("Plot"),
                        vuetify.VCardText(
                            PlotView(server)
                        ),
                    ]
                )
