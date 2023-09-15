""" Global variables definitions. """

from importlib.metadata import metadata

from json2graph.modules.logger import initialize_logger

global METADATA

LOGGER = initialize_logger()

# Software's metadata directly got from pyproject.toml config file
try:
    METADATA = dict(metadata("ontouml-json2graph"))

# When developing, the metadata is not available and hence the information is manually declared
except:
    LOGGER.warning("EXECUTING ON DEVELOPMENT MODE\n")
    METADATA = {
        "Summary": "(dev) OntoUML JSON2Graph Decoder",
        "Version": "(dev) 1.2.1",
        "Name": "(dev) ontouml-json2graph",
        "Home-page": "(dev) https://w3id.org/ontouml/json2graph",
    }

# GROUPS OF CONCEPTS

ELEMENT_VIEW_TYPES = [
    "ClassView",
    "PackageView",
    "GeneralizationSetView",
    "RelationView",
    "GeneralizationView",
    "NoteView",
]
