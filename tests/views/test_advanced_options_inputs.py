"""UI tests for Reduction Parameters widget: input values"""
import os, re
from functools import partial
from qtpy import QtCore, QtWidgets, QtGui

from shiver.views.generate import Generate
from shiver.views.advanced_options import AdvancedDialog
from shiver.views.reduction_parameters import ReductionParameters

def test_advanced_options_valid_input(qtbot):
    """Test for adding all valid inputs in advanced dialog"""
    dialog = AdvancedDialog()
    dialog.show()
    
    color_search = re.compile("QLineEdit { background-color: (.*) }")
    
    #fill the table
    #1row
    dialog.table_view.setCurrentCell(0,0)
    dialog.table_view.item(0, 0).setText("1,5,9")
    dialog.table_view.setCurrentCell(0,1)
    dialog.table_view.item(0, 1).setText("4,5,7")
    dialog.table_view.setCurrentCell(0,2)
    dialog.table_view.item(0, 2).setText("8-67")    

    #2row
    dialog.table_view.setCurrentCell(1,0)
    dialog.table_view.item(1, 0).setText("9:30:2")
    dialog.table_view.setCurrentCell(1,1)
    dialog.table_view.item(1, 1).setText("4:5,7")
    dialog.table_view.setCurrentCell(1,2)
    dialog.table_view.item(1, 2).setText("32:48:2, 1 ,14")

    #3row
    dialog.table_view.setCurrentCell(2,0)
    dialog.table_view.item(2, 0).setText("1,5,55,100-199")
    dialog.table_view.setCurrentCell(2,1)
    dialog.table_view.item(2, 1).setText("7")
    dialog.table_view.setCurrentCell(2,2)
    dialog.table_view.item(2, 2).setText("120,126,127")
    
    dialog.table_view.setCurrentCell(1,0)     
    
    qtbot.keyClicks(dialog.emin_input, "4.8")
    qtbot.keyClicks(dialog.emax_input, "11.7")            
    qtbot.keyClicks(dialog.gonio_input, "goniometer1")
    qtbot.keyClicks(dialog.adt_dim_input, "xx,23,45")
    
    # check background color
    for row in range(3):
        for column in range(3):
            bg_color_cell = dialog.table_view.item(row, column).background().color()
            assert bg_color_cell == QtGui.QColor("#ffffff")
    
    css_style_emin = dialog.emin_input.styleSheet()
    bg_color_emin = color_search.search(css_style_emin).group(1)

    css_style_emax = dialog.emax_input.styleSheet()
    bg_color_emax = color_search.search(css_style_emax).group(1)
    
    css_style_gonio = dialog.gonio_input.styleSheet()
    
    css_style_dim= dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)                

    assert bg_color_emin == '#ffffff'
    assert bg_color_emax == '#ffffff'    
    #no css style was applied
    assert css_style_gonio is ""
    assert bg_color_dim == '#ffffff'        
    
    #assert no error
    assert len(dialog.invalid_fields) == 0
    
    dict_data = dialog.get_advanced_options_dict()
    #assert values are added in the dictionary
    table_data = [
        {'Bank': '1,5,9', 'Tube': '4,5,7', 'Pixel': '8-67'}, 
        {'Bank': '9:30:2', 'Tube': '4:5,7', 'Pixel': '32:48:2,1,14'}, 
        {'Bank': '1,5,55,100-199', 'Tube': '7', 'Pixel': '120,126,127'}
    ]
    for row in range(3):
        assert dict_data["MaskInputs"][row]["Bank"] == table_data[row]["Bank"]
        assert dict_data["MaskInputs"][row]["Tube"] == table_data[row]["Tube"]
        assert dict_data["MaskInputs"][row]["Pixel"] == table_data[row]["Pixel"]        
            
    assert dict_data["E_min"] == '4.8'
    assert dict_data["E_max"] == '11.7'
    assert dict_data["ApplyFilterBadPulses"] == False
    assert dict_data["BadPulsesThreshold"] == '95'
    assert dict_data["TimeIndepBackgroundWindow"] == 'Default'
    assert dict_data["Goniometer"] == 'goniometer1'
    assert dict_data["AdditionalDimensions"] == 'xx,23,45'
    
    qtbot.wait(500)        
    dialog.close()


def test_advanced_options_apply_filter_valid_inputs(qtbot):
    """Test for adding valid filter inputs in advanced dialog"""
    dialog = AdvancedDialog()
    dialog.show()
    
    #default case
    assert dialog.filter_check.isChecked() is False    
    assert dialog.lcutoff_label.isVisible() is False
    assert dialog.lcutoff_input.isVisible() is False 
    #check filter   
    qtbot.mouseClick(dialog.filter_check, QtCore.Qt.LeftButton)
    assert dialog.filter_check.isChecked() is True     
    
    assert dialog.lcutoff_label.isVisible() is True
    assert dialog.lcutoff_input.isVisible() is True 
    assert dialog.lcutoff_input.text() == '95'    

    #change cutoff value
    dialog.lcutoff_input.clear()    
    qtbot.keyClicks(dialog.lcutoff_input, "65")
    dict_data = dialog.get_advanced_options_dict()        
    assert dict_data["ApplyFilterBadPulses"] == True        
    assert dict_data["BadPulsesThreshold"] == '65'    

    #empty cutoff value
    dialog.lcutoff_input.clear()    
    dict_data = dialog.get_advanced_options_dict()        
    assert dict_data["ApplyFilterBadPulses"] == True        
    assert dict_data["BadPulsesThreshold"] == '' 

    #uncheck filter
    qtbot.mouseClick(dialog.filter_check, QtCore.Qt.LeftButton)
    assert dialog.filter_check.isChecked() is False     
    assert dialog.lcutoff_label.isVisible() is False
    assert dialog.lcutoff_input.isVisible() is False 
    
    dialog.close()

def test_advanced_options_apply_tib_valid_input(qtbot):
    """Test for adding valid tib inputs in advanced dialog"""
    dialog = AdvancedDialog()
    dialog.show()
    
    color_search = re.compile("QLineEdit { background-color: (.*) }")
    
    #default case
    assert dialog.tib_default.isChecked() is True
    assert dialog.tib_min_label.isVisible() is False
    assert dialog.tib_min_input.isVisible() is False 
    assert dialog.tib_max_label.isVisible() is False
    assert dialog.tib_max_input.isVisible() is False     
    dict_data = dialog.get_advanced_options_dict()        
    assert dict_data["TimeIndepBackgroundWindow"] == 'Default'
    
    #check yes    
    qtbot.mouseClick(dialog.tib_yes, QtCore.Qt.LeftButton)
    assert dialog.tib_yes.isChecked() is True     
    assert dialog.tib_min_label.isVisible() is True
    assert dialog.tib_min_input.isVisible() is True 
    assert dialog.tib_max_label.isVisible() is True
    assert dialog.tib_max_input.isVisible() is True
       
    #add min value
    qtbot.keyClicks(dialog.tib_min_input, "9")
    
    #max value expected
    css_style_tib_max = dialog.tib_max_input.styleSheet()
    bg_color_tib_max = color_search.search(css_style_tib_max).group(1)  
    assert bg_color_tib_max == '#ff0000'
    
    #add max value
    qtbot.keyClicks(dialog.tib_max_input, "18")
    css_style_tib_max = dialog.tib_max_input.styleSheet()
    bg_color_tib_max = color_search.search(css_style_tib_max).group(1)  
    assert bg_color_tib_max == '#ffffff'
    
    css_style_tib_min = dialog.tib_max_input.styleSheet()
    bg_color_tib_min = color_search.search(css_style_tib_min).group(1) 
    assert bg_color_tib_min == '#ffffff'    
    dict_data = dialog.get_advanced_options_dict()        
    assert dict_data["TimeIndepBackgroundWindow"] == ['9','18']

    #check no
    dialog.tib_no.setChecked(True) 

    assert dialog.tib_min_label.isVisible() is False
    assert dialog.tib_min_input.isVisible() is False 
    assert dialog.tib_max_label.isVisible() is False
    assert dialog.tib_max_input.isVisible() is False                    
    dict_data = dialog.get_advanced_options_dict()        
    assert dict_data["TimeIndepBackgroundWindow"] == None
    
    #assert no error
    assert len(dialog.invalid_fields) == 0        
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

    def dialog_completed():
        nonlocal completed
        assert completed is True
        
    QtCore.QTimer.singleShot(500, partial(handle_dialog))
    qtbot.mouseClick(dialog.delete_btn, QtCore.Qt.LeftButton)
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
    
    #invalid
    dialog.table_view.setCurrentCell(0,0)
    dialog.table_view.item(0, 0).setText(",,,")
    bg_color_cell = dialog.table_view.item(0, 0).background().color()
    dialog.table_view.setCurrentCell(1,0)
    assert bg_color_cell == QtGui.QColor("#ff0000")

    #<min
    dialog.table_view.item(1, 0).setText("-1")
    bg_color_cell = dialog.table_view.item(1, 0).background().color()
    dialog.table_view.setCurrentCell(2,0)
    assert bg_color_cell == QtGui.QColor("#ff0000")
    #>max
    dialog.table_view.item(2, 0).setText("201")
    bg_color_cell = dialog.table_view.item(2, 0).background().color()
    dialog.table_view.setCurrentCell(0,1)
    assert bg_color_cell == QtGui.QColor("#ff0000")

    #invalid
    dialog.table_view.item(0, 1).setText("7--9")
    bg_color_cell = dialog.table_view.item(0, 1).background().color()
    dialog.table_view.setCurrentCell(1,1)
    assert bg_color_cell == QtGui.QColor("#ff0000")

    #<min
    dialog.table_view.item(1, 1).setText("-1")
    bg_color_cell = dialog.table_view.item(1,1).background().color()
    dialog.table_view.setCurrentCell(2,1)
    assert bg_color_cell == QtGui.QColor("#ff0000")
    #>max
    dialog.table_view.item(2, 1).setText("9")
    bg_color_cell = dialog.table_view.item(2,1).background().color()
    dialog.table_view.setCurrentCell(0,2)
    assert bg_color_cell == QtGui.QColor("#ff0000")


    #invalid
    dialog.table_view.item(0, 2).setText(":::-")
    bg_color_cell = dialog.table_view.item(0, 2).background().color()
    dialog.table_view.setCurrentCell(1,2)
    assert bg_color_cell == QtGui.QColor("#ff0000")

    #<min
    dialog.table_view.item(1, 2).setText("-1")
    bg_color_cell = dialog.table_view.item(1,2).background().color()
    dialog.table_view.setCurrentCell(2,2)
    assert bg_color_cell == QtGui.QColor("#ff0000")
    #>max
    dialog.table_view.item(2, 2).setText("129")
    bg_color_cell = dialog.table_view.item(2,2).background().color()
    dialog.table_view.setCurrentCell(2,2)
    assert bg_color_cell == QtGui.QColor("#ff0000")

    #assert error
    assert len(dialog.invalid_fields) == 9

def test_tib_invalid(qtbot):
    """Test for invalid inputs in tib"""
    
    dialog = AdvancedDialog()
    dialog.show()
    
    color_search = re.compile("QLineEdit { background-color: (.*) }")
    
    #check yes    
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
    assert bg_color_tib_min == '#ff0000'
    
    css_style_tib_max = dialog.tib_max_input.styleSheet()
    bg_color_tib_max = color_search.search(css_style_tib_max).group(1)  
    assert bg_color_tib_max == '#ff0000'
    
    #assert error
    assert len(dialog.invalid_fields) == 2
    
def test_adt_invalid(qtbot):
    """Test for additional dimensions inputs in tib"""
    dialog = AdvancedDialog()
    dialog.show()
    color_search = re.compile("QLineEdit { background-color: (.*) }")
        
    #1: inprogress
    qtbot.keyClicks(dialog.adt_dim_input, "1")
    css_style_dim= dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)   
    assert bg_color_dim == '#ffaaaa'
       
    #x1: inprogress
    qtbot.keyClicks(dialog.adt_dim_input, "x")
    css_style_dim= dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)   
    assert bg_color_dim == '#ffaaaa'
    
    #x1,: inprogress
    qtbot.keyClicks(dialog.adt_dim_input, ",")
    css_style_dim= dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)   
    assert bg_color_dim == '#ffaaaa'    
        
    #x1,a,a: inprogress/invalid
    qtbot.keyClicks(dialog.adt_dim_input, "a")
    css_style_dim= dialog.adt_dim_input.styleSheet()
    bg_color_dim = color_search.search(css_style_dim).group(1)   
    assert bg_color_dim == '#ffaaaa'      
    
    #assert error
    assert len(dialog.invalid_fields) == 1
    dialog.close()
    

def test_apply_btn_valid(qtbot):
    """Test for clicking apply and storing the data as a dictionary in parent"""
    red_parameters = ReductionParameters()
    dialog = AdvancedDialog(red_parameters)
    dialog.show()
    
    #fill the table
    #1row
    dialog.table_view.setCurrentCell(0,0)
    dialog.table_view.item(0, 0).setText("1,5,9")
    dialog.table_view.setCurrentCell(0,1)
    dialog.table_view.item(0, 1).setText("4,5,7")
    dialog.table_view.setCurrentCell(0,2)
    dialog.table_view.item(0, 2).setText("8-67")    

    #2row
    dialog.table_view.setCurrentCell(1,0)
    dialog.table_view.item(1, 0).setText("9:30:2")
    dialog.table_view.setCurrentCell(1,1)
    dialog.table_view.item(1, 1).setText("4:5,7")
    dialog.table_view.setCurrentCell(1,2)
    dialog.table_view.item(1, 2).setText("32:48:2, 1 ,14")

    #3row
    dialog.table_view.setCurrentCell(2,0)
    dialog.table_view.item(2, 0).setText("1,5,55,100-199")
    dialog.table_view.setCurrentCell(2,1)
    dialog.table_view.item(2, 1).setText("7")
    dialog.table_view.setCurrentCell(2,2)
    dialog.table_view.item(2, 2).setText("120,126,127")
    
    dialog.table_view.setCurrentCell(1,0)     
    
    qtbot.keyClicks(dialog.emin_input, "4.8")
    qtbot.keyClicks(dialog.emax_input, "11.7")            
    qtbot.keyClicks(dialog.gonio_input, "goniometer1")
    qtbot.keyClicks(dialog.adt_dim_input, "xx,23,45")

    #assert no error
    assert len(dialog.invalid_fields) == 0
        
    #click apply
    qtbot.mouseClick(dialog.btn_apply, QtCore.Qt.LeftButton)

    dict_data = dialog.parent.dict_advanced
    
    #assert values are added in parent dictionary
    
    table_data = [
        {'Bank': '1,5,9', 'Tube': '4,5,7', 'Pixel': '8-67'}, 
        {'Bank': '9:30:2', 'Tube': '4:5,7', 'Pixel': '32:48:2,1,14'}, 
        {'Bank': '1,5,55,100-199', 'Tube': '7', 'Pixel': '120,126,127'}
    ]
    for row in range(3):
        assert dict_data["MaskInputs"][row]["Bank"] == table_data[row]["Bank"]
        assert dict_data["MaskInputs"][row]["Tube"] == table_data[row]["Tube"]
        assert dict_data["MaskInputs"][row]["Pixel"] == table_data[row]["Pixel"]        
            
    assert dict_data["E_min"] == '4.8'
    assert dict_data["E_max"] == '11.7'
    assert dict_data["ApplyFilterBadPulses"] == False
    assert dict_data["BadPulsesThreshold"] == '95'
    assert dict_data["TimeIndepBackgroundWindow"] == 'Default'
    assert dict_data["Goniometer"] == 'goniometer1'
    assert dict_data["AdditionalDimensions"] == 'xx,23,45'
    
    dialog.close()     
          
                
