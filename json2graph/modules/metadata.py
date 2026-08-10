"""Load metadata about the ontouml-json2graph software.

Metadata is loaded in one of two ways:
    (a) Automatically read from the pyproject.toml file.
    (b) Manually inserted.
"""

from importlib.metadata import PackageNotFoundError, metadata
from pathlib import Path
import re

from .logger import initialize_logger

LOGGER = initialize_logger()

global METADATA


def _read_source_project_version() -> str | None:
    """Return the Poetry project version when executing from a source checkout."""
    pyproject_file = Path(__file__).resolve().parents[2] / "pyproject.toml"
    if not pyproject_file.is_file():
        return None

    try:
        version_match = re.search(
            r'^version\s*=\s*["\']([^"\']+)["\']',
            pyproject_file.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
    except OSError:
        return None

    if version_match is None:
        return None
    return version_match.group(1)


SOURCE_PROJECT_VERSION = _read_source_project_version()

# Get software's metadata directly from pyproject.toml config file
try:
    METADATA = dict(metadata("ontouml-json2graph"))
# When developing, the metadata is not available and hence the information is manually declared
except PackageNotFoundError:
    LOGGER.warning("EXECUTING ON DEVELOPMENT MODE\n")
    METADATA = {
        "Summary": "OntoUML JSON2Graph Decoder",
        "Version": SOURCE_PROJECT_VERSION or "X.X.X",
        "Name": "ontouml-json2graph",
        "Home-page": "https://w3id.org/ontouml/json2graph",
    }

# A source checkout takes precedence over metadata from a separately installed
# distribution, which may be absent or stale in the development environment.
if SOURCE_PROJECT_VERSION is not None:
    METADATA["Version"] = SOURCE_PROJECT_VERSION

METADATA.setdefault("Home-page", "https://w3id.org/ontouml/json2graph")

# Manually including additional metadata
METADATA["conformsTo"] = "https://w3id.org/ontouml"
METADATA["conformsToBase"] = "https://w3id.org/ontouml#"
METADATA["conformsToVersion"] = "v1.1.1"
