#!/usr/bin/env python
"""Test save methods in histogram model."""

import os

import pytest
from mantid.simpleapi import LoadMD, CreateMDHistoWorkspace  # pylint: disable=no-name-in-module

from shiver.models.histogram import HistogramModel


def test_save_to_ascii(tmp_path):
    """Unit test for exporting MDHistoWorkspace to ASCII file."""
    # load the testing MDHistoWorkspace from test/data folder
    filename = os.path.join(
        os.path.dirname(__file__),
        "../data/hist",
        "plot_1.nxs.h5",
    )
    LoadMD(filename, OutputWorkspace="plot_1")

    model = HistogramModel()

    # save the MDHistoWorkspace to ASCII file
    save_filename = str(tmp_path / "test_save_to_ascii.dat")
    model.save_to_ascii("plot_1", save_filename)

    # check if the file exists
    assert os.path.exists(save_filename)
    with open(save_filename, "r") as f:
        content = f.read()
        # check if the content is not empty
        assert "# Name: plot_1\n" in content
        assert "# Binning" in content

def test_save_to_ascii_invalid_workspace():
    """Unit test for exporting invalid workspace to ASCII file."""
    model = HistogramModel()

    CreateMDHistoWorkspace(SignalInput='1', ErrorInput='1', Dimensionality=1, Extents='-1,1', NumberOfBins='1', Names='A', Units='rlu', OutputWorkspace='invalid_workspace')

    with pytest.raises(ValueError):
        model.save_to_ascii("invalid_workspace", "test_save_to_ascii.dat")

if __name__ == "__main__":
    pytest.main(["-v", __file__])
