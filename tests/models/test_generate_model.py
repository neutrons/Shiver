#!/usr/env/bin python
"""Test the GenerateModel class"""
import time
import os
import pytest
import shiver.models.convert_dgs_to_single_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
import shiver.models.generate_dgs_mde  # noqa: F401, E402 pylint: disable=unused-import, wrong-import-order
from mantid.simpleapi import Load
from shiver.models.generate import (
    GenerateModel,
    gather_mde_config_dict,
)


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


def test_gather_mde_config_dict():
    """Test the gather_mde_config_dict function."""
    datafile = os.path.join(os.path.dirname(__file__), "../data/mde", "mde_provenance_test.nxs")

    # Load the datafile
    Load(Filename=datafile, OutputWorkspace="mde_provenance_test")

    config_dict = gather_mde_config_dict("mde_provenance_test")

    ref_config_dict = {
        "mde_name": "mde_test",
        "mde_type": "Data",
        "AdvancedOptions": {
            "MaskInputs": [],
            "E_min": "1",
            "E_max": "2",
            "ApplyFilterBadPulses": True,
            "BadPulsesThreshold": "95",
            "Goniometer": "",
        },
        "SampleParameters": {
            "a": "1.00000",
            "b": "1.00000",
            "c": "1.00000",
            "alpha": "90.00000",
            "beta": "90.00000",
            "gamma": "90.00000",
            "u": "0.00000,0.00000,1.00000",
            "v": "1.00000,0.00000,-0.00000",
        },
        "PolarizedOptions": {"PolarizationState": "SF_Pz", "FlippingRatio": "1+x", "PSDA": "1", "SampleLog": "x"},
    }

    assert config_dict["mde_name"] == ref_config_dict["mde_name"]
    assert config_dict["mde_type"] == ref_config_dict["mde_type"]
    # NOTE: do not verify output_dir and filename as they are system dependent
    assert config_dict["AdvancedOptions"] == ref_config_dict["AdvancedOptions"]
    assert config_dict["SampleParameters"] == ref_config_dict["SampleParameters"]
    assert config_dict["PolarizedOptions"] == ref_config_dict["PolarizedOptions"]


if __name__ == "__main__":
    pytest.main([__file__])
