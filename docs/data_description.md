---
layout: default
---
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

Parameters
==========

Runs
----

The runs are a list (or any iterable) of run numbers or a list of run numbers. Together with the `RawDataFolder` parameter, 
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

RawDataFolder
-------------

The folder where the raw data (.nxs.h5) files are located.

MdeName
-------

The name of the intermediate dataset. This is a [Mantid](https://mantidproject.org) mutlidimensional event workspace.

MdeFolder
---------

The storage location for the intermediate dataset.



