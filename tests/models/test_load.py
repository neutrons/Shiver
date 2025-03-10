"""Tests for the file loading part of the HistogramModel"""

import time
import os
from mantid.simpleapi import (  # pylint: disable=no-name-in-module
    CreateMDWorkspace,
    SaveMD,
    SaveNexusProcessed,
    LoadEmptyInstrument,
    mtd,
)
from shiver.models.histogram import HistogramModel


def test_load_norm(tmp_path):
    """test for loading normalization file"""
    # create test file
    data = LoadEmptyInstrument(InstrumentName="HYSPEC", DetectorValue=2)
    filename = str(tmp_path / "test_norm.nxs")
    SaveNexusProcessed(data, filename)

    assert "test_norm" not in mtd

    model = HistogramModel()

    model.load(filename, "norm")

    # wait for file to load
    time.sleep(1)

    assert "test_norm" in mtd


def test_load_mde(tmp_path):
    """test for loading MDE file"""
    # create test file
    mde = CreateMDWorkspace(
        Dimensions=4,
        Extents="-10,10,-10,10,-10,10,-10,10",
        Names="A,B,C,DeltaE",
        Units="x,y,z,e",
        Frames="QSample,QSample,QSample,General Frame",
    )
    filename = str(tmp_path / "test_mde.nxs")
    SaveMD(mde, filename)

    assert "test_mde" not in mtd

    model = HistogramModel()

    model.load(filename, "mde")

    # wait for file to load
    time.sleep(1)

    assert "test_mde" in mtd


def test_nonexisted_file():
    """test file doesn't exist"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
    model.connect_error_message(error_callback)

    model.load("/does/not/exist", "mde")

    assert len(errors) == 1
    assert (
        errors[-1] == 'Invalid value for property Filename (string) from string "/does/not/exist":'
        ' When setting value of property "Filename": File "/does/not/exist" not found'
    )


def test_bad_file(tmp_path):
    """test file is wrong type"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
    model.connect_error_message(error_callback)

    filename = tmp_path / "data.nxs"
    filename.write_text("not an NeXus file")

    model.load(str(filename), "mde")

    # wait for algorithm to finish
    time.sleep(1)
    assert len(errors) == 2
    assert errors[-1].startswith(
        f"""Error loading {filename} as mde
ERROR: Kernel::NexusDescriptor couldn't open hdf5 file {filename}"""
    )


def test_load_dataset():
    """test loading dataset from Python file"""
    # We need to use the pre-generated test file
    # as we need to load actual data
    model = HistogramModel()

    # make the dataset dict
    mde_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "mde",
    )
    norm_folder = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "normalization",
    )
    dataset_dict = {
        "MdeName": "merged_mde_MnO_25meV_5K_unpol_178921-178926",
        "MdeFolder": mde_folder,
        "BackgroundMdeName": None,
        "NormalizationDataFile": os.path.join(norm_folder, "TiZr.nxs"),
    }

    ws_data, ws_background, ws_norm = model.load_dataset(dataset_dict)
    assert ws_data == "merged_mde_MnO_25meV_5K_unpol_178921-178926"
    assert ws_background is None
    assert ws_norm == "TiZr"
