---
layout: default
---

* TOC
{:toc}

Slice Description
=================

Similarly to [Data Description]({{ site.baseurl }}/Scripting/data_description/), the slice descriptions are just
dictionaries that indicate how the program should produce multi-dimensional slices. For ease of use in scripts,
we can generate a function that returns a list of dictionaries.

```python
import numpy as np
from matplotlib.colors import LogNorm

def define_data_slices(extra=''):
    dsl=[]

    # Add single LE slice
    description={'QDimension0':'1,0,0',
                 'QDimension1':'0,1,0',
                 'QDimension2':'0,0,1',
                 'Dimension0Name':'QDimension2',
                 'Dimension0Binning':'-2.5,0.025,2.5',
                 'Dimension1Name':'DeltaE',
                 'Dimension1Binning':'-0.5,0.025,3.25',
                 'Dimension2Name':'QDimension0',
                 'Dimension2Binning':'-0.2,0.2',
                 'Dimension3Name':'QDimension1',
                 'Dimension3Binning':'-2,2',
                  #'SymmetryOperations':'x,y,z;-x,y,z;x,y,-z;-x,y,-z',
                 'ConvertToChi':False,
                 'Plot_parameters':{'norm':LogNorm()},
                 'Axes_parameters':{'xrange':None,'yrange':None,
                                    'xtitle':None, 'ytitle':None,
                                    'title':'CNCS slice',
                                    'aspect_ratio':None,
                                    'tight_axes':True,
                                    'grid':True},
                 'Name':'LE_slice_ K=[-2,2]'+extra}
    dsl.append(description)

    # Add KL slices at different energies in a loop
    for E in np.arange(0,2,0.5):
        dE=0.05
        description={'QDimension0':'1,0,0',
                     'QDimension1':'0,1,0',
                     'QDimension2':'0,0,1',
                     'Dimension0Name':'QDimension1',
                     'Dimension0Binning':'-2.,0.025,2.',
                     'Dimension1Name':'QDimension2',
                     'Dimension1Binning':'-2.5,0.025,2.5',
                     'Dimension2Name':'QDimension0',
                     'Dimension2Binning':'-0.2,0.2',
                     'Dimension3Name':'DeltaE',
                     'Dimension3Binning':f'{E-dE},{E+dE}',
                     'SymmetryOperations':'x,y,z;-x,y,z;x,y,-z;-x,y,-z',
                     'ConvertToChi':False,
                     'Plot_parameters':{'norm':LogNorm(vmin=1e-4,vmax=1e-1)},
                     'Axes_parameters':{'xrange':None,'yrange':None,
                                        'xtitle':None, 'ytitle':None,
                                        'title':f'CNCS E=[{E-dE},{E+dE}]meV',
                                        'aspect_ratio':None,
                                        'tight_axes':True,
                                        'grid':True},
                     'Name':f'KL_slice_{E:.1f}meV'+extra}
        dsl.append(description)

    return dsl
```

For first time users of this software, a recommended approach would be to copy the block between lines 6-30
for each of the slices. Don't forget to append the slice description to the list.

Note that the program is using the [MDNorm](https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html)
algorithm to generate slices, so most of the parameters in the slice descriptions are just properties
of the algorithm.


Name
====

Each slice needs to have a unique name. In the example above, the function returning the list of slice
description contains an *extra* parameter. This is to allow to use the same function to describe slices out of different
datasets. For example, one can call
```python
sd_5K = define_data_slices(extra='_T=5K')
sd_1K = define_data_slices(extra='_T=1K')
```

Reciprocal space geometry parameters
====================================

QDimension0, QDimension1, QDimension2
-------------------------------------

These represent three 3D vectors that define the projection axes. If not defined, these are set by default to
`[1,0,0], [0,1,0], [0,0,1]`, corresponding to projections along the `[H,0,0], [0,K,0], [0,0,L]` axes.
Note that this projections must not be co-planar, but they don't have to be orthogonal.

Dimension0Name, Dimension1Name, ...
-----------------------------------

These parameters specify the dimension of the ouput multidimensional histogram workspace.
Allowed values are `QDimension0`, `QDimension1`, `QDimension2`, `DeltaE`, and any of the names in the
[AdditionalDimensions]({{ site.baseurl }}/Scripting/data_description/#additionaldimensions)
parameters. By default the first three are `QDimension0`, `QDimension1`, `QDimension2`. There needs to be exactly one Name for every dimension in the MDE workspace.

So if one would like to generate a two dimensional slice, with the horizontal axis being `[0,K,0]` and the
vertical axis along the energy transfer, they would need to choose `QDimension1` for `Dimension0Name`,
`DeltaE` for `Dimension1Name`, with the remaining dimension names being `QDimension0` and `QDimension2`.

Dimension0Binning, Dimension1Binning, ...
-----------------------------------------

For each of the dimensions in the output workspace one must choose a binning. These parameters are strings, containing
one, two, or three numbers, with the following meaning:

* three numbers - minimum value, step, maximum value
* two numbers - minimum value, maximum value (data is integrated between these limits)
* one number - step. This is similar to the three number option, but the program will decide the minimum and maximum values.
* empty string - completely integrate the corresponding dimension

For example, a 2D slice in the `[0, K, L]` plane around the elastic line will be defined by

```
   'Dimension0Name':'QDimension1',
   'Dimension0Binning':'-2.,0.025,2.',
   'Dimension1Name':'QDimension2',
   'Dimension1Binning':'-2.5,0.025,2.5',
   'Dimension2Name':'QDimension0',
   'Dimension2Binning':'-0.2,0.2',
   'Dimension3Name':'DeltaE',
   'Dimension3Binning':'-.1,.1',
```

A 1D cut along the energy transfer, with a step of 0.1 meV, going through `[2,1,0]` Bragg peak, would look similar to this:

```
   'Dimension0Name':'DeltaE',
   'Dimension0Binning':'0.1',
   'Dimension1Name':'QDimension0',
   'Dimension1Binning':'1.9,2.1',
   'Dimension2Name':'QDimension1',
   'Dimension2Binning':'0.9,1.1',
   'Dimension3Name':'QDimension2',
   'Dimension3Binning':'-.1,.1',
```

SymmetryOperations
------------------

To increase statistics, one might use symmetry operations. This parameter is a string that contain one of the following:

* list of symmetry operations. Different symmetry operations are separated by semicolon. For example, `'x,y,z;x,-y,z;-x,y,z;-x,-y,z'`.
* a string describing the space group.
* a string describing the point group.

**Notes:**

* applying a symmetry operation is not folding the data
* if one is looking to add symmetrized data and the original one, don't forget to add the identity operation `x,y,z`.
* the time to produce a slice increases proportionally with the number of symmetry operations.
* point and space groups are case and space sensitive. To get a list of possible space and point groups run the code below in Mantid:

```python
from mantid.geometry import SpaceGroupFactory
from mantid.geometry import PointGroupFactory

print('Point groups')
print('; '.join([pgs for pgs in PointGroupFactory.getAllPointGroupSymbols()]))
print('Space groups')
print('; '.join([sgs for sgs in SpaceGroupFactory.getAllSpaceGroupSymbols()]))
```


Plotting related parameters
===========================

As part of the experimental reduction, an important step is plotting of the cuts and slices of the data.
While it is not necessary to fill in these parameters (plotting can be done independently of this software),
sometimes it's convenient to to store the settings for given figures. This program uses
[matplotlib](https://matplotlib.org/) and the [Mantid extensions](https://docs.mantidproject.org/nightly/plotting/index.html) to it.

Axes_parameters
---------------

This is a dictionary of key-value pairs that are related to the `axis` objects in matplotlib. Not all features are supported.

* title - a tring that contains the title of the plot
* grid - if `True` it will show the grid
* xrange, yrange - list with two elements to control the extents of x and y axes
* xtitle, ytitle - strings to override the default axes titles
* aspect_ratio - 'auto', 'equal', or a float. See [set_aspect](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.set_aspect.html)
* tight_axes - the `tight` parameter for [matplotlib.axes.Axes.autoscale](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.autoscale.html)

Plot_parameters
---------------

For one dimensional data, the [plot_slice]({{ site.baseurl }}/Scripting/utility/#plotting-functions) function uses the matplotlib
[errorbar](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.errorbar.html?highlight=errorbar#matplotlib.axes.Axes.errorbar) function, while for two dimensional
plots it uses the [pcolormesh](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html?highlight=pcolormesh#matplotlib.axes.Axes.pcolormesh).
Any key-value pairs in the `Plot_parameters` are passed to the corresponding matplotlib function.


Other parameters
================

ConvertToChi
------------

If set to True, this parameter will change the plots to dynamic susceptibility &chi;''. The temperature is taken from the
[data description]({{ site.baseurl }}/Scripting/data_description/#samplelogvariables).
See [AppliedDetailedBalanceMD](https://docs.mantidproject.org/nightly/algorithms/ApplyDetailedBalanceMD-v1.html)
algorithm in Mantid.

Smoothing
---------

If a number is given, the histogram will be smoothed using a Gaussian kernel with the given FWHM (in units of histogram bins).
