"""OntoUML JSON2Graph Test Module.

This module contains test functions to verify the correctness of the OntoUML JSON2Graph software.
The tests are based on the comparison of the generated graph (from OntoUML JSON files provided in the test folder)
with the expected resulting graph stored in Turtle (.ttl) files (also provided in the test folder).

The module uses a list of test files (`LIST_OF_TESTS`) retrieved from the function `get_test_list()`.
Each test file is a valid OntoUML JSON file representing a model.

The comparison of graphs is done using the function `compare_graphs`, which should be defined and available
for the tests to run successfully.

The tests will ensure the correct functioning of the OntoUML JSON2Graph software and raise an assertion error
if the generated graph does not match the expected graph.
"""

from pathlib import Path

import pytest
from rdflib import RDF, Graph, Literal, Namespace, URIRef

from .test_aux import compare_graphs, get_test_list
from ..decode import decode_ontouml_json2graph, write_graph_file
from ..library import decode_json_model

LIST_OF_TESTS = get_test_list()

BASE_URI = "https://example.org#"
ONTOUML = Namespace("https://w3id.org/ontouml#")
ENUMERATION_INPUT_FILE = str(Path(__file__).parent / "test_files" / "test_028.json")
ENUMERATION_CLASS = URIRef(BASE_URI + "olObZJGFYGjgAQ2v")
NON_ENUMERATION_CLASS = URIRef(BASE_URI + "Q4hbZJGFYGjgAQ3M")
ENUMERATION_LITERALS = {
    "ymXbZJGFYGjgAQ31": "literal1",
    "lB3bZJGFYGjgAQ34": "literal2",
    "zv3bZJGFYGjgAQ37": "literal3",
    "gSPbZJGFYGjgAQ3": "literal4",
}


def assert_enumeration_literals_preserved(ontouml_graph: Graph) -> None:
    """Assert that model-only decoding preserves enumeration literals and their data."""
    expected_literal_uris = {URIRef(BASE_URI + literal_id) for literal_id in ENUMERATION_LITERALS}

    assert (ENUMERATION_CLASS, RDF.type, ONTOUML.Class) in ontouml_graph
    assert set(ontouml_graph.objects(ENUMERATION_CLASS, ONTOUML.literal)) == expected_literal_uris

    for literal_id, literal_name in ENUMERATION_LITERALS.items():
        literal_uri = URIRef(BASE_URI + literal_id)

        assert (literal_uri, RDF.type, ONTOUML.Literal) in ontouml_graph
        assert (literal_uri, ONTOUML.name, Literal(literal_name)) in ontouml_graph

    described_literal = URIRef(BASE_URI + "lB3bZJGFYGjgAQ34")
    assert (described_literal, ONTOUML.description, Literal("test description literal")) in ontouml_graph
    assert not any(ontouml_graph.triples((NON_ENUMERATION_CLASS, ONTOUML.literal, None)))


def assert_diagrammatic_elements_removed(ontouml_graph: Graph) -> None:
    """Assert that model-only decoding continues to remove diagrammatic elements."""
    diagrammatic_types = [
        ONTOUML.Diagram,
        ONTOUML.ClassView,
        ONTOUML.GeneralizationView,
        ONTOUML.Rectangle,
        ONTOUML.Path,
        ONTOUML.Point,
    ]

    for diagrammatic_type in diagrammatic_types:
        assert not any(ontouml_graph.triples((None, RDF.type, diagrammatic_type)))


@pytest.mark.parametrize("input_file", LIST_OF_TESTS)
def test_ontouml_json2graph(input_file: str) -> None:
    """Main test function the OntoUML JSON2Graph software.

    The test is based on the comparison of the generated graph (from OntoUML JSON files provided in the test folder)
    with an expected resulting graph (also provided in the test folder), always in 'ttl' format.

    :param input_file: Path to the JSON file to be tested.
    :type input_file: str
    """
    test_name = Path(input_file).stem

    # Test with language starts on file test_042
    language = "en" if (int(test_name[-2:]) > 41) else ""

    # Create resulting Graph in ttl syntax
    resulting_graph = decode_ontouml_json2graph(json_file_path=input_file, language=language, execution_mode="test")
    resulting_graph_file = write_graph_file(ontouml_graph=resulting_graph, execution_mode="test")

    # Getting expected result
    expected_graph_file = input_file.replace(".json", ".ttl")

    # Comparing resulting and expected graphs
    is_equal = compare_graphs(resulting_graph_file, expected_graph_file, test_name)

    assert is_equal


def test_model_only_preserves_enumeration_literals() -> None:
    """Verify that model-only decoding preserves literals while removing diagrammatic elements."""
    ontouml_graph = decode_ontouml_json2graph(
        json_file_path=ENUMERATION_INPUT_FILE,
        model_only=True,
        execution_mode="import",
    )

    assert_enumeration_literals_preserved(ontouml_graph)
    assert_diagrammatic_elements_removed(ontouml_graph)


def test_decode_json_model_preserves_enumeration_literals() -> None:
    """Verify that the public model-decoding API preserves enumeration literals."""
    ontouml_graph = decode_json_model(json_file_path=ENUMERATION_INPUT_FILE)

    assert_enumeration_literals_preserved(ontouml_graph)
