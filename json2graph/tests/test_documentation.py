"""Validate generated references and executable documentation examples."""

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from rdflib import RDF, Graph, Namespace

from update_documentation import CLI_REFERENCE_RELATIVE_PATH, render_cli_help

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIRECTORY = REPOSITORY_ROOT / "docs" / "examples"
ONTOUML = Namespace("https://w3id.org/ontouml#")


def assert_minimal_project_graph(graph_file: Path) -> None:
    """Assert that a serialized graph contains the canonical project's core resources."""
    graph = Graph()
    graph.parse(graph_file, format="turtle")

    assert any(graph.triples((None, RDF.type, ONTOUML.Project)))
    assert any(graph.triples((None, RDF.type, ONTOUML.Package)))
    assert any(graph.triples((None, RDF.type, ONTOUML.Class)))


def copy_canonical_example(destination: Path) -> None:
    """Copy the canonical input into an isolated execution directory."""
    shutil.copy(EXAMPLES_DIRECTORY / "minimal-project.json", destination / "minimal-project.json")


def test_cli_reference_matches_current_parser() -> None:
    """Require the checked-in CLI reference to match the current parser help."""
    reference_file = REPOSITORY_ROOT / CLI_REFERENCE_RELATIVE_PATH
    assert reference_file.read_text(encoding="utf-8") == render_cli_help(REPOSITORY_ROOT)


def test_canonical_cli_example(tmp_path: Path) -> None:
    """Execute the exact CLI command included by Sphinx and validate its output."""
    copy_canonical_example(tmp_path)
    command = shlex.split((EXAMPLES_DIRECTORY / "cli-usage.txt").read_text(encoding="utf-8"))
    assert command[:3] == ["python", "-m", "json2graph.decode"]
    command[0] = sys.executable

    subprocess.run(command, cwd=tmp_path, check=True, capture_output=True, text=True)

    assert_minimal_project_graph(tmp_path / "output" / "minimal-project.ttl")


def test_canonical_library_example(tmp_path: Path) -> None:
    """Execute the exact library program included by Sphinx and validate its output."""
    copy_canonical_example(tmp_path)
    example_program = tmp_path / "library-usage.py"
    shutil.copy(EXAMPLES_DIRECTORY / "library-usage.py", example_program)

    subprocess.run([sys.executable, example_program.name], cwd=tmp_path, check=True, capture_output=True, text=True)

    assert_minimal_project_graph(tmp_path / "minimal-project.ttl")
