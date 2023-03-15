"""Tests for the file loading part of the HistogramModel"""
import time
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
    mde = CreateMDWorkspace(Dimensions=3, Extents="-10,10,-10,10,-10,10", Names="A,B,C", Units="U,U,U")
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
ERROR: Kernel::NexusHDF5Descriptor couldn't open hdf5 file {filename} with fapl"""
    )
