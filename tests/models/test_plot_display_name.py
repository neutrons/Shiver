"""Tests for the plot title creation part of the HistogramModel"""

# pylint: disable=no-name-in-module
from mantid.simpleapi import (
    mtd,
    CreateMDHistoWorkspace,
)
from shiver.models.histogram import HistogramModel


def test_plot_1d_display_name():
    """test for display name of 1D plot"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
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

    model.connect_error_message(error_callback)
    title = model.get_plot_display_name(workspace.name(), 1)
    assert title == "workspace: -10.0<Dim2<10.0, -20.0<Dim3<20.0, -30.0<Dim4<30.0"
    assert len(errors) == 0


def test_plot_2d_display_name():
    """test for display name of plot"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
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

    model.connect_error_message(error_callback)
    title = model.get_plot_display_name(workspace.name(), 2)
    assert title == "workspace: -20.0<Dim3<20.0, -30.0<Dim4<30.0"
    assert len(errors) == 0


def test_plot_3d_display_name():
    """test for display name of 3D plot"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
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

    model.connect_error_message(error_callback)
    title = model.get_plot_display_name(workspace.name(), 3)
    assert title == "workspace"
    assert len(errors) == 0
