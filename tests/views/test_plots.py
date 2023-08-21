#!/usr/bin/env python
"""UI tests for Plots"""
import pytest

# pylint: disable=no-name-in-module
from mantid.simpleapi import (
    mtd,
    CreateMDHistoWorkspace,
)
from shiver.views.plots import do_default_plot
from shiver.views.histogram import Histogram


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot1d(qtbot, user_conf_file, monkeypatch):
    """Test for 1D plot with intensities and display title"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-3,3",
        SignalInput=range(0, 10),
        ErrorInput=range(0, 10),
        NumberOfBins="10",
        Names="Dim1",
        Units="MomentumTransfer",
    )

    intensity_min = -1
    intensity_max = 4.5
    title = "1D Plot"
    fig = do_default_plot(workspace, 1, title, {"min": intensity_min, "max": intensity_max})
    assert fig.axes[0].get_title() == title
    assert fig.axes[0].get_ylim() == (intensity_min, intensity_max)
    assert fig.axes[0].get_yscale() == "linear"

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = True
    """
    ],
    indirect=True,
)
def test_plot1d_scale(qtbot, user_conf_file, monkeypatch):
    """Test for 1D plot with log scale"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=1,
        Extents="-3,3",
        SignalInput=range(0, 10),
        ErrorInput=range(0, 10),
        NumberOfBins="10",
        Names="Dim1",
        Units="MomentumTransfer",
    )

    intensity_min = None
    intensity_max = None
    title = "1D Plot"
    fig = do_default_plot(workspace, 1, title, {"min": intensity_min, "max": intensity_max})
    assert fig.axes[0].get_yscale() == "log"
    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot2d(qtbot, user_conf_file, monkeypatch):
    """Test for 2D plot with intensities and display title"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=2,
        Extents="-2,2,-5,5",
        SignalInput=range(0, 100),
        ErrorInput=range(0, 100),
        NumberOfBins="10,10",
        Names="Dim1,Dim2",
        Units="Momentum,Energy",
    )

    intensity_min = -1
    intensity_max = 4.5
    title = "2D Plot"
    fig = do_default_plot(workspace, 2, title, {"min": intensity_min, "max": intensity_max})
    assert fig.axes[0].get_title() == title
    assert fig.axes[1].collections[1].get_clim() == (intensity_min, intensity_max)
    assert fig.axes[1].get_yscale() == "linear"

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = True
    """
    ],
    indirect=True,
)
def test_plot2d_scale(qtbot, user_conf_file, monkeypatch):
    """Test for 2D plot with log scale"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=2,
        Extents="-2,2,-5,5",
        SignalInput=range(0, 100),
        ErrorInput=range(0, 100),
        NumberOfBins="10,10",
        Names="Dim1,Dim2",
        Units="Momentum,Energy",
    )

    intensity_min = 0.001
    intensity_max = 1
    title = "2D Plot"
    fig = do_default_plot(workspace, 2, title, {"min": intensity_min, "max": intensity_max})
    assert fig.axes[0].get_title() == title
    assert fig.axes[1].collections[1].get_clim() == (intensity_min, intensity_max)
    assert fig.axes[1].get_yscale() == "log"

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot3d(qtbot, user_conf_file, monkeypatch):
    """Test for 3D plot with intensities"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=3,
        Extents="-5,5,-10,10,-20,20",
        SignalInput=range(0, 1000),
        ErrorInput=range(0, 1000),
        NumberOfBins="10,10,10",
        Names="Dim1,Dim2,Dim3",
        Units="Energy,Momentum,Other",
    )

    intensity_min = -0.1
    intensity_max = 11.3
    title = None
    view = do_default_plot(workspace, 3, title, {"min": intensity_min, "max": intensity_max})
    assert view.data_view.colorbar.cmin_value == intensity_min
    assert view.data_view.colorbar.cmax_value == intensity_max
    assert view.data_view.colorbar.norm.currentText() == "Linear"

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = True
    """
    ],
    indirect=True,
)
def test_plot3d_scale(qtbot, user_conf_file, monkeypatch):
    """Test for 3D plot with log scale"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=3,
        Extents="-5,5,-10,10,-20,20",
        SignalInput=range(0, 1000),
        ErrorInput=range(0, 1000),
        NumberOfBins="10,10,10",
        Names="Dim1,Dim2,Dim3",
        Units="Energy,Momentum,Other",
    )

    title = None
    view = do_default_plot(workspace, 3, title)
    assert view.data_view.colorbar.norm.currentText() == "Log"
    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot4d(qtbot, user_conf_file, monkeypatch):
    """Test for 4D plot with intensities"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-5,5,-10,10,-20,20,-30,30",
        SignalInput=range(0, 10000),
        ErrorInput=range(0, 10000),
        NumberOfBins="10,10,10,10",
        Names="Dim1,Dim2,Dim3,Dim4",
        Units="M,E,O,EX",
    )

    intensity_min = -10.34
    intensity_max = 12.09
    title = None
    view = do_default_plot(workspace, 4, title, {"min": intensity_min, "max": intensity_max})
    assert view.data_view.colorbar.cmin_value == intensity_min
    assert view.data_view.colorbar.cmax_value == intensity_max
    assert view.data_view.colorbar.norm.currentText() == "Linear"

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = True
    """
    ],
    indirect=True,
)
def test_plot4d_invalid_scale(qtbot, user_conf_file, monkeypatch):
    """Test for 4D plot with intensities"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-5,5,-10,10,-20,20,-30,30",
        SignalInput=range(0, 10000),
        ErrorInput=range(0, 10000),
        NumberOfBins="10,10,10,10",
        Names="Dim1,Dim2,Dim3,Dim4",
        Units="M,E,O,EX",
    )

    intensity_min = -10.34
    intensity_max = 12.09
    title = None
    view = do_default_plot(workspace, 4, title, {"min": intensity_min, "max": intensity_max})
    # mantid plot updates user values if invalid are passed
    assert view.data_view.colorbar.cmin_value == 0.0001
    assert view.data_view.colorbar.cmax_value == intensity_max
    assert view.data_view.colorbar.norm.currentText() == "Log"

    qtbot.wait(500)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot5d(qtbot, user_conf_file, monkeypatch):
    """Test for 5D plot with intensities -invalid"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-3,3,-10,10,-20,20,-30,30",
        SignalInput=range(0, 10000),
        ErrorInput=range(0, 10000),
        NumberOfBins="10,10,10,10",
        Names="Dim1,Dim2,Dim3,Dim4",
        Units="EnergyT,MomentumT,Other,Extra",
    )

    intensity_min = -10.34
    intensity_max = 12.09
    title = None
    view = do_default_plot(workspace, 5, title, {"min": intensity_min, "max": intensity_max})
    assert view is None
    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = name_only
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot_data_name_only(qtbot, user_conf_file, monkeypatch):
    """Test plot inputs"""

    # mock get_oncat_url, client_id and use_notes info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    histogram = Histogram()
    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-3,3,-10,10,-20,20,-30,30",
        SignalInput=range(0, 10000),
        ErrorInput=range(0, 10000),
        NumberOfBins="10,10,10,10",
        Names="Dim1,Dim2,Dim3,Dim4",
        Units="EnergyT,MomentumT,Other,Extra",
    )

    data = histogram.get_plot_data(workspace, 4)
    assert data[0] == "workspace"
    assert data[1]["min"] is None
    assert data[1]["max"] is None

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = full
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot_data_full(qtbot, user_conf_file, monkeypatch):
    """Test plot inputs"""

    # mock plot info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    histogram = Histogram()

    def monk_display_name(ws_name, ndims):
        return f"full {ws_name}: {ndims}"

    histogram.plot_display_name_callback = monk_display_name

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-3,3,-10,10,-20,20,-30,30",
        SignalInput=range(0, 10000),
        ErrorInput=range(0, 10000),
        NumberOfBins="10,10,10,10",
        Names="Dim1,Dim2,Dim3,Dim4",
        Units="EnergyT,MomentumT,Other,Extra",
    )

    intensity_min = -10.34
    intensity_max = 12.09
    histogram.histogram_parameters.dimensions.intensity_min.setText(str(intensity_min))
    histogram.histogram_parameters.dimensions.intensity_max.setText(str(intensity_max))

    data = histogram.get_plot_data(workspace, 4)
    assert data[0] == "full workspace: 4"
    assert data[1]["min"] == intensity_min
    assert data[1]["max"] == intensity_max

    qtbot.wait(100)


@pytest.mark.parametrize(
    "user_conf_file",
    [
        """
        [main_tab.plot]
        title = None
        logarithmic_intensity = False
    """
    ],
    indirect=True,
)
def test_plot_data_none(qtbot, user_conf_file, monkeypatch):
    """Test plot inputs"""

    # mock plot info
    monkeypatch.setattr("shiver.configuration.CONFIG_PATH_FILE", user_conf_file)
    histogram = Histogram()

    # clear mantid workspace
    mtd.clear()

    workspace = CreateMDHistoWorkspace(
        Dimensionality=4,
        Extents="-3,3,-10,10,-20,20,-30,30",
        SignalInput=range(0, 10000),
        ErrorInput=range(0, 10000),
        NumberOfBins="10,10,10,10",
        Names="Dim1,Dim2,Dim3,Dim4",
        Units="EnergyT,MomentumT,Other,Extra",
    )

    intensity_max = 12.09

    histogram.histogram_parameters.dimensions.intensity_max.setText(str(intensity_max))

    data = histogram.get_plot_data(workspace, 4)
    assert data[0] is None
    assert data[1]["min"] is None
    assert data[1]["max"] == intensity_max

    qtbot.wait(100)
