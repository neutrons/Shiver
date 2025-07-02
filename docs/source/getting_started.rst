Getting Started
===============

.. _getting_started:



Instructions for SHIVER development
-----------------------------------

Pixi Configuration
```````````````````
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

To start ``SHIVER`` from within the Mantid workbench, start ``mantidworkbench`` then run the following in the
``IPython`` console

.. code-block:: sh

    from shiver import Shiver
    s = Shiver()
    s.show()

**For Developers**

Any change to pyproject.toml, e.g. new dependencies, requires updating the pixi.lock file and including it in the commit.

```bash

pixi.lock

```

To run all tests for ``SHIVER``

.. code-block:: sh

    pytest
    #or
    python -m pytest

To run ``pre-commit`` manually

.. code-block:: sh

    pre-commit run --all-files

Or to set the ``pre-commit`` hook before each ``git`` commit

.. code-block:: sh

    pre-commit install
