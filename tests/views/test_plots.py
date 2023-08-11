#!/usr/bin/env python
"""UI tests for Plots"""
# pylint: disable=no-name-in-module
from mantid.simpleapi import (
    mtd,
    CreateMDHistoWorkspace,
)
from shiver.views.plots import do_default_plot


def test_plot1d(qtbot):
    """Test for 1D plot with intensities and display title"""

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
    qtbot.wait(500)


def test_plot2d(qtbot):
    """Test for 2D plot with intensities and display title"""

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
    assert fig.axes[0].collections[0].get_clim() == (intensity_min, intensity_max)
    qtbot.wait(500)


def test_plot3d(qtbot):
    """Test for 3D plot with intensities"""

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

    qtbot.wait(500)


def test_plot4d(qtbot):
    """Test for 4D plot with intensities"""

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

    qtbot.wait(500)


def test_plot5d(qtbot):
    """Test for 5D plot with intensities -invalid"""

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
