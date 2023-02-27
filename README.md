# Shiver

This repository contains scripts to process single crystal inelastic data. The original work was done by
A. Savici (ORNL), I. Zaliznyak (BNL), March 2019. The idea is to separate data description, the 
slice/cut description and the main processing into different entities.

Data description is a list of dictionaries containing all the information required to process the raw
datafiles into a combined multi-dimensional workspace, in the reciprocal space associated with the goniometer,
in units of inverse Angstrom. Currently, the required files are the runs, the raw data folder, the name of
the output workspace, and the folder to save it.

The slice description is a list of dictionaries defining slices/cuts, to create a multi-dimensional histogram
in the reciprocal space of the sample, in reciprocal lattice units. `QDimenion0`, `QDimension1`, and `QDimension2`
define the projection axes. For example, `1,1,0` will correspond to `H,H,0` axis. Dimension names and binning
allow the user to select binning/integration ranges. Symmetry operations are allowed. The underlying Mantid
algorithm is [MDNorm](https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html), in case one needs
more information about the parameters. One can store information that can be used by matplotlib to make
the plots. The values corresponding to the `Plot_parameters` key will be passed directly to either the
[errobar](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.errorbar.html) function (for 1D plots)
or to [pcolormesh](https://matplotlib.org/api/_as_gen/matplotlib.axes.Axes.pcolormesh.html) function
(for the 2D plots). Keywords in `Axes_parameters` are parsed and applied to the axis objects (things like
`xrange`, `xtitle`, `aspect ratio`, or `grid`). Note that these can be overridden in the main program.

The main program is putting it all together. It will get the data definition. If the workspace with the name
in the definition is not already in memory, it will first try to load it from the disk, or, if unable, it will
create it. It will load the slice definitions. Then, one can choose to create a single pdf file to get all
the plots into it, or show them on the screen, or save the plots separately. The simplest example 
(slice_maker_example1.py) will just create a single plot and show it on the screen. For a more complicated example,
that puts multiple images in a single page, in a multi-page pdf document, please look at the 
slice_maker_example_polarized.py script.

The reduce_data_to_MDE.py and slice_utils.py scripts are used to create and plot the data. To download all these,
just clone the current git repository (it will create the `DGS_SC_scripts` subfolder):

```
git clone https://github.com/neutrons/Shiver.git
```

If one wants this to be done automatically by the autoreduction script, add the following to the end of 
`reduce_INSTRUMENT.py`:

```python
import os
import subprocess
from mantid.simpleapi import logger

output_dir = '/home/3y9/temp/' #this is the original output directory passed to the autoreduction script
output_scripts_dir = os.path.join(output_dir,'SCDGS_scripts')
cwd = os.getcwd()
# if folder is not there, clone the repository
cmd = 'git clone --depth 1 -b master https://github.com/AndreiSavici/DGS_SC_scripts.git {}'.format(output_scripts_dir)
if os.path.isdir(output_scripts_dir):
    #pull the latest version of the scripts
    os.chdir(output_scripts_dir)
    cmd = 'git pull --rebase'

proc = subprocess.Popen(cmd,
                        shell=True,
                        stdin=subprocess.PIPE,                               
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
out = proc.communicate()
rc = proc.returncode
if rc:
    logger.error('single crystal scripts: ' + out[1])
else:
    logger.notice('single crystal scripts: ' + out[0])
os.chdir(cwd)

```
