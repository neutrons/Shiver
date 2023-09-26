Usage
=====

.. _installation:

Installation
------------

- Available as part of Mantid Workbench
- From source code with `pip` and conda environment configuration
- As a conda package: `Shiver <https://anaconda.org/neutrons/shiver>`

Application Information
-----------------------

``SHIVER`` is a desktop application for generating histograms from direct
geometry inelastic data related to spectroscopy event reduction. It is
built as a python package and can be used either as a standalone application
or as a package imported in Mantid workbench.

.. note::
    `Github Shiver Repository <https://github.com/neutrons/Shiver>`_

Technologies
------------

The project is written in Python (>=3.8). It is highly dependent on `Manitd <https://www.mantidproject.org>`_.
The Graphical User Interface (GUI) is based on `QtPy <https://github.com/spyder-ide/qtpy>`_ (version is defined by Mantid)


Project Structure
-----------------

The main code of the project is at src/shiver and the tests are at ``tests/``
folders. The project contains additional scripts at ``DGS_SC_scripts/`` folder,
which are initial scripts that ``SHIVER`` was created around.

The code follows the `MVP (Model-View-Presenter) <https://developer.mantidproject.org/MVPDesign.html>`_ Thus,
all current and future changes will follow this pattern.
