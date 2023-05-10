"""Functions to plot histgrams"""
import matplotlib.pyplot as plt
from mantidqt.widgets.sliceviewer.presenters.presenter import SliceViewer
from mantidqt.plotting.functions import manage_workspace_names


@manage_workspace_names
def do_colorfill_plot(workspaces):
    """Create a colormesh plot for the provided workspace"""
    fig, axis = plt.subplots(subplot_kw={"projection": "mantid"})
    colormesh = axis.pcolormesh(workspaces[0])
    axis.set_title(workspaces[0].name())
    fig.colorbar(colormesh)
    fig.show()


@manage_workspace_names
def do_slice_viewer(workspaces, parent=None):
    """Open sliceviewer for the provided workspace"""
    presenter = SliceViewer(ws=workspaces[0], parent=parent)
    presenter.view.show()
