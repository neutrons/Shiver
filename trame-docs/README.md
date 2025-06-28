# Shiver Trame Migration: A Developer's Guide

This document provides an overview of the recent migration of the Shiver application's user interface from PyQt to [Trame](https://trame.readthedocs.io/en/latest/). It is intended for developers who may be unfamiliar with Trame and need to understand the new architecture, build process, and how to run the application.

## Summary of Work

The primary goal of this migration was to replace the existing PyQt-based View layer with a modern, web-based UI powered by Trame. This was achieved while preserving the existing Model-View-Presenter (MVP) architecture, which significantly streamlined the migration process.

The core of the work involved the following steps for each major UI component (Configuration, Sample, Generate, Histogram, Corrections, Refine UB, and Polarized):

1.  **Analysis**: The interactions between the existing PyQt `View` and its corresponding `Presenter` were carefully analyzed to define a clear "API" for the new Trame-based view.

2.  **Adapter Creation**: For each component, a `Trame...ViewAdapter` class was created. This adapter acts as a bridge, mimicking the interface of the old PyQt view. This allowed the `Presenter` and `Model` layers to remain largely unchanged, as they continue to interact with what they perceive as a traditional view object.

3.  **Trame UI Implementation**: The UI for each component was rebuilt using Trame's declarative syntax with Vuetify components. These new UI components are located in the `src/shiver/trame_app/` directory.

4.  **State Management**: Instead of directly manipulating UI widgets (as in PyQt), the `ViewAdapter` now modifies a central `state` dictionary managed by Trame. Changes to this `state` are automatically synchronized with the web UI, providing a reactive and modern user experience.

5.  **Dialogs for Temporary Views**: UI components that were previously implemented as temporary tabs (like "Corrections" and "Refine UB") have been migrated to dialogs that are launched from the main application interface. This provides a more intuitive and less cluttered user experience.

## Build Steps

There are no traditional "build" steps required to run the Trame application. Unlike compiled languages, Python applications with Trame are run directly from the source code.

However, it is essential to have the correct dependencies installed. The required dependencies, including `trame` and `trame-vuetify`, have been added to the `environment.yml` file. To set up your environment, please follow these steps:

1.  **Install Conda**: If you don't have Conda installed, please follow the instructions on the [official Conda website](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

2.  **Create the Conda Environment**: Open a terminal or command prompt, navigate to the root of the Shiver project, and run the following command:

    ```bash
    conda env create -f environment-trame.yml
    ```

    This will create a new Conda environment named `shiver` with all the necessary dependencies.

3.  **Activate the Environment**: Before running the application, you must activate the `shiver` environment:

    ```bash
    conda activate shiver
    pip install trame
    pip install trame-vuetify
    pip install trame-plotly
    ```

## How to Start the Application

With the `shiver` Conda environment activated, you can start the Trame application by running the following command from the root of the project:

```bash
python run_trame.py
```

The `run_trame.py` script has been configured to automatically add the `src` directory to the Python path, so it can be run directly from the project root.

This will start a local web server. You can then access the Shiver application by opening a web browser and navigating to the URL provided in the terminal output (usually `http://127.0.0.1:8080`).

The application will open in your browser with a tabbed interface, allowing you to interact with the various components of the Shiver application.
