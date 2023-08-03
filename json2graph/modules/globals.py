""" Global variables definitions. """
from os.path import exists
from pprint import pprint

import toml as toml

# Software's metadata got from pyproject.toml config file
global METADATA

pyproject_file = "pyproject.toml"
pyproject_path_prod = "./" + pyproject_file
pyproject_path_test = "../" + pyproject_file
pyproject_path = pyproject_path_prod if exists(pyproject_file) else pyproject_path_test

metadata_project = toml.load(pyproject_path)
METADATA = metadata_project["tool"]["poetry"] | metadata_project["extras"]

# URIs
URI_ONTOUML = "https://w3id.org/ontouml#"

# GROUPS OF CONCEPTS

ELEMENT_VIEW_TYPES = ["ClassView", "PackageView", "GeneralizationSetView", "RelationView", "GeneralizationView",
                      "NoteView"]
