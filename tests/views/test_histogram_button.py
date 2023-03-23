"""UI tests for HistogramParameter button"""
from qtpy import QtCore

# QGroupBox
from shiver.views.histogram import HistogramParameter


def test_dictionary_creation_histogram_btn(qtbot):
    """Test for pressing the Histogram button and accessing all the parameters from the dictionary"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()

    # ["[H,0,0]", "[0,K,0]", "[0,0,L]", "DeltaE"]

    qtbot.mouseClick(histogram_parameters.cut_4d, QtCore.Qt.LeftButton)
    # set parameters, leave the default ones
    # name
    histogram_parameters.name.clear()
    qtbot.keyClicks(histogram_parameters.name, "Plot 1")

    # projections
    histogram_parameters.projection_u.clear()
    histogram_parameters.projection_v.clear()
    histogram_parameters.projection_w.clear()
    qtbot.keyClicks(histogram_parameters.projection_u, "1,0,0")
    qtbot.keyClicks(histogram_parameters.projection_v, "0,1,0")
    qtbot.keyClicks(histogram_parameters.projection_w, "0,0,1")

    # dimensions
    # leave default values
    qtbot.keyClicks(histogram_parameters.dimensions.combo_min1, "1")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max1, "3")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step1, "0.5")

    qtbot.keyClicks(histogram_parameters.dimensions.combo_min2, "2")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max2, "4")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step2, "0.2")

    qtbot.keyClicks(histogram_parameters.dimensions.combo_min3, "0")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max3, "1")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step3, "0.02")

    qtbot.keyClicks(histogram_parameters.dimensions.combo_min4, "1")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_max4, "5")
    qtbot.keyClicks(histogram_parameters.dimensions.combo_step4, "2")

    # symmetry,smoothing
    qtbot.keyClicks(histogram_parameters.symmetry_operations, "x,y,z")
    histogram_parameters.smoothing.clear()
    qtbot.keyClicks(histogram_parameters.smoothing, "3.45")

    params = {}

    def handle_button(params_dict):
        params.update(params_dict)

    histogram_parameters.connect_histogram_submit(handle_button)

    qtbot.mouseClick(histogram_parameters.histogram_btn, QtCore.Qt.LeftButton)

    # name
    assert params["Name"] == "Plot 1"

    # projections
    assert params["ProjectionU"] == "1,0,0"
    assert params["ProjectionV"] == "0,1,0"
    assert params["ProjectionW"] == "0,0,1"

    # dimensions 1-4
    assert params["Dimension1"] == "[H,0,0]"
    assert params["Dimension1Min"] == "1"
    assert params["Dimension1Max"] == "3"
    assert params["Dimension1Step"] == "0.5"
    assert params["Dimension2"] == "[0,K,0]"
    assert params["Dimension2Min"] == "2"
    assert params["Dimension2Max"] == "4"
    assert params["Dimension2Step"] == "0.2"
    assert params["Dimension3"] == "[0,0,L]"
    assert params["Dimension3Min"] == "0"
    assert params["Dimension3Max"] == "1"
    assert params["Dimension3Step"] == "0.02"
    assert params["Dimension4"] == "DeltaE"
    assert params["Dimension4Min"] == "1"
    assert params["Dimension4Max"] == "5"
    assert params["Dimension4Step"] == "2"

    assert params["Symmetry"] == "x,y,z"
    assert params["Smoothing"] == "3.45"
