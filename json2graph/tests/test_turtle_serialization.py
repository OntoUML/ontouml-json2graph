"""Regression tests for whitespace-safe Turtle serialization."""

import json
from pathlib import Path

import pytest
from rdflib import Graph, Literal, Namespace, URIRef, XSD

from ..library import decode_json_project, save_graph_file
from ..modules.input_output import safe_write_graph_file

ONTOUML = Namespace("https://w3id.org/ontouml#")
BASE_URI = "https://example.org#"


def _has_physical_trailing_whitespace(text: str) -> bool:
    """Return whether any physical output line ends in a space or tab."""
    return any(line.endswith((" ", "\t")) for line in text.splitlines())


@pytest.mark.parametrize(
    "literal_value",
    [
        "A \nB",
        "A   \nB",
        "A\nB",
        "A \nB \nC",
        "A \r\nB",
    ],
)
@pytest.mark.parametrize("syntax", ["ttl", "turtle", "turtle2"])
def test_multiline_literals_are_whitespace_clean_and_lexically_preserved(
    tmp_path: Path,
    literal_value: str,
    syntax: str,
) -> None:
    """Preserve multiline lexical values without physical trailing whitespace."""
    subject = URIRef(BASE_URI + "subject")
    predicate = ONTOUML.description
    graph = Graph()
    graph.bind("ontouml", ONTOUML)
    graph.add((subject, predicate, Literal(literal_value)))

    output_file = tmp_path / f"output-{syntax}.ttl"
    safe_write_graph_file(graph, str(output_file), syntax)

    serialized = output_file.read_text(encoding="utf-8")
    assert not _has_physical_trailing_whitespace(serialized)

    parsed_graph = Graph().parse(output_file, format="turtle")
    assert set(parsed_graph.objects(subject, predicate)) == {Literal(literal_value)}


def test_multiline_literal_language_and_datatype_are_preserved(tmp_path: Path) -> None:
    """Keep language and datatype suffixes when multiline literals are escaped."""
    subject = URIRef(BASE_URI + "subject")
    language_predicate = URIRef(BASE_URI + "languageLiteral")
    datatype_predicate = URIRef(BASE_URI + "datatypeLiteral")
    graph = Graph()
    graph.add((subject, language_predicate, Literal("A \nB", lang="en")))
    graph.add((subject, datatype_predicate, Literal("A   \nB", datatype=XSD.string)))

    output_file = tmp_path / "output.ttl"
    safe_write_graph_file(graph, str(output_file), "ttl")

    serialized = output_file.read_text(encoding="utf-8")
    assert not _has_physical_trailing_whitespace(serialized)

    parsed_graph = Graph().parse(output_file, format="turtle")
    assert (subject, language_predicate, Literal("A \nB", lang="en")) in parsed_graph
    assert (subject, datatype_predicate, Literal("A   \nB", datatype=XSD.string)) in parsed_graph


def test_turtle_output_without_multiline_literals_matches_rdflib(tmp_path: Path) -> None:
    """Leave ordinary Turtle serialization unchanged."""
    subject = URIRef(BASE_URI + "subject")
    graph = Graph()
    graph.bind("ontouml", ONTOUML)
    graph.add((subject, ONTOUML.description, Literal("ordinary description")))

    expected = graph.serialize(format="turtle", encoding="utf-8")
    output_file = tmp_path / "output.ttl"
    safe_write_graph_file(graph, str(output_file), "ttl")

    assert output_file.read_bytes() == expected


def test_multiline_turtle_serialization_is_deterministic(tmp_path: Path) -> None:
    """Produce identical Turtle bytes for repeated serialization of the same graph."""
    graph = Graph()
    graph.bind("ontouml", ONTOUML)
    graph.add((URIRef(BASE_URI + "subject"), ONTOUML.description, Literal("A \nB \nC")))

    first_output = tmp_path / "first.ttl"
    second_output = tmp_path / "second.ttl"
    safe_write_graph_file(graph, str(first_output), "ttl")
    safe_write_graph_file(graph, str(second_output), "ttl")

    assert first_output.read_bytes() == second_output.read_bytes()


def test_json_description_round_trips_without_physical_trailing_whitespace(tmp_path: Path) -> None:
    """Reproduce the catalog incident through the public decode/save API."""
    literal_value = "A   \nB \nC"
    input_file = tmp_path / "multiline-description.json"
    input_file.write_text(
        json.dumps(
            {
                "id": "project-1",
                "type": "Project",
                "name": "Example",
                "description": literal_value,
                "model": {
                    "id": "package-1",
                    "type": "Package",
                    "name": "Model",
                    "contents": [],
                },
            }
        ),
        encoding="utf-8",
    )

    graph = decode_json_project(str(input_file), base_uri=BASE_URI)
    output_file = tmp_path / "output.ttl"
    save_graph_file(graph, str(output_file), "ttl")

    serialized = output_file.read_text(encoding="utf-8")
    assert not _has_physical_trailing_whitespace(serialized)

    parsed_graph = Graph().parse(output_file, format="turtle")
    assert (URIRef(BASE_URI + "project-1"), ONTOUML.description, Literal(literal_value)) in parsed_graph
