"""Validate generated references and executable documentation examples."""

import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from rdflib import RDF, Graph, Namespace

from json2graph.library import decode_json_model, decode_json_project
from json2graph.modules.path_order import PathPointOrderWarning

from update_documentation import CLI_REFERENCE_RELATIVE_PATH, render_cli_help

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIRECTORY = REPOSITORY_ROOT / "docs" / "examples"
ONTOUML = Namespace("https://w3id.org/ontouml#")
PROV = Namespace("http://www.w3.org/ns/prov#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
CATALOG_JSON = EXAMPLES_DIRECTORY / "catalog" / "genealogy2013.json"


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


def copy_catalog_example(destination: Path) -> None:
    """Copy the catalog input while retaining the documented relative path."""
    catalog_directory = destination / "catalog"
    catalog_directory.mkdir()
    shutil.copy(CATALOG_JSON, catalog_directory / "genealogy2013.json")


def run_catalog_cli(destination: Path, *options: str) -> subprocess.CompletedProcess[str]:
    """Run a documented catalog command from the examples working directory."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            "catalog/genealogy2013.json",
            "-o",
            "output",
            *options,
            "--silent",
        ],
        cwd=destination,
        check=True,
        capture_output=True,
        text=True,
    )


def assert_catalog_model(graph: Graph) -> None:
    """Check representative named resources without relying on Turtle ordering."""
    person = next(
        subject
        for subject in graph.subjects(RDF.type, ONTOUML.Class)
        if any(str(name) == "Person" for name in graph.objects(subject, ONTOUML.name))
    )
    assert (person, ONTOUML.stereotype, ONTOUML.kind) in graph
    assert any(
        str(name) == "parentOf"
        for relation in graph.subjects(RDF.type, ONTOUML.Relation)
        for name in graph.objects(relation, ONTOUML.name)
    )


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


def test_catalog_model_only_cli_example(tmp_path: Path) -> None:
    """Execute the documented model-only recipe on the complete catalog JSON."""
    copy_catalog_example(tmp_path)
    result = run_catalog_cli(tmp_path, "--model_only")

    assert "PathPointOrderWarning" not in result.stderr
    graph = Graph().parse(tmp_path / "output" / "genealogy2013.ttl", format="turtle")
    assert_catalog_model(graph)
    for resource_type in (ONTOUML.Project, ONTOUML.Package, ONTOUML.Diagram, ONTOUML.ClassView, ONTOUML.Path):
        assert not any(graph.subjects(RDF.type, resource_type))


def test_catalog_complete_project_and_model_scope() -> None:
    """Compare graph scope and capture the expected path-order warning."""
    with pytest.warns(PathPointOrderWarning, match="ordered point sequences"):
        complete_graph = decode_json_project(str(CATALOG_JSON))
    model_graph = decode_json_model(str(CATALOG_JSON))

    assert_catalog_model(complete_graph)
    assert_catalog_model(model_graph)
    for resource_type in (
        ONTOUML.Project,
        ONTOUML.Package,
        ONTOUML.Diagram,
        ONTOUML.ClassView,
        ONTOUML.RelationView,
        ONTOUML.Path,
        ONTOUML.Point,
    ):
        assert any(complete_graph.subjects(RDF.type, resource_type))
        assert not any(model_graph.subjects(RDF.type, resource_type))


def test_catalog_complete_project_cli_warning(tmp_path: Path) -> None:
    """Even with --silent, the complete CLI recipe writes RDF and warns about path order."""
    copy_catalog_example(tmp_path)
    result = run_catalog_cli(tmp_path)

    assert "PathPointOrderWarning" in result.stderr
    graph = Graph().parse(tmp_path / "output" / "genealogy2013.ttl", format="turtle")
    assert_catalog_model(graph)
    assert any(graph.subjects(RDF.type, ONTOUML.Diagram))


def test_catalog_explicit_base_uri() -> None:
    """The documented Python URI option places model resources under that base."""
    graph = decode_json_model(str(CATALOG_JSON), base_uri="https://example.org/genealogy#")

    assert_catalog_model(graph)
    assert all(
        str(subject).startswith("https://example.org/genealogy#") for subject in graph.subjects(RDF.type, ONTOUML.Class)
    )


def test_catalog_provenance_sidecar_cli_example(tmp_path: Path) -> None:
    """The documented CLI option writes separate, parseable model and provenance graphs."""
    copy_catalog_example(tmp_path)
    run_catalog_cli(tmp_path, "--model_only", "--transformation-metadata", "sidecar")

    output_directory = tmp_path / "output"
    model_graph = Graph().parse(output_directory / "genealogy2013.ttl", format="turtle")
    provenance_graph = Graph().parse(output_directory / "genealogy2013.provenance.ttl", format="turtle")
    assert_catalog_model(model_graph)
    assert any(provenance_graph.subjects(RDF.type, PROV.Activity))
    assert any(str(title) == "genealogy2013.json" for title in provenance_graph.objects(None, DCTERMS.title))
