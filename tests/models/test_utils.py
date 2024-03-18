"""Tests for shiver.models.utils"""

from shiver.models.utils import flatten_list


def test_flatten_list():
    """Test flatten_list function"""
    assert list(flatten_list("test")) == ["test"]
    assert list(flatten_list(["1", "2", "3"])) == ["1", "2", "3"]
    assert list(flatten_list(["test", ["1", "2"], "3"])) == ["test", "1", "2", "3"]
