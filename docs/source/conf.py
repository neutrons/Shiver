"""
Purpose: A Python script holding the configuration of the project. Contains the project
name and release information as well as some extra configuration keys.
"""

import os
import sys
import versioningit


sys.path.insert(0, os.path.abspath("../../"))

# Configuration file for the Sphinx documentation builder.

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "SHIVER"  # pylint: disable=C0103
copyright = "2023, ORNL"  # pylint: disable=W0622, C0103
author = "ORNL"  # pylint: disable=C0103
version = versioningit.get_version("../../")
release = ".".join(version.split(".")[:-1])  # pylint: disable=C0103

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

autodoc_mock_imports = [
    "mantid",
    "mantid.kernel",
    "mantid.utils",
    "mantid.utils.logging",
    "mantid.simpleapi",
    "mantid.geometry",
    "mantidqt.widgets",
    "mantidqt.widgets.algorithmprogress",
    "qtpy",
    "qtpy.uic",
    "qtpy.QtWidgets",
    "mantidqt",
    "mantid.plots",
    "mantid.plots.plotfunctions",
    "mantid.plots.datafunctions",
    "mantid.plots.utility",
]


intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"  # pylint: disable=C0103

html_theme_options = {"style_nav_header_background": "#472375"}

epub_show_urls = "footnote"  # pylint: disable=C0103
