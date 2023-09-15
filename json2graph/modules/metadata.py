""" Load metadata about the ontouml-json2graph software.

Metadata is loaded in one of two ways:
    (a) Automatically read from the pyproject.toml file.
    (b) Manually inserted.
"""

from importlib.metadata import metadata

from json2graph.modules.logger import initialize_logger

LOGGER = initialize_logger()

global METADATA

# Get software's metadata directly from pyproject.toml config file
try:
    METADATA = dict(metadata("ontouml-json2graph"))
# When developing, the metadata is not available and hence the information is manually declared
except ModuleNotFoundError:
    LOGGER.warning("EXECUTING ON DEVELOPMENT MODE\n")
    METADATA = {
        "Summary": "OntoUML JSON2Graph Decoder",
        "Version": "X.X.X",
        "Name": "ontouml-json2graph",
        "Home-page": "https://w3id.org/ontouml/json2graph",
    }

# Manually including additional metadata
METADATA["conformsTo"] = "https://w3id.org/ontouml"
METADATA["conformsToBase"] = "https://w3id.org/ontouml#"
METADATA["conformsToVersion"] = "v1.1.0"
