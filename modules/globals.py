""" Global variables definitions. """
import toml as toml

# Software's metadata
global METADATA
metadata_project = toml.load("../pyproject.toml")
METADATA = metadata_project["project"]

# URIs
URI_ONTOUML = "https://w3id.org/ontouml#"

# GROUPS OF CONCEPTS

ELEMENT_VIEW_TYPES = ["ClassView", "PackageView", "GeneralizationSetView", "RelationView", "GeneralizationView",
                      "NoteView"]
