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

PROJECT = "SHIVER"
COPYRIGHT = "2022, ORNL"
AUTHOR = "ORNL"
VERSION = versioningit.get_version("../../")
RELEASE = ".".join(VERSION.split(".")[:-1])

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
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

HTML_THEME = "sphinx_rtd_theme"

html_theme_options = {"style_nav_header_background": "#472375"}

EPUB_SHOW_URLS = "footnote"
