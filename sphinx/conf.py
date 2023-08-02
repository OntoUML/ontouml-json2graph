# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ontouml-json2graph'
copyright = '2023, Semantics, Cybersecurity & Services (SCS), University of Twente, the Netherlands'
author = 'Pedro Paulo F. Barcelos (p.p.favatobarcelos@utwente.nl)'
release = '2023.08.02'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
                "autoapi.extension",
                "myst_parser",
                "sphinx.ext.autosectionlabel",
                "sphinx.ext.autosummary",
                "sphinx.ext.coverage",
                "sphinx.ext.doctest",
                "sphinx.ext.githubpages",
                "sphinx_toolbox.shields",
                "sphinx_toolbox.sidebar_links",
            ]

autodoc_typehints = 'description'
github_username = "pedropaulofb"
github_repository = "ontouml/ontouml-json2graph"

autoapi_dirs = [
    '../json2graph/',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
html_logo = "../json2graph/resources/logo-json2graph.png"
html_theme_options = {
    'display_version': True
}