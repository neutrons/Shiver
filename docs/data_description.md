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
