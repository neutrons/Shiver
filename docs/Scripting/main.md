---
layout: default
---

* TOC
{:toc}

Main program
============

The purpose of the main program is to load the data and slice definitions, generate or load the intermediate multidimensional
event workspaces, and create the required histograms. Usually one would also plot any one or two dimensional slices using
matplotlib.

A simple script would look something like this:

```python
from imp import reload
import matplotlib.pyplot as plt
import sys
sys.path.append('/opt/Mantid/bin')
sys.path.append('/opt/Mantid/lib')
sys.path.append('/SNS/groups/dgs/DGS_SC_scripts')

from mantid import plots
from reduce_data_to_MDE import *
from slice_utils import *
import define_data_example
import define_slices_example

#############################################
# MAIN PROGRAM
#############################################
reload(define_data_example)
reload(define_slices_example)

datasets=define_data_example.define_data_set()
reduce_data_to_MDE(datasets)

slice_descriptions=define_slices_example.define_data_slices(extra='_dataset0')

make_slice(datasets[0],slice_descriptions[0])

fig,ax=plt.subplots(subplot_kw={'projection':'mantid'})
c=plot_slice(slice_descriptions[0], ax=ax, cbar_label='Intensity')
set_axes_parameters(ax,**slice_descriptions[0]['Axes_parameters'])
fig.show()
```

Import section
--------------

This is lines 1-12 in the above example. Since the program uses Mantid as the main processing
library, one might add it to the `sys.path` (lines 3-5). You might ommit these if you run
this script from within a Mantid environment (mantidpython or MantidWorkbench). Similarly,
the location of the utlility functions called in this program needs to be available (line 6).
You can skip this information if you already added this files to your python path, or if they
are in the same folder as the current script.

We need to import the following libraries:

* `reduce_data_to_MDE` - utility library to load/ process the raw data to `MDEventWorkspace`
* `slice_utils` - library to generate slices (and optionally plot them)
* Your data description, `define_data_example` in this case
* Your slice description, `define_slices_example` in this case
* Optionally the `mantid.plots` library, in case you want to use matplotlib to plot your data

One might run the program multiple times, just changing data or slice descriptions. Since those
functions are in libraries already loaded in python, just running `import` again will not get the
latest updates. For that one must force reload the libraries (lines 17 and 18).

Getting the data
----------------

To get the data, the first step is to get the corresponding definitions. This is achieved using
a call to the user defined [data description]({{ site.baseurl }}/Scripting/data_description/), in line 20.
The [reduce_data_to_MDE]({{ site.baseurl }}/Scripting/utility/#reduce-raw-data-to-mdevent-workspaces) function (line 21)
takes the list of data descriptions and makes sure that, for each description, the workspace with the given `MDEName` is present
in memory. Optionally, if the `BackgroundMdeName` is not `None`, it will also get those workspaces.

**Note:** Since the generation of the intermediate `MDEvent` data structure is slow, the behavior of
the `reduce_data_to_MDE` function is as follows
* If there is a workspace in memory with the name `MDEName` no further processing will happen
* If the `MDEName` workspace is not in memory, it will try it to load it from the file with the same
name, extension `.nxs`, in the `MdeFolder`
* If the above steps fail, the function will try to generate the workspace from the parameters given
in the data description.

A similar behavior is present for the background data. In the case one would like to re-reduce the original data,
then one would need to delete the workspace from memory *and* delete it from the disk.



Generating slices
-----------------

Similar to getting the data, generating slices is a two step process. In the first step, a call (line 23) to
the userdefined slice description library returns a list of dictionaries, one for each slice. If more
than one dataset is to be cut, it is recommended to use the `extra` parameter to generate a new set of
slice descriptions for each dataset, so that the names of the histogrammed workspaces are different.

The second step is to generate the histogram (1D, 2D, 3D, ...). This is done using the
[make_slice]({{ site.baseurl }}/Scripting/utility/#generating-histograms) function (line 25). The main
parameters are a single dataset description and a single slice description. Most of the calculation is
done using the [MDNorm](https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html) algorithm.
Additional parameters allow for overriding the measured efficiency workspace (usually Vanadium), and for
saving the data in ASCII or HDF5 file (processed MD histogram workspace in Mantid).

The main result is the generation of an MDHistogram workspace with the name given in the slice description.

Plotting slices
---------------

Optionally, one can plot the histograms as part of this script. One can use the
[Mantid/matplotlib](https://docs.mantidproject.org/nightly/plotting/index.html#plotting)
libraries. For convenience, a [plot_slice]({{ site.baseurl }}/Scripting/utility/#plotting-functions)
function can be used for line plots (wrapping a call to matplotlib errorbar function), or for 2D
plots (using matplotlib pcolormesh and colorbar functions). The example in the script above will
generate a 2D plot on the screen.


Notes about polarization
------------------------

For polarized mode, one would like to apply a flipping ratio correction to the data. This
needs to account for both the spin flip and non spin flip data. For convenience, a
`make_slices_FR_corrected` function is available. It uses two datasets, it applies the
flipping ratio corrections, and it will use the `make_slice` function to produce
histograms for both spin states.
