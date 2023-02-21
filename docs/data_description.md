---
layout: default
---

* TOC
{:toc}

Data Description
================

The purpose of this program is to transform time of flight event data into histograms in reciprocal space.
If one would like to look at more than one histogram of the same raw data, it would be computationally expensive to
repeat all the calculations. It is more efficient to preprocess data by applying various corrections, coordinate
transformations only once, and then store them in an intermediate data structure.
One of the [utility functions]({{ site.baseurl }}/utility/) to be called in the [main program]({{ site.baseurl }}/main/)
is taking care of this process. The only input parameter is a list of python dictionaries, each containing a
dataset description. This section will show the content of such a dictionary.

The minimal dataset decription can be generated in a function like:

```python
raw_data_folder='/SNS/CNCS/IPTS-21407/nexus/'
mde_folder='/SNS/CNCS/IPTS-21407/shared/MDE/'
vanadium_file = '/SNS/CNCS/IPTS-21407/shared/autoreduce/van_277537.nxs'

def define_data_set(**kwargs):
    data_set_list=[]

    # single dataset
    data_set={'Runs':range(297517,297696+1),
              'RawDataFolder':raw_data_folder,
              'MdeFolder':mde_folder,
              'MdeName':'merged_3K',
              'MaskingDataFile':vanadium_file,
              'NormalizationDataFile':vanadium_file,
              'UBSetup':{'a':5.12484,'b':5.33161,'c':7.31103,
                         'alpha':90,'beta':90,'gamma':90,
                         'u':'-0.0493617,4.27279,-4.37293',
                         'v':'-0.0706905,-3.18894,-5.85775'},
              }
    data_set_list.append(data_set)

    return data_set_list
```

If you want to describe more datasets, just repeat the code between lines 8 and 21. Don't forget to append it to the list
of datasets.

Mandatory parameters
====================

Runs
----

The `Runs` are a list (or any iterable) of run numbers or a list of run numbers. Together with the `RawDataFolder` parameter, 
these are describing what is the raw data. If the elements of the original list are
integers, say `NNNN`, then the reduction will look in the raw data folder for the file `*NNNN.nxs.h5`.

If the original iterable contains lists of runs, these will be added together for processing (assumed
to have the same sample orientation).

Here are a few examples:

```python
# for runs 10, 11, 12, 13, 14
range(10,15)
# for runs 100, 102, 105
[100, 102, 105]
# add together some ranges - this one is runs from 10 to 20, skipping 15
list(range(10,15)) + list(range(16, 21))
# add runs together for processing - runs separated by 10 have the same goniometer angle
[[100, 110], [101,111], [102, 112], [103, 113], [104], [105]]
```

In addition, we can store the run information in a json file. This is very useful if the [OnCat](https://oncat.ornl.gov)
database is used. Using the [oncat utilites]({{ site.baseurl }}/utility/) functions, one generates a file, say
`deleteme.json` with the following content:

```json
{"100meV_5K": [[222204, 222208], [222205, 222206], [222207, 222209]]}
```
Then, the value of `'Runs'` will be 
```python
{'file':'/SNS/some_path/deleteme.json', 'ky':"100meV_5K"}
```


RawDataFolder
-------------

The folder where the raw data (.nxs.h5) files are located.

MdeName
-------

The name of the intermediate dataset. This is a [Mantid](https://mantidproject.org) mutlidimensional event workspace.

**Note:** Make sure each dataset has a unique name.

MdeFolder
---------

The storage location for the intermediate dataset.

NormalizationDataFile
---------------------

This is a processed NeXus file that contains the efficiency/ solid angle measurement. It is usually
obtained by scattering from an incoherent scatterer, such as Vanadium or TiZr alloy. It will contain the same number
of spectra as the raw data, but it is integrated into a single bin (usually either energy or wavelength). It can contain
information about masking. At SNS, one can use the integrated Vanadium that is used for autoreduction.
It can be set to `None` if all detectors have the same efficiency.

MaskingDataFile
---------------

The masking data file is a Mantid procesed nexus file that contains information about masked data. In most
cases one can use the same file as the normalization data. It can also be set to `None`, in which case
the top and bottom eight pixels in each detector tube.


Additional parameters
=====================

BackgroundMdeName
-----------------

The name of the background intermediate data. Currently, two types of background butraction are implemented in this
program. In the first case, one can measure background at the same angles as the data (say a measurement at a different
temperature). In this case we process the background first, then use the `MdeName` of the background dataset as
the `BackgroundMdeName` for the current data. A second option would be to measure an isotropic background. In this cae,
the background runs must be specified.

BackgroundRuns
--------------

This is a list of runs to be added together and processed as a single background.

BackgroundScaling
-----------------

When one subtracts a background, one might need to rescale it (different amount of background). By default, the scaling factor is 1.


RawDataFolderBackground
-----------------------

The location for the raw background files. If not entered, it will be the same as the `RawDataFolder`


UBSetup
-------

For convenience, one can save the sample lattice parameters and orientation using the UB matrix formalism. The
value of this parameter is a dictionary containing the input parameters for the
[SetUB](https://docs.mantidproject.org/nightly/algorithms/SetUB-v1.html) Mantid algorithm (with the except of `InputWorkspace`).

Overriding default reduction parameters
=======================================

The program will try to guess the correct reduction parameters, but it might get the wrong values in some cases.
It is advisable to consult the instrument scientist before modifying any of these values.
Here are some inputs that can be set by the user:

Ei
--

The incident energy in meV.

T0
--

The time zero offset (the nominal time when the neutrons leave the moderator face).

SampleLogVariables
------------------

Some additional sample logs might be required to reduce the data. The value of this parameter is a dictionary.
Currently only the following keys are processed:

* `'OmegaMotorName'`: a string that contains the name of the motor for sample rotation around the vertical axis.
If set to `None`, the default the goniometer setting is found from the `phi`, `chi`, and `omega` sample logs, but for some older
files one might need to use something like `'huber'` or `'CCR13VRot'`. Consult with the instrument scientist.
* `'Temperature'`: The temperature (in Kelvin) of the sample. It can be a number or a string containing the sample log corresponding
to the temperature. This is only used to calculate the dynamic susceptibility (apply the detailed balance).

BadPulsesThreshold
------------------

If one wants to filter out events with low proton charge (during the ramping of the accelerator), this input
is used by the [FilterBadPulses](https://docs.mantidproject.org/nightly/algorithms/FilterBadPulses-v1.html)
algorithm. By default it is `None`.

TimeIndepBackgroundWindow
-------------------------

This parameter allows a time independent background subtraction. The following options are allowed:
* `None` - no time independent bakckground.
* `'Default'` - for CNCS and HYSPEC instruments there are Mantid algorithms to guess and independent
background range, based on incident energy. There is no processing done for other instruments
* `[TIB_min, TIB_max]` - a list with the time independent background range in units of microseconds. Consult your local
contact for adequate values.

E_min
-----

The lower end of energy transfer to be processed, in units of meV. If set to `None` the program will use -0.95 times the
incident energy.

E_max
-----

The upper end of energy transfer to be processed, in units of meV. If set to `None` the program will use +0.95 times the
incident energy.

AdditionalDimensions
--------------------

By default the intermediate data is stored as a muti-dimensional workspace. The coordinates are momentum transfer in the
sampel coordinate frame and energy transfer. This parameter allows adding additional dimensions (such as temperature).
Each additional dimension is a triplet. The first element of the triplet is the sample log variable name, the
second and third are the minimum and maximum values to be used. For example, set `'AdditionalDimensions'` to:

```
[('SampleTemp', 0, 300)]
```


Polarization related parameters
===============================

PolarizationState
-----------------

This is a label for polarization state, such as `'SF_Px';'NSF_Px';'SF_Py';'NSF_Py';'SF_Pz';'NSF_Pz'`. It is not
directly used by the program. It is intended for future expansion to calculate nuclear, magnetic, and
incoherent cross sections for polarized experiments.

FlippingRatio
-------------

A number or a mathematical expression involving certain sample environment parameters, that allows corrections
for flipping ratio. For details see [FlippingRatioCorrectionMD](https://docs.mantidproject.org/nightly/algorithms/FlippingRatioCorrectionMD-v1.html)
algorithm. For example, setting this value to 
```python
'6.5+2.8*cos((omega+3.7)*pi/180),omega'
```
will generate a flipping ratio that is dependent on the `omega` value in the raw files.

PolarizingSupermirrorDeflectionAdjustment
-----------------------------------------

In case that the sample log specifying that a run is measured in polarized mode is not correctly recorded in the file,
set this value to `0` for unpolarized measurements or `-1.8` for polarized experiments on HYSPEC.

EfCorrectionFunction
--------------------

This is the name of a function to apply to the data. Currently it is used to provide a correction for the transmission of the supermirror analyzer on HYSPEC. However, any function can be implemented, with a signature that takes a workspace handle and a data description. The input workspace of this function will be an event workspace, in units of energy transfer (just before converting to a multi-dimensional event workspace).
