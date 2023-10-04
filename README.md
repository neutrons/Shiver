# Shiver

Tool (desktop application) for allowing the examination of Time of Flight (ToF) inelastic neutron data, from single crystal, direct geometry experiments.

## Installation

Create and activate conda environment for shiver development

```bash
conda env create
# or
mamba env create

conda activate shiver
```

Install shiver (in editable mode) and start application

```bash
python -m pip install -e .

shiver
```

To start shiver from within the Mantid workbench, start
`mantidworkbench` then run the following in the `IPython` console

```python
from shiver import Shiver
s=Shiver()
s.show()
```

## For Contributors

**Testing**

---

To run all tests for shiver
```bash
pytest
#or
python -m pytest
```

To run pre-commit manually
```bash
pre-commit run --all-files
```
Or

To set the pre-commit hook before each git commit
```bash
pre-commit install
```

**Automated Jobs**

---

The repository runs automated tests on branches during Pull-Requests and on the main ones: next, main and qa. The jobs are described in .github/workflows/actions.yml:
  * `Tests`. It includes pytest, pre-commit and code coverage tools

  * `Conda build`. A new conda package is built and uploaded to Anaconda, depending upon git tags and authorized branches.

  * `Trigger deploy`. Given that the two above jobs were successful, deployment is triggered.


**Documentation Updates**

---

When adding new views, presenters and methods, please navigate to docs/source/repo_doc.rst. Add the new feature under the appropriate section following the given template:

```bash
.. automodule:: path.to.new.module
   :members:
```

Once complete, rebuild the documentation:

    cd SHIVER/docs/
    make clean
    make html


---

## Code Documentation

https://shiver.readthedocs.io/en/latest/

---

[![CI](https://github.com/neutrons/Shiver/actions/workflows/actions.yml/badge.svg?branch=next)](https://github.com/neutrons/Shiver/actions/workflows/actions.yml)
[![codecov](https://codecov.io/gh/neutrons/shiver/branch/next/graph/badge.svg?token=J1ZNHXF6Ml)](https://codecov.io/gh/neutrons/shiver)
[![OpenSSF Best Practices](https://bestpractices.coreinfrastructure.org/projects/7381/badge)](https://bestpractices.coreinfrastructure.org/projects/7381)
