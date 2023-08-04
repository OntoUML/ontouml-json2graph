""" Global variables definitions. """
import os

import yaml

from .errors import report_error_io_read

# Software's metadata from resources/metadata.yaml (indirectly got from pyproject.toml config file)
global METADATA

# Guarantees that the file will be found as it searches using this file as basis
package_dir = os.path.dirname(os.path.dirname(__file__))
metadata_file = os.path.join(package_dir, "resources\metadata.yaml")

# Loads metadata_file into a dictionary
try:
    with open(metadata_file) as file:
        metadata_dictionary = yaml.safe_load(file)
except IOError as error:
    file_description = "Metadata file could not be loaded."
    report_error_io_read(metadata_file, file_description, error)

METADATA = metadata_dictionary["tool"]["poetry"] | metadata_dictionary["extras"]

# GROUPS OF CONCEPTS

ELEMENT_VIEW_TYPES = ["ClassView", "PackageView", "GeneralizationSetView", "RelationView", "GeneralizationView",
                      "NoteView"]
