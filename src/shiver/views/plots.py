"""Functions to plot histgrams"""
import matplotlib.pyplot as plt
from mantidqt.widgets.sliceviewer.presenters.presenter import SliceViewer
from mantidqt.plotting.functions import manage_workspace_names, plot_md_ws_from_names


@manage_workspace_names
def do_1d_plot(workspaces, display_name, intensity_limits=None):
    """Create an 1D plot for the provided workspace"""
    fig = plot_md_ws_from_names(workspaces, False, False)
    plot_title = display_name if display_name else workspaces[0].name()
    min_limit = intensity_limits["min"] if intensity_limits is not None and "min" in intensity_limits else None
    max_limit = intensity_limits["max"] if intensity_limits is not None and "max" in intensity_limits else None
    fig.axes[0].set_ylim(min_limit, max_limit)
    fig.canvas.manager.set_window_title(display_name)
    fig.axes[0].set_title(plot_title)
    return fig


@manage_workspace_names
def do_colorfill_plot(workspaces, display_name=None, intensity_limits=None):
    """Create a colormesh plot for the provided workspace"""
    fig, axis = plt.subplots(subplot_kw={"projection": "mantid"})
    plot_title = display_name or workspaces[0].name()
    min_limit = intensity_limits["min"] if intensity_limits is not None and "min" in intensity_limits else None
    max_limit = intensity_limits["max"] if intensity_limits is not None and "max" in intensity_limits else None
    colormesh = axis.pcolormesh(workspaces[0], vmin=min_limit, vmax=max_limit)
    axis.set_title(plot_title)
    fig.canvas.manager.set_window_title(plot_title)

    fig.colorbar(colormesh)
    fig.show()
    return fig


@manage_workspace_names
def do_slice_viewer(workspaces, parent=None, intensity_limits=None):
    """Open sliceviewer for the provided workspace"""
    presenter = SliceViewer(ws=workspaces[0], parent=parent)

    min_limit = (
        intensity_limits["min"]
        if intensity_limits is not None and intensity_limits["min"] is not None
        else presenter.view.data_view.colorbar.cmin_value
    )
    max_limit = (
        intensity_limits["max"]
        if intensity_limits is not None and intensity_limits["max"] is not None
        else presenter.view.data_view.colorbar.cmax_value
    )
    presenter.view.data_view.colorbar.cmin.setText(f"{min_limit:.4}")
    presenter.view.data_view.colorbar.clim_changed()
    presenter.view.data_view.colorbar.cmax.setText(f"{max_limit:.4}")
    presenter.view.data_view.colorbar.clim_changed()

    presenter.view.show()
    return presenter.view


def do_default_plot(workspace, ndims, display_name=None, intensity_limits=None):
    """Create the default plot for the workspace and number of dimensions"""
    if ndims == 1:
        return do_1d_plot([workspace], display_name, intensity_limits)
    if ndims == 2:
        return do_colorfill_plot([workspace], display_name, intensity_limits)
    if ndims in (3, 4):
        return do_slice_viewer([workspace], intensity_limits=intensity_limits)
    return None
