---
layout: default
---

* TOC
{:toc}

Utilities
=========

Find raw data using OnCat
-------------------------

For many experiments users already used sequence names or comments to group together runs for autoreduction.
If that's the case, this information is stored in the https://oncat.ornl.gov database. There are some functions
available to access the database and retrieve the information. It is recommended to write a separate script to
log in to ONCat, retrieve run information, and store it in a json file. An example script can be found below:

```python
import pyoncat
from oncat_util import oncat_login, write_json_from_oncat

# login to oncat if required
try:
    ocl.Facility.list()
except (NameError, pyoncat.LoginRequiredError, pyoncat.InvalidRefreshTokenError):
    ocl = oncat_login()

# generate file and print the keys
keys = write_json_from_oncat(filename="/SNS/some_path/deleteme.json",
                             login=ocl,
                             ipts_number="27023",
                             instrument="ARCS",
                             group_by_angle=True)
print(keys)
```
Save the script in your folder, say as `retrieve_data_IPTS-27023.py`. Open a terminal, navigate to your folder,
start `mantidpython`, then type `run -i retrieve_data_IPTS-27023.py`. The script will save a file,
`/SNS/some_path/deleteme.json`, and will print the keys (the names of the datasets you used in autoreduction).

The beginning of the output file will look like
```
{"Sample_800meV_flux_5K": [[223212], [223213], [223214], [223215], [223216], [223217], [223218], [223219], [223220], [223221], [223222], [223223], [223224], [223225], [223226], [223227], [223228], [223229], [223230], [223231], [223232], [223233], [223234], [223235], [223236], [223237], [223238], [223239], [223240], [223241], [223242], [223243], [223244], [223245], [223246], [223247]], "Sample_30meV_new_5K": [[229833, 230557]]
```
and the keys are
```
dict_keys(['Sample_800meV_flux_5K', 'Sample_30meV_new_5K', 'None', ' ', 'Sample_30meV_new_18K', 'Sample_300meV_flux_5K', 'Sample_60meV_res_5K', 'Sample_120meV_flux_5K', 'Sample_30meV_new_300K', 'Sample_30meV_res_5K', 'Sample_30meV_new_100K', 'Sample_500meV_flux_5K'])
```
To use this information, change the value of `Runs` to
```python
'Runs':{'file':'/SNS/some_path/deleteme.json', 'ky':"Sample_800meV_flux_5K"}
```
It might happen that the information in the ONCat database is not accurate, or some files must be added or excluded from one dataset.
The `write_json_from_oncat` function can add or exclude runs from a dataset, and it can group entries by angle. Please see the
documentation in the function. Also, there are several examples available in the `oncat_example.py` file.

Reduce raw data to MDEvent workspaces
-------------------------------------

The `reduce_data_to_MDE` function takes a lists of dataset description and will try to get the associated workspace in memory. If already there, the function does not try to load or generate them again. For each dataset in the list, if the workspaces are not in memory, it will try to load them from the disk. Finally, if this step fails, it will call the `generate_mde(dataset)` function, and optionally the `generate_BG_mde(data_set,compress_events_tof)` to produce muti-dimensional event workspaces. In the case of background, all files are summed together, then transformed to an angle-independent momentum trasfer frame (laboratory frame). In future releases, these two functions will be combined into asingle one, with an additional flag to specify if the result is real data or background.

Generating histograms
---------------------

* The `make_slice(data_set, slice_description, solid_angle_ws=None, ASCII_slice_folder='', MD_slice_folder='')` function is the main histogramming utility of this program. It is based on the `MDNorm` algorithm. 
```python
slicename = make_slice(data_set,slice_description, solid_angle_ws=None, ASCII_slice_folder='', MD_slice_folder='')
```
The `data_set` dictionary contains the name of the input multi-dimensional event workspace, and optionally background information, incoherent scatterer information, and temperature (for converting to dynamical susceptibility). The `slice_description` parameter is one of the elements in the list of [slice descriptions]({{ site.baseurl }}/Scripting/slice_description/). The optional `solid_angle_ws` can be used to override the value of the incoherent scattering workspace used to measure the detector efficiency. 
If `ASCII_slice_folder` or `MD_slice_folder` are defined, the function will save ASCII or MDHistogram NeXus files in the given folders.

Correction functions
--------------------

* Detailed balance - If the temperature is set in the `data_set['SampleLogVariables']['Temperature']` entry, and `ConvertToChi` is set to `True` in the slice description, the `ApplyDetailedBalanceMD` from Mantid will act on the MDEvent workspace. A new workspace will be created , named after the original one, with a `_chi` postfix.
* HYSPEC analyzer transmission - Currently will be used to generate the `MDEvent` workspace with an exponential correction function of the scattered energy.
* Flipping ratio correction - The `make_slices_FR_corrected` function uses two dataset descriptions, one for spin flip scattering and one for non spin flip. It uses the [FlippingRatioCorrectionMD](https://docs.mantidproject.org/nightly/algorithms/FlippingRatioCorrectionMD-v1.html) algorithm and several calls to `make_slice` to provide a correction for finite capabilities of the instrument to separate the two polarizations.

Plotting functions
------------------

* The `plot_slice` function is a wrapper for using matplotlib/Mantid plotting utilities. It can deal with 1D histograms (using the `errorbar` function) and 2D Historgrams (using `pcolormesh`). Any `Plot_parameters` values in the slice descriptions are passed to the corresponding plotting functions
