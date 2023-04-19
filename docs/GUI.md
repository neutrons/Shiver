---
layout: default
---
* TOC
{:toc}

GUI
===

In preparation for a stable release of the software, work has started on a development of a graphical user interface (GUI).

Release schedule
----------------
In phase 1 (April 2023), the GUI will implement the functionality of `make_slice`. In phase 2 (June 2023), the GUI will also allow creation of the multidimensional event workspaces, the equivalent of `reduce_data_to_MDE`. Phase 3 (undecided release date), will contain possibility to get the sample orientation from the peaks in the multidimensional event workspace, calculating background by looking at the minimum scattering as a function of goniometer rotation, and some polarization related functionality.

Starting
--------

Currently it is installed on analysis.sns.gov. To start it, in a terminal type `shiver` (for main release) or `shiver --qa` (for testing branch). This will open the shiver main window:

![Main Shiver GUI]({{ site.baseurl }}/images/Shiver-main.png)

Alternatively, one can activate the conda environment `conda activate shiver` or `conda activate shiver-qa`, start `mantidworkbench`, then navigate in the menu to `Interfaces`>`Direct`>`Shiver`.

![Launching Shiver from Mantid]({{ site.baseurl }}/images/Shiver-mantid.png)

Loading data
------------

Data and background multidimensional event workspaces can be loaded using `Load MDE` button. Workspaces that contain goniometer angle dependent data will show up with a `Qs` (Q-sample-frame in Mantid terminology) icon next to their name. These can be used as either data or background. Workspaces that contain only goniometer angle independent information will have a `Ql` icon (Q-laboratory-frame).

One can right click on an item. This will open a context menu. The user must select one workspace to be the `Data`. Optionally, one can select a `Background`.

![Context menu for MDEvent workspaces]({{ site.baseurl }}/images/Shiver-mde_menu.png)

The `Provenance` item is not yet implemented. It will show parameters used to generate the workspace. Currently, `Set sample parameters` will open a tab to set/overwrite the sample lattice parameters and orientation (UB matrix)

![Shiver UB setup]({{ site.baseurl }}/images/Shiver-UB.png)

Using the `Set corrections` context menu item will open a new tab. Currently implemented features are corrections for detailed balance and for HYSPEC polarizer transmission. Applying these corrections will result in new MDEvent workspaces in the list. Their name appends `_DB`/`_PT` or both to the original workspace name.

![Shiver corrections tab]({{ site.baseurl }}/images/Shiver-corrections_tab.png)

![Shiver corrected workspaces]({{ site.baseurl }}/images/Shiver-corrections_DB.png)

To load a normalization workspace (incoherent Vanadium or TiZr scattering), click on `Load normalization`. If the workspace is selected, it will be used for normalization. To unselect it, press the `Ctrl` key and click it with the mouse.

Alternatively, one can load dictionaries from previous uses of the scripting features. Click on `Load dataset`, then navigate to a python script that contain the data definition. The program will try to look up the `define_data_set` function. If found, the user is presented with an option to load the workspaces related to one particular dictionary. On successfull load, data/ background/ normalization are automatically selected.

Histogram parameters
--------------------

When generating a histogram, one would like to have a unique name. The viewing axes are set up using the `Projection u, v,w` inputs. Projections must not be colinear. This will change the dimenion names. Selecting numbers of non-integrated dimensions can be done using the radio buttons. For each of the non-integrated dimensions a step must be provided. All dimensions allow setting of minimum/maximum values (these must be doen in pairs). The symmetry operations are the same as those accepted by the MDNorm algorithm. Smoothing options is a gaussian. The number represents the width in histogram pixels. Click on `Histogram` button to produce the MDHistogram workspace

Histogram plotting/output options
---------------------------------

Once the histogram workspace is produced, it will show up in the list on the right hand side. If selected, a histogram will try to populate the GUI with the parameters used to generate it. Right clicking on the workspace opens a context menu, to allow plotting or saving the data.

![Shiver histogram menu]({{ site.baseurl }}/images/Shiver-histo_menu.png)


Known bugs/issues
-----------------
* Some progress reporting is not accurate
* Script generation is not yet very useful (will be fixed when we release part 2)
* Save in the ASCII format for histogram is not yet implemented

