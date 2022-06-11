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

* Single dataset reduction
* Background reduction

Generating histograms
---------------------
* make_slice

Correction functions
--------------------

* Detailed balance
* HYSPEC analyzer transmission
* Flipping ratio correction

Plotting functions
------------------

* plot_slice

