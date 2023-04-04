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

    params = histogram_parameters.gather_histogram_parameters()

    ref_params = {
        "Name": "Plot 1",
        "QDimension0": "1,0,0",
        "QDimension1": "0,1,0",
        "QDimension2": "0,0,1",
        "Dimension0Name": "QDimension0",
        "Dimension0Binning": "1,0.5,3",
        "Dimension1Name": "QDimension1",
        "Dimension1Binning": "2,0.2,4",
        "Dimension2Name": "QDimension2",
        "Dimension2Binning": "0,0.02,1",
        "Dimension3Name": "DeltaE",
        "Dimension3Binning": "1,2,5",
        "SymmetryOperations": "x,y,z",
        "Smoothing": "3.45",
    }

    assert params == ref_params
