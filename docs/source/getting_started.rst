Getting Started
===============

.. _getting_started:


Instructions for SHIVER development
-----------------------------------

Pixi Configuration
```````````````````
Create and activate a virtual environment with [Pixi](https://pixi.sh/).
Prerequisites: Pixi installation e.g. for Linux:

.. code-block:: bash

    curl -fsSL https://pixi.sh/install.sh | sh

Download the repository. Setup/Update the environment

.. code-block:: bash

    pixi install

Enter the environment

.. code-block:: bash

    pixi shell

The Shiver environment is activated and the application is ready to use.

Start the application

.. code-block:: bash

    shiver

To start ``SHIVER`` from within the Mantid workbench, start ``mantidworkbench`` then run the following in the
``IPython`` console

.. code-block:: bash

    from shiver import Shiver
    s = Shiver()
    s.show()

**For Developers**

Any change to pyproject.toml, e.g. new dependencies, requires updating the pixi.lock file and including it in the commit.

.. code-block:: bash

    pixi lock

List the pixi tasks that can run on the machine

```bash
pixi task list

```

To run all tests for ``SHIVER``

.. code-block:: bash

    pytest
    #or
    python -m pytest

To run ``pre-commit`` manually

.. code-block:: bash

    pre-commit run --all-files

Or to set the ``pre-commit`` hook before each ``git`` commit

.. code-block:: bash

    pre-commit install
