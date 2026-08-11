"""Sphinx configuration for ontouml-json2graph."""

import os
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - used only on Python 3.10
    import tomli as tomllib


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.fspath(REPOSITORY_ROOT))

with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as pyproject_file:
    project_metadata = tomllib.load(pyproject_file)["project"]

project = "ontouml-json2graph"
author = "Pedro Paulo Favato Barcelos"
copyright = "2023–2026, OntoUML developers and maintainers at the SCS group, University of Twente"
release = project_metadata["version"]
version = ".".join(release.split(".")[:2])

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.githubpages",
]

autodoc_typehints = "description"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
nitpicky = True
nitpick_ignore = [
    ("py:class", "Graph"),  # Third-party RDFLib return type referenced by existing public docstrings.
]
root_doc = "index"
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}

html_theme = "sphinx_rtd_theme"
html_logo = "../json2graph/resources/logo-json2graph-reduced.png"
html_title = f"{project} {release} documentation"
