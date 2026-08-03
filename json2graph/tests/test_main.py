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

import json
import subprocess
import sys
import warnings
from pathlib import Path

import pytest
from rdflib import RDF, Graph, Literal, Namespace, URIRef

from .test_aux import compare_graphs, get_test_list
from ..decode import decode_ontouml_json2graph, write_graph_file
from ..library import decode_json_model
from ..modules.input_output import JSONEncodingFallbackWarning, safe_load_json_file
from ..modules.stereotypes import (
    InvalidStereotypeError,
    InvalidStereotypeWarning,
    StereotypeNormalizationWarning,
    normalize_stereotype,
    set_stereotype_relation,
)

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


def write_invalid_stereotype_project(tmp_path: Path, stereotype: str = "abstract individual") -> Path:
    """Write a minimal project containing one invalid Class stereotype assignment."""
    input_file = tmp_path / "invalid-stereotype.json"
    input_file.write_text(
        json.dumps(
            {
                "id": "project-1",
                "type": "Project",
                "name": "Example",
                "model": {
                    "id": "package-1",
                    "type": "Package",
                    "name": "Model",
                    "contents": [
                        {
                            "id": "class-1",
                            "type": "Class",
                            "name": "Example",
                            "stereotype": stereotype,
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    return input_file


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


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_safe_load_json_file_preserves_supported_source_encodings(
    tmp_path: Path,
    encoding: str,
) -> None:
    """Verify that supported source encodings preserve the same JSON data."""
    expected_json = {
        "id": "project-1",
        "type": "Project",
        "name": "Integração €",
    }
    input_file = tmp_path / f"project-{encoding}.json"
    input_file.write_bytes(json.dumps(expected_json, ensure_ascii=False).encode(encoding))

    if encoding == "cp1252":
        with pytest.warns(JSONEncodingFallbackWarning, match="loaded using CP1252"):
            loaded_json = safe_load_json_file(str(input_file))
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("error", JSONEncodingFallbackWarning)
            loaded_json = safe_load_json_file(str(input_file))

    assert loaded_json == expected_json


@pytest.mark.parametrize(
    ("stereotype", "expected"),
    [
        ("abstract individual", "abstractIndividual"),
        ("quality-structure", "qualityStructure"),
        ("historicalRole", "historicalRole"),
        ("Agent", "agent"),
        ("CMP", "cmp"),
    ],
)
def test_stereotypes_are_normalized_to_lower_camel_case(stereotype: str, expected: str) -> None:
    """Verify deterministic lowerCamelCase normalization of stereotype values."""
    assert normalize_stereotype(stereotype) == expected


@pytest.mark.parametrize(
    ("policy", "expected_stereotype", "expected_exception"),
    [
        ("preserve", ONTOUML.abstractIndividual, None),
        ("omit", None, None),
        ("error", None, InvalidStereotypeError),
    ],
)
def test_invalid_stereotype_policy(
    policy: str,
    expected_stereotype: URIRef | None,
    expected_exception: type[Exception] | None,
) -> None:
    """Verify preserve, omit, and error handling for a nonexistent stereotype."""
    element = {
        "id": "element-1",
        "type": "Class",
        "name": "Example",
        "stereotype": "abstract individual",
    }
    ontouml_graph = Graph()

    if expected_exception is not None:
        with pytest.raises(expected_exception, match="Transformation aborted"):
            set_stereotype_relation(element, ontouml_graph, policy, BASE_URI)
    else:
        with pytest.warns(InvalidStereotypeWarning, match=f"policy is '{policy}'"):
            set_stereotype_relation(element, ontouml_graph, policy, BASE_URI)

    element_uri = URIRef(BASE_URI + element["id"])
    mapped_stereotypes = set(ontouml_graph.objects(element_uri, ONTOUML.stereotype))

    if expected_stereotype is None:
        assert mapped_stereotypes == set()
    else:
        assert mapped_stereotypes == {expected_stereotype}

    ontouml_graph.serialize(format="turtle")


@pytest.mark.parametrize(
    ("element_type", "stereotype", "recognized_element_type"),
    [
        ("Class", "participation", "Relation"),
        ("Relation", "kind", "Class"),
        ("Property", "material", "Relation"),
    ],
)
@pytest.mark.parametrize(
    ("policy", "expected_stereotype", "expected_exception"),
    [
        ("preserve", True, None),
        ("omit", False, None),
        ("error", False, InvalidStereotypeError),
    ],
)
def test_wrong_element_type_applies_invalid_stereotype_policy(
    element_type: str,
    stereotype: str,
    recognized_element_type: str,
    policy: str,
    expected_stereotype: bool,
    expected_exception: type[Exception] | None,
) -> None:
    """Verify policy handling when a recognized stereotype is assigned to the wrong element type."""
    element = {
        "id": "element-1",
        "type": element_type,
        "name": "Example",
        "stereotype": stereotype,
    }
    ontouml_graph = Graph()

    if expected_exception is not None:
        with pytest.raises(expected_exception, match=f"not valid for {element_type}"):
            set_stereotype_relation(element, ontouml_graph, policy, BASE_URI)
    else:
        with pytest.warns(
            InvalidStereotypeWarning,
            match=rf"recognized for {recognized_element_type}, but not for {element_type}",
        ):
            set_stereotype_relation(element, ontouml_graph, policy, BASE_URI)

    element_uri = URIRef(BASE_URI + element["id"])
    mapped_stereotypes = set(ontouml_graph.objects(element_uri, ONTOUML.stereotype))

    if expected_stereotype:
        assert mapped_stereotypes == {ONTOUML[stereotype]}
    else:
        assert mapped_stereotypes == set()


@pytest.mark.parametrize(
    ("element_type", "stereotype", "canonical_stereotype"),
    [
        ("Class", "Role", "role"),
        ("Class", "Kind", "kind"),
        ("Relation", "Material", "material"),
        ("Property", "Begin", "begin"),
    ],
)
@pytest.mark.parametrize("policy", ["preserve", "omit", "error"])
def test_valid_lexical_variant_emits_canonical_stereotype_with_warning(
    element_type: str,
    stereotype: str,
    canonical_stereotype: str,
    policy: str,
) -> None:
    """Verify that valid lexical variants are normalized, warned about, and emitted under every policy."""
    element = {
        "id": "element-1",
        "type": element_type,
        "name": "Example",
        "stereotype": stereotype,
    }
    ontouml_graph = Graph()

    with pytest.warns(StereotypeNormalizationWarning, match="normalized to the canonical"):
        set_stereotype_relation(element, ontouml_graph, policy, BASE_URI)

    element_uri = URIRef(BASE_URI + element["id"])
    assert set(ontouml_graph.objects(element_uri, ONTOUML.stereotype)) == {ONTOUML[canonical_stereotype]}


@pytest.mark.parametrize(
    ("policy", "expected_stereotypes"),
    [
        ("preserve", {ONTOUML.abstractIndividual}),
        ("omit", set()),
    ],
)
def test_decoding_applies_invalid_stereotype_policy(
    tmp_path: Path,
    policy: str,
    expected_stereotypes: set[URIRef],
) -> None:
    """Verify that decoding preserves the element while applying the stereotype policy."""
    input_file = write_invalid_stereotype_project(tmp_path)

    with pytest.warns(InvalidStereotypeWarning, match=f"policy is '{policy}'"):
        ontouml_graph = decode_ontouml_json2graph(
            json_file_path=str(input_file),
            invalid_stereotype_policy=policy,
        )

    element_uri = URIRef(BASE_URI + "class-1")
    assert (element_uri, RDF.type, ONTOUML.Class) in ontouml_graph
    assert set(ontouml_graph.objects(element_uri, ONTOUML.stereotype)) == expected_stereotypes


@pytest.mark.parametrize(
    ("policy", "expected_stereotypes"),
    [
        ("preserve", {ONTOUML.participation}),
        ("omit", set()),
    ],
)
def test_decoding_applies_policy_to_stereotype_from_wrong_element_type(
    tmp_path: Path,
    policy: str,
    expected_stereotypes: set[URIRef],
) -> None:
    """Verify that a wrong-type stereotype follows policy without removing its element."""
    input_file = write_invalid_stereotype_project(tmp_path, stereotype="participation")

    with pytest.warns(InvalidStereotypeWarning, match="recognized for Relation, but not for Class"):
        ontouml_graph = decode_ontouml_json2graph(
            json_file_path=str(input_file),
            invalid_stereotype_policy=policy,
        )

    element_uri = URIRef(BASE_URI + "class-1")
    assert (element_uri, RDF.type, ONTOUML.Class) in ontouml_graph
    assert set(ontouml_graph.objects(element_uri, ONTOUML.stereotype)) == expected_stereotypes


@pytest.mark.parametrize("stereotype", ["abstract individual", "participation"])
def test_error_policy_does_not_create_an_output_file(tmp_path: Path, stereotype: str) -> None:
    """Verify that command-line error policy aborts before an output file is written."""
    input_file = write_invalid_stereotype_project(tmp_path, stereotype=stereotype)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            str(input_file),
            "-o",
            str(tmp_path),
            "--invalid-stereotype-policy",
            "error",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "InvalidStereotypeError" in result.stderr
    assert not (tmp_path / "invalid-stereotype.ttl").exists()
