"""UI tests for Reduction Parameters widget: input values"""
import re
from functools import partial
from qtpy import QtCore


from shiver.views.advanced_options import AdvancedDialog
from shiver.views.reduction_parameters import ReductionParameters


def test_advanced_options_valid_input(qtbot):
    """Test for adding all valid inputs in advanced dialog"""
    dialog = AdvancedDialog()
    dialog.show()

    # fill the table
    # 1row
    dialog.table_view.setCurrentCell(0, 0)
    dialog.table_view.item(0, 0).setText("1,5,9")
    dialog.table_view.setCurrentCell(0, 1)
    dialog.table_view.item(0, 1).setText("4,5,7")
    dialog.table_view.setCurrentCell(0, 2)
    dialog.table_view.item(0, 2).setText("8-67")

    # 2row
    dialog.table_view.setCurrentCell(1, 0)
    dialog.table_view.item(1, 0).setText("9:30:2")
    dialog.table_view.setCurrentCell(1, 1)
    dialog.table_view.item(1, 1).setText("4:5,7")
    dialog.table_view.setCurrentCell(1, 2)
    dialog.table_view.item(1, 2).setText("32:48:2, 1 ,14")

    # 3row
    dialog.table_view.setCurrentCell(2, 0)
    dialog.table_view.item(2, 0).setText("1,5,55,100-199")
    dialog.table_view.setCurrentCell(2, 1)
    dialog.table_view.item(2, 1).setText("7")
    dialog.table_view.setCurrentCell(2, 2)
    dialog.table_view.item(2, 2).setText("120,126,127")

    dialog.table_view.setCurrentCell(1, 0)

    qtbot.keyClicks(dialog.emin_input, "4.8")
    qtbot.keyClicks(dialog.emax_input, "11.7")
    qtbot.keyClicks(dialog.gonio_input, "goniometer1")
    qtbot.keyClicks(dialog.adt_dim_input, "xx,23,45")

    css_style_emin = dialog.emin_input.styleSheet()

    css_style_emax = dialog.emax_input.styleSheet()

    css_style_gonio = dialog.gonio_input.styleSheet()

    css_style_dim = dialog.adt_dim_input.styleSheet()

    assert css_style_emin == ""
    assert css_style_emax == ""
    # no css style was applied
    assert css_style_gonio == ""
    assert css_style_dim == ""

    # assert no error
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True

    dict_data = dialog.get_advanced_options_dict()
    # assert values are added in the dictionary
    table_data = [
        {"Bank": "1,5,9", "Tube": "4,5,7", "Pixel": "8-67"},
        {"Bank": "9:30:2", "Tube": "4:5,7", "Pixel": "32:48:2,1,14"},
        {"Bank": "1,5,55,100-199", "Tube": "7", "Pixel": "120,126,127"},
    ]
    for row in range(3):
        assert dict_data["MaskInputs"][row]["Bank"] == table_data[row]["Bank"]
        assert dict_data["MaskInputs"][row]["Tube"] == table_data[row]["Tube"]
        assert dict_data["MaskInputs"][row]["Pixel"] == table_data[row]["Pixel"]

    assert dict_data["E_min"] == "4.8"
    assert dict_data["E_max"] == "11.7"
    assert dict_data["ApplyFilterBadPulses"] is False
    assert dict_data["BadPulsesThreshold"] == "95"
    assert dict_data["TimeIndepBackgroundWindow"] == "Default"
    assert dict_data["Goniometer"] == "goniometer1"
    assert dict_data["AdditionalDimensions"] == "xx,23,45"

    qtbot.wait(500)
    dialog.close()


def test_advanced_options_apply_filter_valid_inputs(qtbot):
    """Test for adding valid filter inputs in advanced dialog"""
    dialog = AdvancedDialog()
    dialog.show()

    # default case
    assert dialog.filter_check.isChecked() is False
    assert dialog.lcutoff_label.isVisible() is False
    assert dialog.lcutoff_input.isVisible() is False
    # check filter
    qtbot.mouseClick(dialog.filter_check, QtCore.Qt.LeftButton)
    assert dialog.filter_check.isChecked() is True

    assert dialog.lcutoff_label.isVisible() is True
    assert dialog.lcutoff_input.isVisible() is True
    assert dialog.lcutoff_input.text() == "95"

    # change cutoff value
    dialog.lcutoff_input.clear()
    qtbot.keyClicks(dialog.lcutoff_input, "65")
    dict_data = dialog.get_advanced_options_dict()
    assert dict_data["ApplyFilterBadPulses"] is True
    assert dict_data["BadPulsesThreshold"] == "65"

    # empty cutoff value
    dialog.lcutoff_input.clear()
    dict_data = dialog.get_advanced_options_dict()
    assert dict_data["ApplyFilterBadPulses"] is True
    assert dict_data["BadPulsesThreshold"] is None

    # uncheck filter
    qtbot.mouseClick(dialog.filter_check, QtCore.Qt.LeftButton)
    assert dialog.filter_check.isChecked() is False
    assert dialog.lcutoff_label.isVisible() is False
    assert dialog.lcutoff_input.isVisible() is False

    dialog.close()


def test_advanced_options_apply_tib_valid_input(qtbot):
    """Test for adding valid tib inputs in advanced dialog"""
    dialog = AdvancedDialog()
    dialog.show()

    color_search = re.compile("border-color: (.*);")

    # default case
    assert dialog.tib_default.isChecked() is True
    assert dialog.tib_min_label.isVisible() is False
    assert dialog.tib_min_input.isVisible() is False
    assert dialog.tib_max_label.isVisible() is False
    assert dialog.tib_max_input.isVisible() is False
    dict_data = dialog.get_advanced_options_dict()
    assert dict_data["TimeIndepBackgroundWindow"] == "Default"

    # check yes
    qtbot.mouseClick(dialog.tib_yes, QtCore.Qt.LeftButton)
    assert dialog.tib_yes.isChecked() is True
    assert dialog.tib_min_label.isVisible() is True
    assert dialog.tib_min_input.isVisible() is True
    assert dialog.tib_max_label.isVisible() is True
    assert dialog.tib_max_input.isVisible() is True

    # add min value
    qtbot.keyClicks(dialog.tib_min_input, "9")

    # max value expected
    css_style_tib_max = dialog.tib_max_input.styleSheet()
    bg_color_tib_max = color_search.search(css_style_tib_max).group(1)
    assert bg_color_tib_max == "red"
    assert dialog.btn_apply.isEnabled() is False

    # add max value
    qtbot.keyClicks(dialog.tib_max_input, "18")
    assert len(dialog.invalid_fields) == 0
    dict_data = dialog.get_advanced_options_dict()
    assert dict_data["TimeIndepBackgroundWindow"] == "9, 18"

    # check no
    dialog.tib_no.setChecked(True)

    assert dialog.tib_min_label.isVisible() is False
    assert dialog.tib_min_input.isVisible() is False
    assert dialog.tib_max_label.isVisible() is False
    assert dialog.tib_max_input.isVisible() is False
    dict_data = dialog.get_advanced_options_dict()
    assert dict_data["TimeIndepBackgroundWindow"] is None

    # assert no error
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True
    dialog.close()


def test_mask_table_add_row(qtbot):
    """Test for adding a row in the table"""
    dialog = AdvancedDialog()
    dialog.show()

    assert dialog.table_view.rowCount() == 3
    qtbot.mouseClick(dialog.add_btn, QtCore.Qt.LeftButton)
    assert dialog.table_view.rowCount() == 4
    dialog.close()


def test_mask_table_delete_selected_row(qtbot):
    """Test for deleting a row in the table"""
    dialog = AdvancedDialog()
    dialog.show()

    dialog.table_view.selectRow(1)
    assert dialog.table_view.rowCount() == 3
    qtbot.mouseClick(dialog.delete_btn, QtCore.Qt.LeftButton)
    assert dialog.table_view.rowCount() == 2
    dialog.close()


def test_mask_table_delete_unselected_row_invalid(qtbot):
    """Test for deleting a row in the table"""
    dialog = AdvancedDialog()
    dialog.show()

    assert dialog.table_view.rowCount() == 3
    completed = False

    # This is to handle modal dialogs
    def handle_dialog():
        nonlocal completed
        dialog.error.done(1)
        completed = True

    def dialog_completed():
        nonlocal completed
        assert completed is True

    QtCore.QTimer.singleShot(500, partial(handle_dialog))
    qtbot.mouseClick(dialog.delete_btn, QtCore.Qt.LeftButton)
    qtbot.waitUntil(dialog_completed, timeout=5000)
    assert dialog.table_view.rowCount() == 3
    dialog.close()


def test_help_button(qtbot):
    """Test for pushing the help button"""

    dialog = AdvancedDialog()
    dialog.show()

    # push the Help button
    qtbot.mouseClick(dialog.btn_help, QtCore.Qt.LeftButton)

    dialog.close()


def test_mask_table_invalid(qtbot):
    """Test for invalid inputs in table"""
    dialog = AdvancedDialog()
    dialog.show()

    color_search = re.compile("border-color: (.*);")

    # invalid
    dialog.table_view.setCurrentCell(0, 0)
    dialog.table_view.item(0, 0).setText(",,,")
    dialog.table_view.setCurrentCell(1, 0)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # <min
    dialog.table_view.item(1, 0).setText("-1")
    dialog.table_view.setCurrentCell(2, 0)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # >max
    dialog.table_view.item(2, 0).setText("201")
    dialog.table_view.setCurrentCell(0, 1)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # invalid
    dialog.table_view.item(0, 1).setText("7--9")
    dialog.table_view.setCurrentCell(1, 1)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # <min
    dialog.table_view.item(1, 1).setText("-1")
    dialog.table_view.setCurrentCell(2, 1)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # >max
    dialog.table_view.item(2, 1).setText("9")
    dialog.table_view.setCurrentCell(0, 2)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # invalid
    dialog.table_view.item(0, 2).setText(":::-")
    dialog.table_view.setCurrentCell(1, 2)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # <min
    dialog.table_view.item(1, 2).setText("-1")
    dialog.table_view.setCurrentCell(2, 2)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    # >max
    dialog.table_view.item(2, 2).setText("129")
    dialog.table_view.setCurrentCell(2, 2)
    css_style_table = dialog.table_view.styleSheet()
    table_color = color_search.search(css_style_table).group(1)
    assert table_color == "red"

    qtbot.wait(400)
    # assert error
    assert len(dialog.invalid_fields) == 9
    assert dialog.btn_apply.isEnabled() is False


def test_tib_invalid(qtbot):
    """Test for invalid inputs in tib"""

    dialog = AdvancedDialog()
    dialog.show()

    color_search = re.compile("border-color: (.*);")

    # check yes
    qtbot.mouseClick(dialog.tib_yes, QtCore.Qt.LeftButton)

    assert dialog.tib_yes.isChecked() is True
    assert dialog.tib_min_label.isVisible() is True
    assert dialog.tib_min_input.isVisible() is True
    assert dialog.tib_max_label.isVisible() is True
    assert dialog.tib_max_input.isVisible() is True

    qtbot.keyClicks(dialog.tib_min_input, "19")
    qtbot.keyClicks(dialog.tib_max_input, "8")

    css_style_tib_min = dialog.tib_min_input.styleSheet()
    bg_color_tib_min = color_search.search(css_style_tib_min).group(1)
    assert bg_color_tib_min == "red"

    css_style_tib_max = dialog.tib_max_input.styleSheet()
    bg_color_tib_max = color_search.search(css_style_tib_max).group(1)
    assert bg_color_tib_max == "red"

    # assert error
    assert len(dialog.invalid_fields) == 2
    assert dialog.btn_apply.isEnabled() is False


def test_adt_invalid(qtbot):
    """Test for additional dimensions inputs in tib"""
    dialog = AdvancedDialog()
    dialog.show()
    color_search = re.compile("border-color: (.*);")

    # x: inprogress
    qtbot.keyClicks(dialog.adt_dim_input, "x")
    css_style_dim = dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)
    assert bg_color_dim == "red"

    # x1: inprogress
    qtbot.keyClicks(dialog.adt_dim_input, "1")
    css_style_dim = dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)
    assert bg_color_dim == "red"

    # x1,: inprogress
    qtbot.keyClicks(dialog.adt_dim_input, ",")
    css_style_dim = dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)
    assert bg_color_dim == "red"

    # x1,a: inprogress/invalid
    qtbot.keyClicks(dialog.adt_dim_input, "a")
    css_style_dim = dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)
    assert bg_color_dim == "red"

    # x1,5,4: inprogress/invalid
    qtbot.keyClicks(dialog.adt_dim_input, "5,4")
    css_style_dim = dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)
    assert bg_color_dim == "red"

    # assert error
    assert len(dialog.invalid_fields) == 1
    assert dialog.btn_apply.isEnabled() is False
    dialog.close()


def test_apply_btn_valid(qtbot):
    """Test for clicking apply and storing the data as a dictionary in parent"""
    red_parameters = ReductionParameters()
    dialog = AdvancedDialog(red_parameters)
    dialog.show()

    # fill the table
    # 1row
    # dialog.table_view.setCurrentCell(0, 0)
    dialog.table_view.item(0, 0).setText("1,5,9")
    # dialog.table_view.setCurrentCell(0, 1)
    dialog.table_view.item(0, 1).setText("4,5,7")
    # dialog.table_view.setCurrentCell(0, 2)
    dialog.table_view.item(0, 2).setText("8-67")

    # 2row
    # dialog.table_view.setCurrentCell(1, 0)
    dialog.table_view.item(1, 0).setText("9:30:2")
    # dialog.table_view.setCurrentCell(1, 1)
    dialog.table_view.item(1, 1).setText("4:5,7")
    # dialog.table_view.setCurrentCell(1, 2)
    dialog.table_view.item(1, 2).setText("32:48:2, 1 ,14")

    # 3row
    # dialog.table_view.setCurrentCell(2, 0)
    dialog.table_view.item(2, 0).setText("1,5,55,100-199")
    # dialog.table_view.setCurrentCell(2, 1)
    dialog.table_view.item(2, 1).setText("7")
    # dialog.table_view.setCurrentCell(2, 2)
    dialog.table_view.item(2, 2).setText("120,126,127")

    # dialog.table_view.setCurrentCell(1, 0)

    qtbot.keyClicks(dialog.emin_input, "4.8")
    qtbot.keyClicks(dialog.emax_input, "11.7")
    qtbot.keyClicks(dialog.gonio_input, "goniometer1")
    qtbot.keyClicks(dialog.adt_dim_input, "xx,23,45,z,1,3")

    # assert no error
    assert len(dialog.invalid_fields) == 0
    assert dialog.btn_apply.isEnabled() is True

    # click apply
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    dict_data = dialog.parent.dict_advanced

    # assert values are added in parent dictionary

    table_data = [
        {"Bank": "1,5,9", "Tube": "4,5,7", "Pixel": "8-67"},
        {"Bank": "9:30:2", "Tube": "4:5,7", "Pixel": "32:48:2,1,14"},
        {"Bank": "1,5,55,100-199", "Tube": "7", "Pixel": "120,126,127"},
    ]
    for row in range(3):
        assert dict_data["MaskInputs"][row]["Bank"] == table_data[row]["Bank"]
        assert dict_data["MaskInputs"][row]["Tube"] == table_data[row]["Tube"]
        assert dict_data["MaskInputs"][row]["Pixel"] == table_data[row]["Pixel"]

    assert dict_data["E_min"] == "4.8"
    assert dict_data["E_max"] == "11.7"
    assert dict_data["ApplyFilterBadPulses"] is False
    assert dict_data["BadPulsesThreshold"] == "95"
    assert dict_data["TimeIndepBackgroundWindow"] == "Default"
    assert dict_data["Goniometer"] == "goniometer1"
    assert dict_data["AdditionalDimensions"] == "xx,23,45,z,1,3"

    dialog.close()


def test_advanced_options_initialization_from_dict_rows():
    """Test for initializing all parameters from dict"""

    red_parameters = ReductionParameters()
    dialog = AdvancedDialog(red_parameters)
    dialog.show()

    # an additional row
    table_data = [
        {"Bank": "", "Tube": "4,5,7", "Pixel": "8-67"},
        {"Bank": "9:30:2", "Tube": "", "Pixel": "32:48:2,1,14"},
        {"Bank": "1,5,55", "Tube": "7", "Pixel": "120,126,127"},
        {"Bank": "2", "Tube": "2", "Pixel": ""},
        {"Bank": "100-199", "Tube": "2", "Pixel": "12"},
    ]

    params = {
        "MaskInputs": table_data,
        "E_min": "4.8",
        "E_max": "11.7",
        "ApplyFilterBadPulses": True,
        "BadPulsesThreshold": "80",
        "TimeIndepBackgroundWindow": ["1", "8"],
        "Goniometer": "goniom",
        "AdditionalDimensions": "xx,23,45,z,1,3",
    }

    dialog.populate_advanced_options_from_dict(params)

    # assert fields are populated properly
    for row in range(len(table_data)):
        assert dialog.table_view.item(row, 0).text() == params["MaskInputs"][row]["Bank"]
        assert dialog.table_view.item(row, 1).text() == params["MaskInputs"][row]["Tube"]
        assert dialog.table_view.item(row, 2).text() == params["MaskInputs"][row]["Pixel"]

    assert dialog.emin_input.text() == params["E_min"]
    assert dialog.emax_input.text() == params["E_max"]
    assert dialog.filter_check.isChecked() is params["ApplyFilterBadPulses"]
    assert dialog.lcutoff_input.text() == params["BadPulsesThreshold"]
    assert dialog.tib_min_input.text() == params["TimeIndepBackgroundWindow"][0]
    assert dialog.tib_max_input.text() == params["TimeIndepBackgroundWindow"][1]

    assert dialog.gonio_input.text() == params["Goniometer"]
    assert dialog.adt_dim_input.text() == params["AdditionalDimensions"]

    # assert no error
    assert len(dialog.invalid_fields) == 0

    dialog.close()


def test_advanced_options_initialization_from_dict_e_default():
    """Test for initializing all parameters from dict"""

    red_parameters = ReductionParameters()
    dialog = AdvancedDialog(red_parameters)
    dialog.show()

    # an additional row
    table_data = [{"Bank": "1,5,9", "Tube": "4,5,7", "Pixel": "8-67"}, {"Bank": "2", "Tube": "2", "Pixel": "12"}]

    params = {
        "MaskInputs": table_data,
        "E_min": "",
        "E_max": "",
        "ApplyFilterBadPulses": False,
        "BadPulsesThreshold": "80",
        "TimeIndepBackgroundWindow": "Default",
        "Goniometer": "g1",
        "AdditionalDimensions": "xx,23,45",
    }
    dialog.populate_advanced_options_from_dict(params)

    # assert fields are populated properly
    for row in range(len(table_data)):
        assert dialog.table_view.item(row, 0).text() == params["MaskInputs"][row]["Bank"]
        assert dialog.table_view.item(row, 1).text() == params["MaskInputs"][row]["Tube"]
        assert dialog.table_view.item(row, 2).text() == params["MaskInputs"][row]["Pixel"]

    assert dialog.emin_input.text() == params["E_min"]
    assert dialog.emax_input.text() == params["E_max"]
    assert dialog.filter_check.isChecked() is params["ApplyFilterBadPulses"]
    assert dialog.lcutoff_input.text() == params["BadPulsesThreshold"]
    assert dialog.tib_min_input.text() == ""
    assert dialog.tib_max_input.text() == ""

    assert dialog.gonio_input.text() == params["Goniometer"]
    assert dialog.adt_dim_input.text() == params["AdditionalDimensions"]

    # assert no error
    assert len(dialog.invalid_fields) == 0

    dialog.close()


def test_advanced_options_initialization_from_dict_none_default():
    """Test for initializing all parameters from dict"""

    red_parameters = ReductionParameters()
    dialog = AdvancedDialog(red_parameters)
    dialog.show()

    table_data = [{"Bank": "1,5,9", "Tube": "4,5,7", "Pixel": "8-67"}, {"Bank": "2", "Tube": "2", "Pixel": "12"}]

    params = {
        "MaskInputs": table_data,
        "E_min": "",
        "E_max": "",
        "ApplyFilterBadPulses": False,
        "BadPulsesThreshold": "",
        "TimeIndepBackgroundWindow": None,
        "Goniometer": "g1",
        "AdditionalDimensions": "xx,23,45",
    }
    dialog.populate_advanced_options_from_dict(params)

    # assert fields are populated properly
    for row in range(len(table_data)):
        assert dialog.table_view.item(row, 0).text() == params["MaskInputs"][row]["Bank"]
        assert dialog.table_view.item(row, 1).text() == params["MaskInputs"][row]["Tube"]
        assert dialog.table_view.item(row, 2).text() == params["MaskInputs"][row]["Pixel"]

    assert dialog.emin_input.text() == params["E_min"]
    assert dialog.emax_input.text() == params["E_max"]
    assert dialog.filter_check.isChecked() is params["ApplyFilterBadPulses"]
    assert dialog.lcutoff_input.text() == params["BadPulsesThreshold"]
    assert dialog.tib_min_input.text() == ""
    assert dialog.tib_max_input.text() == ""

    assert dialog.gonio_input.text() == params["Goniometer"]
    assert dialog.adt_dim_input.text() == params["AdditionalDimensions"]

    # assert no error
    assert len(dialog.invalid_fields) == 0

    dialog.close()


def test_advanced_options_initialization_from_dict_invalid():
    """Test for initializing parameters from invalid dict"""

    red_parameters = ReductionParameters()
    dialog = AdvancedDialog(red_parameters)
    dialog.show()

    # an additional row
    table_data = [{"Bank": "1,5,9", "Tube": "4,5,7", "Pixel": "8-67"}, {"Bank": "2", "Tube": "2", "Pixel": "12"}]

    params = {
        "MaskInputs": table_data,
        "A": "",
        "E_max": "",
    }

    # This is to handle modal dialog expected error
    def handle_dialog():
        dialog.error.done(1)

    QtCore.QTimer.singleShot(500, partial(handle_dialog))
    dialog.populate_advanced_options_from_dict(params)

    dialog.close()
