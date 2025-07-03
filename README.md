# Shiver

Tool (desktop application) for allowing the examination of Time of Flight (ToF) inelastic neutron data, from single crystal, direct geometry experiments.

## Installation

Create and activate a virtual environment with [Pixi](https://pixi.sh/).
Prerequisites: Pixi installation e.g. for Linux:

```bash
curl -fsSL https://pixi.sh/install.sh | sh

```

Download the repository. Setup/Update the environment

```bash
pixi install
```

Enter the environment

```bash
pixi shell

```

The Shiver environment is activated and the application is ready to use.

Start the application

```bash
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

**Development/Deployment**


---

Any change to pyproject.toml, e.g. new dependencies, requires updating the pixi.lock file and including it in the commit.

```bash

pixi.lock

```

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
  * `Testing suite`. It includes pytest, pre-commit and code coverage tools

  * `Conda build`. A new conda package is built and uploaded in a github temporary location (servers).

  * `Conda Verify`. The new conda package is installed in a test environment and checked, e.g. import shiver.

  * `Publish`. The new conda package is uploaded in Anaconda Neutrons registry.

  * `Trigger deploy`. Given that the two above jobs were successful, deployment is triggered. (this is temporarily in comments)


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
