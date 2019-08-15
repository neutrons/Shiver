# DGS_SC_scripts
scripts to process single crystal inelastic data

for autoreduction add the following to the script:

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
