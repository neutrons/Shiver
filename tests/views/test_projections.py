"""UI tests for HistogramParameter button"""
import re
from shiver.views.histogram import HistogramParameter


def test_projections_valid_values(qtbot):
    """Test for typing valid values in projections"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    # 1
    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()
    qtbot.keyClicks(histogram_parameters.projection_u, "1,2,3")
    qtbot.keyClicks(histogram_parameters.projection_v, "0,1,0")
    qtbot.keyClicks(histogram_parameters.projection_w, "2,0,1")

    projection_u = histogram_parameters.projection_u.text()
    projection_v = histogram_parameters.projection_v.text()
    projection_w = histogram_parameters.projection_w.text()

    assert projection_u == "1,2,3"
    assert projection_v == "0,1,0"
    assert projection_w == "2,0,1"
    assert histogram_parameters.projections_valid_state is True
    # 2
    color_search = re.compile("background-color: (.*) ")
    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()
    qtbot.keyClicks(histogram_parameters.projection_u, "3,3,0")
    qtbot.keyClicks(histogram_parameters.projection_v, "2,1,2")
    qtbot.keyClicks(histogram_parameters.projection_w, "7,3,1")

    projection_u = histogram_parameters.projection_u.text()
    projection_v = histogram_parameters.projection_v.text()
    projection_w = histogram_parameters.projection_w.text()

    assert projection_u == "3,3,0"
    assert projection_v == "2,1,2"
    assert projection_w == "7,3,1"
    assert histogram_parameters.projections_valid_state is True

    css_style_u = histogram_parameters.projection_u.styleSheet()
    css_style_v = histogram_parameters.projection_v.styleSheet()
    css_style_w = histogram_parameters.projection_w.styleSheet()

    bg_color_u = color_search.search(css_style_u).group(1)
    bg_color_v = color_search.search(css_style_v).group(1)
    bg_color_w = color_search.search(css_style_w).group(1)

    assert bg_color_u == "#ffffff"
    assert bg_color_v == "#ffffff"
    assert bg_color_w == "#ffffff"
    assert histogram_parameters.projections_valid_state is True


def test_projections_invalid_color(qtbot):
    """Test for typing invalid values in projections - background color"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
    color_search = re.compile("background-color: (.*) ")

    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()

    qtbot.keyClicks(histogram_parameters.projection_u, "11")
    qtbot.keyClicks(histogram_parameters.projection_v, "aaa,aaa")
    qtbot.keyClicks(histogram_parameters.projection_w, " ")

    # projection_u = histogram_parameters.projection_u.text()
    # projection_v = histogram_parameters.projection_v.text()
    # projection_w = histogram_parameters.projection_w.text()

    css_style_u = histogram_parameters.projection_u.styleSheet()
    css_style_v = histogram_parameters.projection_v.styleSheet()
    css_style_w = histogram_parameters.projection_w.styleSheet()

    bg_color_u = color_search.search(css_style_u).group(1)
    bg_color_v = color_search.search(css_style_v).group(1)
    bg_color_w = color_search.search(css_style_w).group(1)

    assert bg_color_u == "#ffaaaa"
    assert bg_color_v == "#ffaaaa"
    assert bg_color_w == "#ffaaaa"
    assert histogram_parameters.projections_valid_state is False


def test_projections_co_linear_color(qtbot):
    """Test for typing invalid values in projections - background color"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
    color_search = re.compile("background-color: (.*) ")

    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()

    qtbot.keyClicks(histogram_parameters.projection_u, "1,1,0")
    qtbot.keyClicks(histogram_parameters.projection_v, "1,1,0")
    qtbot.keyClicks(histogram_parameters.projection_w, "1,1,1")

    # projection_u = histogram_parameters.projection_u.text()
    # projection_v = histogram_parameters.projection_v.text()
    # projection_w = histogram_parameters.projection_w.text()

    css_style_u = histogram_parameters.projection_u.styleSheet()
    css_style_v = histogram_parameters.projection_v.styleSheet()
    css_style_w = histogram_parameters.projection_w.styleSheet()

    bg_color_u = color_search.search(css_style_u).group(1)
    bg_color_v = color_search.search(css_style_v).group(1)
    bg_color_w = color_search.search(css_style_w).group(1)

    assert bg_color_u == "#ff0000"
    assert bg_color_v == "#ff0000"
    assert bg_color_w == "#ff0000"
    assert histogram_parameters.projections_valid_state is False