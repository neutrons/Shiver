---
layout: default
---
Slice Description
================

The purpose in this file is to describe a one or more dimension workspace histogrammed from the workspace.  It contains a list of these items so you can make more than one at a time.

Example
-----------------

The following example shows the description fora two dimensional slice and a one dimensional cut.

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
description2 = {'QDimension0':'0,0,1',
               'QDimension1':'1,1,0',
               'QDimension2':'1,-1,0',
               'SymmetryOperations':'x,y,z;-x,y,z;x,y,-z;-x,y,-z',
               'ConvertToChi':False, #Future option: MANTID algorithm not yet implemented
               'Plot_parameters': {'norm':LogNorm()},
               'Axes_parameters': {'xrange':None,'yrange':None, 'xtitle':None,
                                   'ytitle':None,'title':'ARCS', 'aspect_ratio':None, 'tight_axes':True, 'grid':True}
               'Dimension0Name': 'QDimension0',
               'Dimension0Binning': '-2.05,-1.95',
               'Dimension1Name': 'QDimension1',
               'Dimension1Binning':  '-0.1,0.1',
               'Dimension2Name': 'QDimension2',
               'Dimension2Binning': '-0.1,0.1',
               'Dimension3Name': 'DeltaE',
               'Dimension3Binning': '-5.0,1,90.0',
               'Name':'HH_L-2_E_100meV'
            }
 dsl.append(description2)           
```

Description
------------

- **QDimension0, QDimension1, QDimension2** - define the orientation to use to do the slicing and cutting.

- **Dimension0Name, Dimension1Name, Dimension2Name, ...** - define which dimension corresponds to which.  It can be one of the QDimension, DeltaE, or additional Dimensions if they have been defined. There needs to be 1 Name for every dimension in the MDE workspace.

- **Dimension0Binning, Dimension1Binning, Dimension1Binning, ...** - define the binning along each dimension.  If three values are give it is min, step, max.  If two values are given that dimension will be integrated between the 2 values.  There needs to be 1 Binning for every dimension in the MDE workspace.

- **Symmetry Operations** - this will combine data that is at equivalent symmetry positions according to the provided operation.
The available symmetry operations are described in [Mantid Symmetry Reference](https://docs.mantidproject.org/nightly/concepts/PointAndSpaceGroups.html)

- **Plot_parameters** - are parameters to pass through to the matplotlib plot commands
- **Axis_parameters** - are parameters to adjust the axes in the plot.
