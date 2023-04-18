#!/usr/env/bin python
"""Test the generate view."""
import pytest
from shiver.views.generate import (
    MDEType,
    is_valid_name,
    has_special_char,
)


def test_mde_name_check():
    """Test the mde name check."""
    assert is_valid_name("test") is True
    assert is_valid_name("_test") is True
    assert is_valid_name("test0") is True
    assert is_valid_name("0test") is False
    assert is_valid_name("?test_0") is False
    assert is_valid_name("test?_0") is False
    assert is_valid_name("test-0") is False

def test_path_check():
    """Test the path check function."""
    assert has_special_char("/tmp/test") is False
    assert has_special_char("/tmp/test?") is True
    assert has_special_char("/tmp/test/me#") is True
    assert has_special_char("C:\\tmp") is False

def test_mde_type_widget(qtbot):
    """Test for the generate widget (view)."""
    mde_type_widget = MDEType()
    qtbot.addWidget(mde_type_widget)
    mde_type_widget.show()

    errors_list = []
    def error_callback(msg):
        """Callback for error."""
        errors_list.append(msg)

    mde_type_widget.connect_error_callback(error_callback)

    # check happy path (ui -> dict)
    mde_type_widget.mde_name.setText("test")
    mde_type_widget.output_dir.setText("/tmp/test")
    mde_type_widget.mde_type_background_integrated.setChecked(True)
    rst_dict = mde_type_widget.as_dict()
    #
    ref_dict = {
        "mde_name": "test",
        "output_dir": "/tmp/test",
        "mde_type": "Background (angle integrated)",
    }
    #
    assert rst_dict == ref_dict

    # check happy path (dict -> ui)
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict(ref_dict)
    #
    assert mde_type_widget.mde_name.text() == "test"
    assert mde_type_widget.output_dir.text() == "/tmp/test"
    assert mde_type_widget.mde_type_background_integrated.isChecked() is True
    #
    ref_dict["mde_type"] = "Data"
    mde_type_widget.populate_from_dict(ref_dict)
    assert mde_type_widget.mde_type_data.isChecked() is True
    #
    ref_dict["mde_type"] = "Background (minimized by angle and energy)"
    mde_type_widget.populate_from_dict(ref_dict)
    assert mde_type_widget.mde_type_background_minimized.isChecked() is True

    # check error_1: invalid mde name
    mde_type_widget.re_init_widget()
    mde_type_widget.mde_name.setText("test?")
    assert mde_type_widget.as_dict() == {}
    assert errors_list[-1] == "Invalid MDE name."

    # check error_2: empty output dir
    mde_type_widget.re_init_widget()
    mde_type_widget.mde_name.setText("test")
    mde_type_widget.output_dir.setText(" ")
    assert mde_type_widget.as_dict() == {}
    assert errors_list[-1] == "Output directory cannot be empty."

    # check error_3: invalid output dir
    mde_type_widget.re_init_widget()
    mde_type_widget.mde_name.setText("test")
    mde_type_widget.output_dir.setText("/tmp/test?")
    assert mde_type_widget.as_dict() == {}
    assert errors_list[-1] == "Output directory cannot contain special characters."

    # check error_4: invalid dict used to populate UI
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict({"mde_name": "test?"})
    assert errors_list[-1] == "Invalid MDE name found in history."
    #
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict({
        "mde_name": "test",
        "output_dir": "/tmp/test?",
        })
    assert errors_list[-1] == "Invalid output directory found in history."
    #
    mde_type_widget.re_init_widget()
    mde_type_widget.populate_from_dict({
        "mde_name": "test",
        "output_dir": "/tmp/test",
        "mde_type": "Data_",
    })
    assert errors_list[-1] == "Invalid MDE type found in history."


if __name__ == "__main__":
    pytest.main([__file__])
