"""Tests for the file loading part of the HistogramModel"""
from shiver.models.histogram import HistogramModel


def test_symmetry_valid():
    """test for loading normalization file"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
    model.connect_error_message(error_callback)
    model.symmetry_operations("x,y,z")

    assert len(errors) == 0


def test_symmetry_invalid():
    """test for loading MDE file"""
    errors = []

    def error_callback(msg):
        errors.append(msg)

    model = HistogramModel()
    model.connect_error_message(error_callback)
    model.symmetry_operations("cccc")

    assert len(errors) == 1
    assert (
        errors[-1]
        == "Invalid symmentry value: cccc::Parse error: Additional characters at end of string: 'cccc'. in \"cccc\" on line 0 \n"
    )
