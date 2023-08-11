Getting Started
===============

.. _getting_started:



Instructions for SHIVER development
-----------------------------------

Conda Configuration
```````````````````
Create and activate conda environment for ``SHIVER``.

.. code-block:: sh

    conda env create --file environment.yml
    # or
    mamba env create --file environment.yml

    conda activate shiver

Install ``SHIVER`` (in `editable mode <https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e>`_) and start application

.. code-block:: sh

    python -m pip install -e .

    shiver

If it has been a while, once can update using

.. code-block:: sh

    conda activate shiver
    conda env update --file environment.yml --prune

To start ``SHIVER`` from within the Mantid workbench, start ``mantidworkbench`` then run the following in the
``IPython`` console

.. code-block:: sh

    from shiver import Shiver
    s = Shiver()
    s.show()

**For Developers**

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
