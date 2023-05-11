#!/usr/env/bin python
"""Test the GenerateModel class"""
import time
import os
import pytest
from shiver.models.generate import GenerateModel


def test_generate_mde_model(tmpdir):
    """Test the GenerateMDE model.

    Note:
    -----
    The validity of the algorithm is ensured in test_generatemde.py
    """
    datafile = os.path.join(os.path.dirname(__file__), "../data/raw", "SEQ_124735.nxs.h5")

    model = GenerateModel()
    assert model.error_callback is None
    assert model.algorithm_observer == set()

    err_msg = []

    def error_callback(msg, *args, **kwargs):  # pylint: disable=unused-argument
        err_msg.append(msg)

    model.connect_error_message(error_callback)

    # correct config_dict should not raise error
    datafile = os.path.join(
        os.path.dirname(__file__),
        "../data/raw",
        "HYS_178921.nxs.h5",
    )

    config_dict = {
        "mde_name": "test",
        "output_dir": tmpdir,
        "mde_type": "Data",
        "filename": datafile,
    }
    model.generate_mde(config_dict)
    time.sleep(1)  # wait for async thread to finish
    assert len(err_msg) == 0  # no new error message


if __name__ == "__main__":
    pytest.main([__file__])
