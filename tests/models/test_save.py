#!/usr/bin/env python
"""Test save methods in histogram model."""
import os
import pytest
from mantid.simpleapi import LoadMD  # pylint: disable=no-name-in-module
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


if __name__ == "__main__":
    pytest.main(["-v", __file__])
