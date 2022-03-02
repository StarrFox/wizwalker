# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "WizWalker"
copyright = "© Copyright 2020-present, StarrFox"
author = "StarrFox"

import re

with open("../pyproject.toml") as fp:
    version = re.search(
        r'\[tool.poetry]\nname = "\w+"\n(version ?= ?"([^"]+)")', fp.read()
    ).group(2)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "amunra_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_theme_options = {
    # Title shown in the top left. (Default: ``project`` value.)
    "navbar_title": "Wizwalker",
    # Links to shown in the top bar. (Default: top-level ``toctree`` entries.)
    "navbar_links": [
        ("Quickstart", "quickstart"),
        ("API", "api"),
        ("Memory objects", "memory_objects"),
        ("Index", "genindex"),
    ],
    "footer_text": "",
    # If ``github_link`` is set, a GitHub icon will be shown in the top right.
    "github_link": "https://github.com/StarrFox/wizwalker",
}
