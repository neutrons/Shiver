---
layout: default
---
Slice Description
================

The purpose in this file is to describe a one or more dimension workspace histogrammed from the workspace.  It contains a list of these items so you can make more than one at a time.
A two dimensional slice is made as follows

```python
dsl=[]
description = {'QDimension0':'0,0,1',
               'QDimension1':'1,1,0',
               'QDimension2':'1,-1,0',
               'SymmetryOperations':'x,y,z;-x,y,z;x,y,-z;-x,y,-z',
               'ConvertToChi':False, #Future option: MANTID algorithm not yet implemented
               'Plot_parameters': {'norm':LogNorm()},
               'Axes_parameters': {'xrange':None,'yrange':None, 'xtitle':None, 'ytitle':None,
                                    'title':'ARCS', 'aspect_ratio':None, 'tight_axes':True, 'grid':True}
               'Dimension0Name': 'QDimension0',
               'Dimension0Binning': '-2.05,-1.95',
               'Dimension1Name': 'QDimension1',
               'Dimension1Binning':  '-0.1,0.1',
               'Dimension2Name': 'QDimension2',
               'Dimension2Binning': '-6.0,0.025,6.0',
               'Dimension3Name': 'DeltaE',
               'Dimension3Binning': '-5.0,1,90.0',
               'Name':'HH_L-2_E_100meV'
            }
dsl.append(description)
```
