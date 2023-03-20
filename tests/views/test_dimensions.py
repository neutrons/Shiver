"""UI tests for HistogramParameter button"""
import functools
from qtpy import QtCore, QtWidgets 
#QGroupBox
from shiver.views.histogram import HistogramParameter
import re

def test_dimensions_radio_btn(qtbot):
    """Test for selecting the Dimension step size radio buttons and accessing the steps"""
    
    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
   

    #set 4D volume
    qtbot.mouseClick(histogram_parameters.cut_4d, QtCore.Qt.LeftButton)
    #set steps
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step1, "0.5") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step2, "0.2") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step3, "0.02") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step4, "2") 
    

    # dimensions 1-4
    assert histogram_parameters.dimesions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimesions.combo_step2.text() == "0.2"   
    assert histogram_parameters.dimesions.combo_step3.text() == "0.02"   
    assert histogram_parameters.dimesions.combo_step4.text() == "2"   

    qtbot.wait(1000)
         
    histogram_parameters.dimesions.combo_step1.clear()
    histogram_parameters.dimesions.combo_step2.clear()
    histogram_parameters.dimesions.combo_step3.clear()
    histogram_parameters.dimesions.combo_step4.clear()    
    #set 3D volume
    qtbot.mouseClick(histogram_parameters.cut_3d, QtCore.Qt.LeftButton)

    #set steps 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step1, "0.5") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step2, "0.2") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step3, "0.02") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step4, "2") 

    # dimensions 1-4
    assert histogram_parameters.dimesions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimesions.combo_step2.text() == "0.2"   
    assert histogram_parameters.dimesions.combo_step3.text() == "0.02"   
    assert histogram_parameters.dimesions.combo_step4.text() == ""     
    
    qtbot.wait(1000) 
    
    histogram_parameters.dimesions.combo_step1.clear()
    histogram_parameters.dimesions.combo_step2.clear()
    histogram_parameters.dimesions.combo_step3.clear()
    histogram_parameters.dimesions.combo_step4.clear()       
    #set 2D volume
    qtbot.mouseClick(histogram_parameters.cut_2d, QtCore.Qt.LeftButton)
    #set steps 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step1, "0.5") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step2, "0.2") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step3, "0.02") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step4, "2") 
    

    # dimensions 1-4
    assert histogram_parameters.dimesions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimesions.combo_step2.text() == "0.2"   
    assert histogram_parameters.dimesions.combo_step3.text() == ""   
    assert histogram_parameters.dimesions.combo_step4.text() == ""      

    qtbot.wait(1000) 

    histogram_parameters.dimesions.combo_step1.clear()
    histogram_parameters.dimesions.combo_step2.clear()
    histogram_parameters.dimesions.combo_step3.clear()
    histogram_parameters.dimesions.combo_step4.clear()   
    #set 1D volume
    qtbot.mouseClick(histogram_parameters.cut_1d, QtCore.Qt.LeftButton)
    #set steps 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step1, "0.5") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step2, "0.2") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step3, "0.02") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_step4, "2") 
    

    # dimensions 1-4
    assert histogram_parameters.dimesions.combo_step1.text() == "0.5"
    assert histogram_parameters.dimesions.combo_step2.text() == ""   
    assert histogram_parameters.dimesions.combo_step3.text() == ""   
    assert histogram_parameters.dimesions.combo_step4.text() == ""       
    
    
def test_dimensions_min_max_color_valid(qtbot):    
    """Test for min max valu pairs in dimensions"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
    
    p = re.compile("background-color: (.*) ")
    
    #min1<max1
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min1, "1") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max1, "3") 
    
    css_style_min1 = histogram_parameters.dimesions.combo_min1.styleSheet()
    css_style_max1 = histogram_parameters.dimesions.combo_max1.styleSheet()
    
    bg_color_min = p.search(css_style_min1).group(1)
    bg_color_max = p.search(css_style_max1).group(1)    

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"
    
    #min2<max2
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min2, "0") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max2, "4") 
    
    css_style_min2 = histogram_parameters.dimesions.combo_min2.styleSheet()
    css_style_max2 = histogram_parameters.dimesions.combo_max2.styleSheet()
    
    bg_color_min = p.search(css_style_min2).group(1)
    bg_color_max = p.search(css_style_max2).group(1)    

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"   
    
    #min3<max3
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min3, "10") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max3, "12") 
    
    css_style_min3 = histogram_parameters.dimesions.combo_min3.styleSheet()
    css_style_max3 = histogram_parameters.dimesions.combo_max3.styleSheet()
    
    bg_color_min = p.search(css_style_min3).group(1)
    bg_color_max = p.search(css_style_max3).group(1)    

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"
    
    #min4<max4
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min4, "5") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max4, "7") 
    
    css_style_min4 = histogram_parameters.dimesions.combo_min4.styleSheet()
    css_style_max4 = histogram_parameters.dimesions.combo_max4.styleSheet()
    
    bg_color_min = p.search(css_style_min4).group(1)
    bg_color_max = p.search(css_style_max4).group(1)    

    assert bg_color_min == "#ffffff"
    assert bg_color_max == "#ffffff"        

    
def test_dimensions_min_max_color_invalid(qtbot):    
    """Test for min max valu pairs in dimensions"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
    
    p = re.compile("background-color: (.*) ")
        
    #min1>max1
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min1, "4") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max1, "3") 
    
    css_style_min = histogram_parameters.dimesions.combo_min1.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max1.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    


    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"       
    
    #min2>max2
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min2, "7") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max2, "5") 
    
    css_style_min = histogram_parameters.dimesions.combo_min2.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max2.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"    

    #min3>max3
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min3, "0") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max3, "-2") 
    
    css_style_min = histogram_parameters.dimesions.combo_min2.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max2.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"   
    
    #min4>max4
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min4, "7") 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max4, "3") 
    
    css_style_min = histogram_parameters.dimesions.combo_min4.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max4.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"

    
def test_dimensions_min_max_color_missing(qtbot):    
    """Test for min max valu pairs in dimensions"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
    
    p = re.compile("background-color: (.*) ")
        
    #min1 is missing
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max1, "7")     
    css_style_min = histogram_parameters.dimesions.combo_min1.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max1.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    
    #min2 is missing
    qtbot.keyClicks(histogram_parameters.dimesions.combo_max2, "2")         
    css_style_min = histogram_parameters.dimesions.combo_min2.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max2.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
    
    #max3 is missing
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min3, "2")             
    css_style_min = histogram_parameters.dimesions.combo_min3.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max3.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
        
    #max4 is missing 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_min4, "2")                    
    css_style_min = histogram_parameters.dimesions.combo_min4.styleSheet()
    css_style_max = histogram_parameters.dimesions.combo_max4.styleSheet()
    
    bg_color_min = p.search(css_style_min).group(1)
    bg_color_max = p.search(css_style_max).group(1)    

    assert bg_color_min == "#ff0000"
    assert bg_color_max == "#ff0000"
            
def test_dimensions_dropdown_uniqueness(qtbot):    
    """Test for dimensions dropdown selection values are unique among them"""

    # start widget
    histogram_parameters = HistogramParameter()
    qtbot.addWidget(histogram_parameters)
    histogram_parameters.show()
    
    #["[H,0,0]", "[0,K,0]", "[0,0,L]", "DeltaE"]
    combo_dimensions = histogram_parameters.dimesions.combo_dimensions
    #[0, 1, 2, 3]
    previous_dimension_value_indexes = histogram_parameters.dimesions.previous_dimension_value_indexes
    
    qtbot.wait(5000) 

    #set all different 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim1, combo_dimensions[0]) 
    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim2, combo_dimensions[1])
    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim3, combo_dimensions[2])
    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim4, combo_dimensions[3])  
    qtbot.wait(5000) 
#    # dimensions 1-4
#    assert histogram_parameters.dimesions.combo_dim1.currentText() == combo_dimensions[0]
#    assert histogram_parameters.dimesions.combo_dim2.currentText() == combo_dimensions[1]
#    assert histogram_parameters.dimesions.combo_dim3.currentText() == combo_dimensions[2]
#    assert histogram_parameters.dimesions.combo_dim4.currentText() == combo_dimensions[3]
#    
#    #swap 1->3
#    print("Start 1->3")
#    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim1, combo_dimensions[2]) 
#    qtbot.wait(5000)
#    # dimensions 1-4
#    assert histogram_parameters.dimesions.combo_dim1.currentText() == combo_dimensions[2]
#    assert histogram_parameters.dimesions.combo_dim2.currentText() == combo_dimensions[1]
#    assert histogram_parameters.dimesions.combo_dim3.currentText() == combo_dimensions[0]
#    assert histogram_parameters.dimesions.combo_dim4.currentText() == combo_dimensions[3]

#    #swap 4->2
#    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim4, combo_dimensions[2]) 

#    # dimensions 1-4
#    assert histogram_parameters.dimesions.combo_dim1.currentText() == combo_dimensions[3]
#    assert histogram_parameters.dimesions.combo_dim2.currentText() == combo_dimensions[4]
#    assert histogram_parameters.dimesions.combo_dim3.currentText() == combo_dimensions[0]
#    assert histogram_parameters.dimesions.combo_dim4.currentText() == combo_dimensions[2]

#    #swap 2->3
#    qtbot.keyClicks(histogram_parameters.dimesions.combo_dim2, combo_dimensions[0]) 

#    # dimensions 1-4
#    assert histogram_parameters.dimesions.combo_dim1.currentText() == combo_dimensions[3]
#    assert histogram_parameters.dimesions.combo_dim2.currentText() == combo_dimensions[0]
#    assert histogram_parameters.dimesions.combo_dim3.currentText() == combo_dimensions[4]
#    assert histogram_parameters.dimesions.combo_dim4.currentText() == combo_dimensions[2]
#                        

