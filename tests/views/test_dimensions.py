"""UI tests for HistogramParameter button"""
import re
from qtpy import QtCore

# QGroupBox
from shiver.views.histogram import HistogramParameter


def test_dimensions_radio_btn(qtbot):
    """Test for selecting the Dimension step size radio buttons and accessing the steps"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    # set steps
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "0.5")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step2, "0.2")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step3, "0.02")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step4, "2")

    # set 4D volume
    qtbot.mouseClick(histogram_parameters.cut_4d, QtCore.Qt.LeftButton)
    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimensions.combo_step2.text() == "0.2"
    assert histogram_parameters.dimensions.combo_step3.text() == "0.02"
    assert histogram_parameters.dimensions.combo_step4.text() == "2"
    assert histogram_parameters.dimensions.steps_valid_state() is True

    histogram_parameters.dimensions.combo_step1.clear()
    histogram_parameters.dimensions.combo_step2.clear()
    histogram_parameters.dimensions.combo_step3.clear()
    histogram_parameters.dimensions.combo_step4.clear()

    # set steps
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "0.5")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step2, "0.2")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step3, "0.02")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step4, "2")

    # set 3D volume
    qtbot.mouseClick(histogram_parameters.cut_3d, QtCore.Qt.LeftButton)

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimensions.combo_step2.text() == "0.2"
    assert histogram_parameters.dimensions.combo_step3.text() == "0.02"
    assert histogram_parameters.dimensions.combo_step4.text() == ""
    assert histogram_parameters.dimensions.steps_valid_state() is True

    histogram_parameters.dimensions.combo_step1.clear()
    histogram_parameters.dimensions.combo_step2.clear()
    histogram_parameters.dimensions.combo_step3.clear()
    histogram_parameters.dimensions.combo_step4.clear()

    # set steps
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "0.5")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step2, "0.2")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step3, "0.02")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step4, "2")

    # set 2D volume
    qtbot.mouseClick(histogram_parameters.cut_2d, QtCore.Qt.LeftButton)

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimensions.combo_step2.text() == "0.2"
    assert histogram_parameters.dimensions.combo_step3.text() == ""
    assert histogram_parameters.dimensions.combo_step4.text() == ""
    assert histogram_parameters.dimensions.steps_valid_state() is True

    histogram_parameters.dimensions.combo_step1.clear()
    histogram_parameters.dimensions.combo_step2.clear()
    histogram_parameters.dimensions.combo_step3.clear()
    histogram_parameters.dimensions.combo_step4.clear()

    # set steps
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "0.5")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step2, "0.2")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step3, "0.02")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step4, "2")

    # set 1D volume
    qtbot.mouseClick(histogram_parameters.cut_1d, QtCore.Qt.LeftButton)

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimensions.combo_step2.text() == ""
    assert histogram_parameters.dimensions.combo_step3.text() == ""
    assert histogram_parameters.dimensions.combo_step4.text() == ""
    assert histogram_parameters.dimensions.steps_valid_state() is True


def test_dimensions_ste_values_required_color(qtbot):
    """Test for selecting the Dimension step size radio buttons and the step required field colors"""
    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    color_search = re.compile("background-color: (.*) ")

    # set 4D volume
    qtbot.mouseClick(histogram_parameters.cut_4d, QtCore.Qt.LeftButton)

    css_style_step1 = histogram_parameters.dimensions.combo_step1.styleSheet()
    css_style_step2 = histogram_parameters.dimensions.combo_step2.styleSheet()
    css_style_step3 = histogram_parameters.dimensions.combo_step3.styleSheet()
    css_style_step4 = histogram_parameters.dimensions.combo_step4.styleSheet()

    bg_color_step1 = color_search.search(css_style_step1).group(1)
    bg_color_step2 = color_search.search(css_style_step2).group(1)
    bg_color_step3 = color_search.search(css_style_step3).group(1)
    bg_color_step4 = color_search.search(css_style_step4).group(1)

    assert bg_color_step1 == "#ffaaaa"
    assert bg_color_step2 == "#ffaaaa"
    assert bg_color_step3 == "#ffaaaa"
    assert bg_color_step4 == "#ffaaaa"
    assert histogram_parameters.dimensions.steps_valid_state() is False


def test_dimensions_step_values_invalid(qtbot):
    """Test for setting invalid values in steps"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    # set 4D volume
    qtbot.mouseClick(histogram_parameters.cut_4d, QtCore.Qt.LeftButton)
    # set steps
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "a")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step2, "c")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step3, "c")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step4, "a")

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_step1.text() == ""
    assert histogram_parameters.dimensions.combo_step2.text() == ""
    assert histogram_parameters.dimensions.combo_step3.text() == ""
    assert histogram_parameters.dimensions.combo_step4.text() == ""


def test_dimensions_min_max_valid(qtbot):
    """Test for min max value pairs in dimensions"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    color_search = re.compile("background-color: (.*) ")

    # min1<max1
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min1, "1")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max1, "3")

    css_style_min1 = histogram_parameters.dimensions.combo_min1.styleSheet()
    css_style_max1 = histogram_parameters.dimensions.combo_max1.styleSheet()

    bg_color_min = color_search.search(css_style_min1).group(1)
    bg_color_max = color_search.search(css_style_max1).group(1)

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 0

    # min2<max2
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min2, "0")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max2, "4")

    css_style_min2 = histogram_parameters.dimensions.combo_min2.styleSheet()
    css_style_max2 = histogram_parameters.dimensions.combo_max2.styleSheet()

    bg_color_min = color_search.search(css_style_min2).group(1)
    bg_color_max = color_search.search(css_style_max2).group(1)

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 0

    # min3<max3
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min3, "10")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max3, "12")

    css_style_min3 = histogram_parameters.dimensions.combo_min3.styleSheet()
    css_style_max3 = histogram_parameters.dimensions.combo_max3.styleSheet()

    bg_color_min = color_search.search(css_style_min3).group(1)
    bg_color_max = color_search.search(css_style_max3).group(1)

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 0

    # min4<max4
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min4, "5")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max4, "7")

    css_style_min4 = histogram_parameters.dimensions.combo_min4.styleSheet()
    css_style_max4 = histogram_parameters.dimensions.combo_max4.styleSheet()

    bg_color_min = color_search.search(css_style_min4).group(1)
    bg_color_max = color_search.search(css_style_max4).group(1)

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 0


def test_dimensions_min_max_color_invalid(qtbot):
    """Test for min max value pairs in dimensions"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    color_search = re.compile("background-color: (.*) ")

    # min1>max1
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min1, "4")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max1, "3")

    css_style_min = histogram_parameters.dimensions.combo_min1.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max1.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 2

    # min2>max2
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min2, "7")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max2, "5")

    css_style_min = histogram_parameters.dimensions.combo_min2.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max2.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 4

    # min3>max3
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min3, "0")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max3, "-2")

    css_style_min = histogram_parameters.dimensions.combo_min2.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max2.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 6

    # min4>max4
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min4, "7")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max4, "3")

    css_style_min = histogram_parameters.dimensions.combo_min4.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max4.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 8


def test_dimensions_min_max_color_missing(qtbot):
    """Test for min max value pairs in dimensions"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    color_search = re.compile("background-color: (.*) ")

    # min1 is missing
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max1, "7")
    css_style_min = histogram_parameters.dimensions.combo_min1.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max1.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 2

    # min2 is missing
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max2, "2")
    css_style_min = histogram_parameters.dimensions.combo_min2.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max2.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 4

    # max3 is missing
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min3, "2")
    css_style_min = histogram_parameters.dimensions.combo_min3.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max3.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 6

    # max4 is missing
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min4, "2")
    css_style_min = histogram_parameters.dimensions.combo_min4.styleSheet()
    css_style_max = histogram_parameters.dimensions.combo_max4.styleSheet()

    bg_color_min = color_search.search(css_style_min).group(1)
    bg_color_max = color_search.search(css_style_max).group(1)

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    assert len(histogram_parameters.dimensions.min_max_invalid_states) == 8


def test_dimensions_dropdown_uniqueness(qtbot):
    """Test for dimensions dropdown selection values are unique among them"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    # ["[H,0,0]", "[0,K,0]", "[0,0,L]", "DeltaE"]
    combo_dimensions = histogram_parameters.dimensions.combo_dimensions

    # start
    # assign 3 = [4]
    qtbot.keyClicks(histogram_parameters.dimensions.combo_dim3, combo_dimensions[3])

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_dim1.currentText() != combo_dimensions[3]
    assert histogram_parameters.dimensions.combo_dim2.currentText() != combo_dimensions[3]
    assert histogram_parameters.dimensions.combo_dim3.currentText() == combo_dimensions[3]
    assert histogram_parameters.dimensions.combo_dim4.currentText() != combo_dimensions[3]

    # assign 1 = [2]
    qtbot.keyClicks(histogram_parameters.dimensions.combo_dim1, combo_dimensions[2])

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_dim1.currentText() == combo_dimensions[2]
    assert histogram_parameters.dimensions.combo_dim2.currentText() != combo_dimensions[2]
    assert histogram_parameters.dimensions.combo_dim3.currentText() != combo_dimensions[2]
    assert histogram_parameters.dimensions.combo_dim4.currentText() != combo_dimensions[2]

    # assign 4 = [1]
    qtbot.keyClicks(histogram_parameters.dimensions.combo_dim4, combo_dimensions[1])

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_dim1.currentText() != combo_dimensions[1]
    assert histogram_parameters.dimensions.combo_dim2.currentText() != combo_dimensions[1]
    assert histogram_parameters.dimensions.combo_dim3.currentText() != combo_dimensions[1]
    assert histogram_parameters.dimensions.combo_dim4.currentText() == combo_dimensions[1]

    # assign 2 = [0]
    qtbot.keyClicks(histogram_parameters.dimensions.combo_dim2, combo_dimensions[0])

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_dim1.currentText() != combo_dimensions[0]
    assert histogram_parameters.dimensions.combo_dim2.currentText() == combo_dimensions[0]
    assert histogram_parameters.dimensions.combo_dim3.currentText() != combo_dimensions[0]
    assert histogram_parameters.dimensions.combo_dim4.currentText() != combo_dimensions[0]


def test_dimensions_update_on_projection_edit(qtbot):
    """Test for dimensions dropdown selection values are unique among them
    test case are created based on example scenarios atMantidWorkBench -> Interfaces -> Direct -> DGSPlanner"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()

    # test 1
    qtbot.keyClicks(histogram_parameters.projection_u, "13,1,0")
    qtbot.keyClicks(histogram_parameters.projection_v, "1,8,0")
    qtbot.keyClicks(histogram_parameters.projection_w, "1,1,6")

    # dimensions 1-3
    assert histogram_parameters.dimensions.combo_dim1.currentText() == "[13.0H,H,0]"
    assert histogram_parameters.dimensions.combo_dim2.currentText() == "[K,8.0K,0]"
    assert histogram_parameters.dimensions.combo_dim3.currentText() == "[L,L,6.0L]"

    # test 2
    # assign 4 = [0]
    qtbot.keyClicks(histogram_parameters.dimensions.combo_dim4, "[13.0H,H,0]")

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_dim1.currentText() == "DeltaE"
    assert histogram_parameters.dimensions.combo_dim2.currentText() == "[K,8.0K,0]"
    assert histogram_parameters.dimensions.combo_dim3.currentText() == "[L,L,6.0L]"
    assert histogram_parameters.dimensions.combo_dim4.currentText() == "[13.0H,H,0]"

    # test 3 : projection update triggers dimension combo selected items updates
    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()

    qtbot.keyClicks(histogram_parameters.projection_u, "6,6,6")
    qtbot.keyClicks(histogram_parameters.projection_v, "2,1,3")
    qtbot.keyClicks(histogram_parameters.projection_w, "0,0,1")

    # dimensions 1-4
    assert histogram_parameters.dimensions.combo_dim1.currentText() == "[6.0H,6.0H,6.0H]"
    assert histogram_parameters.dimensions.combo_dim2.currentText() == "[2.0L,L,3.0L]"
    assert histogram_parameters.dimensions.combo_dim3.currentText() == "[0,0,L]"
    assert histogram_parameters.dimensions.combo_dim4.currentText() == "DeltaE"
