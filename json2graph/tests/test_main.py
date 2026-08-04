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

import hashlib
import json
import subprocess
import sys
import warnings
from pathlib import Path

import pytest
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

from .test_aux import compare_graphs, get_test_list
from ..decode import decode_ontouml_json2graph, write_graph_file
from ..library import decode_json_model
from ..modules.cardinalities import (
    CardinalityRepairWarning,
    InvalidCardinalityError,
    InvalidCardinalityWarning,
)
from ..modules.input_output import JSONEncodingFallbackWarning, safe_load_json_file
from ..modules.metadata import METADATA
from ..modules.model_element_references import (
    UnresolvedModelElementError,
    UnresolvedModelElementWarning,
)
from ..modules.stereotypes import (
    InvalidStereotypeError,
    InvalidStereotypeWarning,
    StereotypeNormalizationWarning,
    normalize_stereotype,
    set_stereotype_relation,
)
from ..modules.text_values import UnsupportedTextValueWarning
from ..modules.transformation_metadata import get_rdf_media_type
from ..modules.utils_graph import load_ontouml_vocabulary

LIST_OF_TESTS = get_test_list()

BASE_URI = "https://example.org#"
ONTOUML = Namespace("https://w3id.org/ontouml#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
ONTOUML_VOCABULARY_111 = URIRef("https://w3id.org/ontouml/vocabulary/v1.1.1")
IANA_MEDIA_TYPES = "https://www.iana.org/assignments/media-types/"
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


def write_cardinality_project(tmp_path: Path, cardinality: str) -> Path:
    """Write a minimal project containing one Property with the supplied cardinality."""
    input_file = tmp_path / "cardinality.json"
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
                            "stereotype": "kind",
                            "properties": [
                                {
                                    "id": "property-1",
                                    "type": "Property",
                                    "name": "attribute",
                                    "cardinality": cardinality,
                                }
                            ],
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    return input_file


def write_text_shape_project(
    tmp_path: Path,
    width: int,
    height: int,
    value: str = "",
) -> Path:
    """Write a minimal project containing a diagrammatic Text shape."""
    input_file = tmp_path / "text-shape.json"
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
                    "contents": [],
                },
                "diagrams": [
                    {
                        "id": "diagram-1",
                        "type": "Diagram",
                        "name": "Diagram",
                        "owner": {"id": "package-1", "type": "Package"},
                        "contents": [
                            {
                                "id": "view-1",
                                "type": "GeneralizationSetView",
                                "shape": {
                                    "id": "view-1_shape",
                                    "type": "Text",
                                    "x": 0,
                                    "y": 0,
                                    "width": width,
                                    "height": height,
                                    "value": value,
                                },
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return input_file


def write_model_element_reference_project(
    tmp_path: Path,
    referenced_element_type: str = "Relation",
    resolved: bool = False,
) -> Path:
    """Write a minimal project containing an ElementView modelElement reference."""
    referenced_element_id = "referenced-element-1"

    if resolved:
        nested_contents = [
            {
                "id": referenced_element_id,
                "type": "Class",
                "name": "Defined class",
            }
        ]
        model_contents = [
            {
                "id": "nested-package-1",
                "type": "Package",
                "name": "Nested package",
                "contents": nested_contents,
            }
        ]
    else:
        model_contents = []

    if referenced_element_type == "Relation":
        shape = {
            "id": "view-1_path",
            "type": "Path",
            "points": [{"x": 0, "y": 0}, {"x": 20, "y": 20}],
        }
    else:
        shape = {
            "id": "view-1_shape",
            "type": "Rectangle",
            "x": 0,
            "y": 0,
            "width": 80,
            "height": 40,
        }

    input_file = tmp_path / "model-element-reference.json"
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
                    "contents": model_contents,
                },
                "diagrams": [
                    {
                        "id": "diagram-1",
                        "type": "Diagram",
                        "name": "Diagram",
                        "owner": {"id": "package-1", "type": "Package"},
                        "contents": [
                            {
                                "id": "view-1",
                                "type": f"{referenced_element_type}View",
                                "modelElement": {
                                    "id": referenced_element_id,
                                    "type": referenced_element_type,
                                },
                                "shape": shape,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return input_file


def assert_cardinality(
    ontouml_graph: Graph,
    value: str,
    lower_bound: str | None,
    upper_bound: str | None,
) -> None:
    """Assert the preserved Cardinality individual, value, and optional bounds."""
    property_uri = URIRef(BASE_URI + "property-1")
    cardinality_uri = URIRef(BASE_URI + "property-1_cardinality")

    assert (property_uri, RDF.type, ONTOUML.Property) in ontouml_graph
    assert (cardinality_uri, RDF.type, ONTOUML.Cardinality) in ontouml_graph
    assert (property_uri, ONTOUML.cardinality, cardinality_uri) in ontouml_graph
    assert set(ontouml_graph.objects(cardinality_uri, ONTOUML.cardinalityValue)) == {Literal(value)}

    actual_lower_bounds = set(ontouml_graph.objects(cardinality_uri, ONTOUML.lowerBound))
    actual_upper_bounds = set(ontouml_graph.objects(cardinality_uri, ONTOUML.upperBound))

    if lower_bound is None or upper_bound is None:
        assert actual_lower_bounds == set()
        assert actual_upper_bounds == set()
    else:
        assert actual_lower_bounds == {Literal(lower_bound, datatype=XSD.nonNegativeInteger)}
        assert actual_upper_bounds == {Literal(upper_bound)}


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


def test_empty_text_shape_value_is_omitted_without_warning(tmp_path: Path) -> None:
    """Verify that an empty legacy Text.value is omitted without misusing ontouml:text."""
    input_file = write_text_shape_project(tmp_path, width=80, height=42)

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedTextValueWarning)
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    text_shape_uri = URIRef(BASE_URI + "view-1_shape")
    assert (text_shape_uri, RDF.type, ONTOUML.Text) in ontouml_graph
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.text, None)))
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.value, None)))


def test_non_empty_text_shape_value_is_warned_and_omitted(tmp_path: Path) -> None:
    """Verify defensive handling for an unsupported non-empty legacy Text.value."""
    input_file = write_text_shape_project(tmp_path, width=80, height=42, value="Legacy label")

    with pytest.warns(UnsupportedTextValueWarning, match="Legacy label"):
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    text_shape_uri = URIRef(BASE_URI + "view-1_shape")
    assert (text_shape_uri, RDF.type, ONTOUML.Text) in ontouml_graph
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.text, None)))
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.value, None)))


@pytest.mark.parametrize(
    ("width", "height"),
    [
        (80, 42),
        (10, 0),
        (0, 10),
        (0, 0),
    ],
)
def test_dimensions_use_non_negative_integer_datatype(
    tmp_path: Path,
    width: int,
    height: int,
) -> None:
    """Verify that positive and zero dimensions follow OntoUML Vocabulary v1.1.1."""
    input_file = write_text_shape_project(tmp_path, width=width, height=height)

    ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    text_shape_uri = URIRef(BASE_URI + "view-1_shape")
    assert set(ontouml_graph.objects(text_shape_uri, ONTOUML.width)) == {
        Literal(width, datatype=XSD.nonNegativeInteger)
    }
    assert set(ontouml_graph.objects(text_shape_uri, ONTOUML.height)) == {
        Literal(height, datatype=XSD.nonNegativeInteger)
    }
    assert not any(
        value.datatype == XSD.positiveInteger
        for predicate in (ONTOUML.width, ONTOUML.height)
        for value in ontouml_graph.objects(text_shape_uri, predicate)
    )


def test_bundled_vocabulary_111_defines_non_negative_dimensions() -> None:
    """Verify that the declared and bundled vocabulary version supports zero dimensions."""
    ontouml_vocabulary = load_ontouml_vocabulary()

    assert METADATA["conformsToVersion"] == "v1.1.1"
    assert (ONTOUML.width, RDFS.range, XSD.nonNegativeInteger) in ontouml_vocabulary
    assert (ONTOUML.height, RDFS.range, XSD.nonNegativeInteger) in ontouml_vocabulary
    assert (ONTOUML.width, RDFS.range, XSD.positiveInteger) not in ontouml_vocabulary
    assert (ONTOUML.height, RDFS.range, XSD.positiveInteger) not in ontouml_vocabulary


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


@pytest.mark.parametrize(
    "cardinality",
    [
        "1,,*",
        "2,,*",
        "0:*",
        "2...*",
        "0..",
        "1..",
        "-1",
        "n",
        "m",
        "merged_1s",
        "*..5",
        "5..1",
    ],
)
def test_preserve_policy_keeps_invalid_cardinality_without_bounds(
    tmp_path: Path,
    cardinality: str,
) -> None:
    """Verify that preserve policy keeps invalid source text without inventing bounds."""
    input_file = write_cardinality_project(tmp_path, cardinality)

    with pytest.warns(InvalidCardinalityWarning, match="lowerBound and upperBound were omitted"):
        ontouml_graph = decode_ontouml_json2graph(
            json_file_path=str(input_file),
            invalid_cardinality_policy="preserve",
        )

    assert_cardinality(ontouml_graph, cardinality, None, None)


@pytest.mark.parametrize(
    ("source", "repaired", "lower_bound", "upper_bound"),
    [
        ("1,,*", "1..*", "1", "*"),
        ("2,,*", "2..*", "2", "*"),
        ("0:*", "0..*", "0", "*"),
        ("2...*", "2..*", "2", "*"),
        ("0..", "0..*", "0", "*"),
        ("1..", "1..*", "1", "*"),
    ],
)
def test_repair_policy_fixes_only_observed_malformed_patterns(
    tmp_path: Path,
    source: str,
    repaired: str,
    lower_bound: str,
    upper_bound: str,
) -> None:
    """Verify deterministic repairs for the malformed patterns observed in the catalog."""
    input_file = write_cardinality_project(tmp_path, source)

    with pytest.warns(CardinalityRepairWarning, match="It was repaired"):
        ontouml_graph = decode_ontouml_json2graph(
            json_file_path=str(input_file),
            invalid_cardinality_policy="repair",
        )

    assert_cardinality(ontouml_graph, repaired, lower_bound, upper_bound)


@pytest.mark.parametrize("cardinality", ["-1", "n", "m", "merged_1s", "*..5", "5..1"])
def test_repair_policy_falls_back_to_preserve_when_repair_is_unsafe(
    tmp_path: Path,
    cardinality: str,
) -> None:
    """Verify that repair policy does not invent semantics for unsupported invalid values."""
    input_file = write_cardinality_project(tmp_path, cardinality)

    with pytest.warns(InvalidCardinalityWarning, match="could not be safely repaired"):
        ontouml_graph = decode_ontouml_json2graph(
            json_file_path=str(input_file),
            invalid_cardinality_policy="repair",
        )

    assert_cardinality(ontouml_graph, cardinality, None, None)


@pytest.mark.parametrize(
    ("source", "normalized", "lower_bound", "upper_bound"),
    [
        ("0..1", "0..1", "0", "1"),
        ("1..*", "1..*", "1", "*"),
        ("20..25", "20..25", "20", "25"),
        ("5", "5..5", "5", "5"),
        ("*", "0..*", "0", "*"),
    ],
)
def test_valid_cardinality_emits_vocabulary_compliant_lower_bound(
    tmp_path: Path,
    source: str,
    normalized: str,
    lower_bound: str,
    upper_bound: str,
) -> None:
    """Verify valid cardinalities and the required lower-bound datatype."""
    input_file = write_cardinality_project(tmp_path, source)

    with warnings.catch_warnings():
        warnings.simplefilter("error", InvalidCardinalityWarning)
        warnings.simplefilter("error", CardinalityRepairWarning)
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    assert_cardinality(ontouml_graph, normalized, lower_bound, upper_bound)


def test_decode_json_model_applies_cardinality_repair_policy(tmp_path: Path) -> None:
    """Verify that the public library API exposes cardinality repair."""
    input_file = write_cardinality_project(tmp_path, "0..")

    with pytest.warns(CardinalityRepairWarning, match="It was repaired"):
        ontouml_graph = decode_json_model(
            json_file_path=str(input_file),
            invalid_cardinality_policy="repair",
        )

    assert_cardinality(ontouml_graph, "0..*", "0", "*")


def test_cardinality_error_policy_aborts_decoding(tmp_path: Path) -> None:
    """Verify that error policy rejects an invalid cardinality."""
    input_file = write_cardinality_project(tmp_path, "-1")

    with pytest.raises(InvalidCardinalityError, match="Transformation aborted"):
        decode_ontouml_json2graph(
            json_file_path=str(input_file),
            invalid_cardinality_policy="error",
        )


def test_cardinality_error_policy_does_not_create_an_output_file(tmp_path: Path) -> None:
    """Verify that command-line error policy aborts before writing output."""
    input_file = write_cardinality_project(tmp_path, "-1")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            str(input_file),
            "-o",
            str(tmp_path),
            "--invalid-cardinality-policy",
            "error",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "InvalidCardinalityError" in result.stderr
    assert not (tmp_path / "cardinality.ttl").exists()


def test_new_cardinality_argument_preserves_existing_positional_api_order(tmp_path: Path) -> None:
    """Verify that adding cardinality policy does not move the existing stereotype-policy argument."""
    input_file = write_invalid_stereotype_project(tmp_path)

    with pytest.warns(InvalidStereotypeWarning, match="policy is 'omit'"):
        ontouml_graph = decode_json_model(
            str(input_file),
            BASE_URI,
            "",
            False,
            "omit",
        )

    element_uri = URIRef(BASE_URI + "class-1")
    assert (element_uri, RDF.type, ONTOUML.Class) in ontouml_graph
    assert set(ontouml_graph.objects(element_uri, ONTOUML.stereotype)) == set()


@pytest.mark.parametrize("referenced_element_type", ["Class", "Relation"])
def test_default_policy_omits_unresolved_model_element_reference(
    tmp_path: Path,
    referenced_element_type: str,
) -> None:
    """Verify that omit is the default for every unresolved modelElement reference type."""
    input_file = write_model_element_reference_project(tmp_path, referenced_element_type)

    with pytest.warns(UnresolvedModelElementWarning, match="policy is 'omit'") as warning_records:
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    warning_message = str(warning_records[0].message)
    assert str(input_file) in warning_message
    assert "view-1" in warning_message
    assert "referenced-element-1" in warning_message
    assert f"declared type '{referenced_element_type}'" in warning_message

    element_view_uri = URIRef(BASE_URI + "view-1")
    referenced_element_uri = URIRef(BASE_URI + "referenced-element-1")
    shape_suffix = "_path" if referenced_element_type == "Relation" else "_shape"

    assert (element_view_uri, RDF.type, ONTOUML[f"{referenced_element_type}View"]) in ontouml_graph
    assert (element_view_uri, ONTOUML.shape, URIRef(BASE_URI + "view-1" + shape_suffix)) in ontouml_graph
    assert not any(ontouml_graph.triples((element_view_uri, ONTOUML.isViewOf, None)))
    assert not any(ontouml_graph.triples((referenced_element_uri, None, None)))
    assert not any(ontouml_graph.triples((None, None, referenced_element_uri)))


@pytest.mark.parametrize("referenced_element_type", ["Class", "Relation"])
def test_preserve_policy_retains_unresolved_model_element_reference(
    tmp_path: Path,
    referenced_element_type: str,
) -> None:
    """Verify that preserve keeps the current materialization behavior with a warning."""
    input_file = write_model_element_reference_project(tmp_path, referenced_element_type)

    with pytest.warns(UnresolvedModelElementWarning, match="policy is 'preserve'"):
        ontouml_graph = decode_ontouml_json2graph(
            json_file_path=str(input_file),
            unresolved_model_element_policy="preserve",
        )

    element_view_uri = URIRef(BASE_URI + "view-1")
    referenced_element_uri = URIRef(BASE_URI + "referenced-element-1")

    assert (referenced_element_uri, RDF.type, ONTOUML[referenced_element_type]) in ontouml_graph
    assert (element_view_uri, ONTOUML.isViewOf, referenced_element_uri) in ontouml_graph


def test_resolved_model_element_reference_is_preserved_without_warning(tmp_path: Path) -> None:
    """Verify that recursively contained model elements resolve normally under the default policy."""
    input_file = write_model_element_reference_project(tmp_path, referenced_element_type="Class", resolved=True)

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnresolvedModelElementWarning)
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    element_view_uri = URIRef(BASE_URI + "view-1")
    referenced_element_uri = URIRef(BASE_URI + "referenced-element-1")

    assert (referenced_element_uri, RDF.type, ONTOUML.Class) in ontouml_graph
    assert (element_view_uri, ONTOUML.isViewOf, referenced_element_uri) in ontouml_graph


def test_unresolved_model_element_error_policy_aborts_decoding(tmp_path: Path) -> None:
    """Verify that error policy rejects an unresolved modelElement reference."""
    input_file = write_model_element_reference_project(tmp_path)

    with pytest.raises(UnresolvedModelElementError, match="Transformation aborted") as error_info:
        decode_ontouml_json2graph(
            json_file_path=str(input_file),
            unresolved_model_element_policy="error",
        )

    error_message = str(error_info.value)
    assert str(input_file) in error_message
    assert "view-1" in error_message
    assert "referenced-element-1" in error_message
    assert "declared type 'Relation'" in error_message


def test_unresolved_model_element_error_policy_does_not_create_output_file(tmp_path: Path) -> None:
    """Verify that command-line error policy aborts before writing output."""
    input_file = write_model_element_reference_project(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            str(input_file),
            "-o",
            str(tmp_path),
            "--unresolved-model-element-policy",
            "error",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "UnresolvedModelElementError" in result.stderr
    assert str(input_file) in result.stderr
    assert "view-1" in result.stderr
    assert "referenced-element-1" in result.stderr
    assert not (tmp_path / "model-element-reference.ttl").exists()


def test_decode_json_model_exposes_unresolved_model_element_policy(tmp_path: Path) -> None:
    """Verify that the public model API exposes explicit preserve behavior."""
    input_file = write_model_element_reference_project(tmp_path)

    with pytest.warns(UnresolvedModelElementWarning, match="policy is 'preserve'"):
        ontouml_graph = decode_json_model(
            json_file_path=str(input_file),
            unresolved_model_element_policy="preserve",
        )

    referenced_element_uri = URIRef(BASE_URI + "referenced-element-1")
    assert (referenced_element_uri, RDF.type, ONTOUML.Relation) in ontouml_graph


def run_metadata_cli(input_file: Path, output_directory: Path, mode: str | None = None) -> subprocess.CompletedProcess:
    """Run the command-line transformation with an optional metadata mode."""
    command = [
        sys.executable,
        "-m",
        "json2graph.decode",
        "-i",
        str(input_file),
        "-o",
        str(output_directory),
        "--silent",
    ]
    if mode is not None:
        command.extend(["--transformation-metadata", mode])
    return subprocess.run(command, capture_output=True, check=False, text=True)


def get_output_artifact(metadata_graph: Graph) -> URIRef:
    """Return the single entity generated by a recorded transformation activity."""
    output_artifacts = set(metadata_graph.subjects(PROV.wasGeneratedBy, None))
    assert len(output_artifacts) == 1
    return next(iter(output_artifacts))


def test_default_output_omits_transformation_metadata(tmp_path: Path) -> None:
    """Verify that the default output is a pure, deterministic model graph."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    first_graph = decode_ontouml_json2graph(json_file_path=str(input_file))
    second_graph = decode_ontouml_json2graph(json_file_path=str(input_file))

    assert set(first_graph) == set(second_graph)
    assert not any(first_graph.triples((None, RDF.type, PROV.Entity)))
    assert not any(first_graph.triples((None, PROV.generatedAtTime, None)))
    assert not any(first_graph.triples((None, DCTERMS.conformsTo, None)))
    assert not any(first_graph.triples((None, RDF.type, OWL.Ontology)))
    assert not any(first_graph.triples((None, DCTERMS.created, None)))
    assert not any(first_graph.triples((None, DCTERMS.language, None)))
    assert not any(first_graph.triples((None, RDFS.comment, None)))
    assert not any(first_graph.triples((None, RDFS.seeAlso, None)))


def test_cli_default_writes_no_metadata_or_sidecar(tmp_path: Path) -> None:
    """Verify that omitting the new CLI option preserves metadata-free output."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    result = run_metadata_cli(input_file, tmp_path)

    assert result.returncode == 0, result.stderr
    output_graph = Graph().parse(tmp_path / "cardinality.ttl", format="turtle")
    assert not any(output_graph.triples((None, RDF.type, PROV.Entity)))
    assert not (tmp_path / "cardinality.provenance.ttl").exists()


def test_embedded_metadata_describes_the_transformation(tmp_path: Path) -> None:
    """Verify the complete, opt-in embedded provenance profile."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    result = run_metadata_cli(input_file, tmp_path, "embedded")

    assert result.returncode == 0, result.stderr
    output_file = tmp_path / "cardinality.ttl"
    output_graph = Graph().parse(output_file, format="turtle")
    output_artifact = get_output_artifact(output_graph)
    transformation = output_graph.value(output_artifact, PROV.wasGeneratedBy)

    assert (output_artifact, RDF.type, PROV.Entity) in output_graph
    assert (output_artifact, DCTERMS.title, Literal(output_file.name)) in output_graph
    assert (
        output_artifact,
        DCTERMS["format"],
        URIRef(IANA_MEDIA_TYPES + "text/turtle"),
    ) in output_graph
    assert (output_artifact, DCTERMS.conformsTo, ONTOUML_VOCABULARY_111) in output_graph
    assert (transformation, RDF.type, PROV.Activity) in output_graph

    generation_time = output_graph.value(output_artifact, PROV.generatedAtTime)
    assert generation_time.datatype == XSD.dateTime
    assert generation_time.toPython().utcoffset().total_seconds() == 0

    software_agents = set(output_graph.objects(transformation, PROV.wasAssociatedWith))
    assert len(software_agents) == 1
    software_agent = next(iter(software_agents))
    assert (software_agent, RDF.type, PROV.SoftwareAgent) in output_graph
    assert (software_agent, DCTERMS.title, Literal(METADATA["Name"])) in output_graph
    assert set(output_graph.objects(software_agent, DCTERMS.identifier)) == {
        Literal(f"{METADATA['Name']}/{METADATA['Version']}")
    }

    used_entities = set(output_graph.objects(transformation, PROV.used))
    source_artifact = next(
        entity for entity in used_entities if (entity, DCTERMS.title, Literal(input_file.name)) in output_graph
    )
    configuration_entity = next(entity for entity in used_entities if (entity, PROV.value, None) in output_graph)
    expected_digest = hashlib.sha256(input_file.read_bytes()).hexdigest()

    assert (source_artifact, RDF.type, PROV.Entity) in output_graph
    assert (source_artifact, DCTERMS.identifier, Literal(f"sha256:{expected_digest}")) in output_graph
    assert (
        source_artifact,
        DCTERMS["format"],
        URIRef(IANA_MEDIA_TYPES + "application/json"),
    ) in output_graph

    configuration = json.loads(str(output_graph.value(configuration_entity, PROV.value)))
    assert configuration == {
        "base_uri": BASE_URI,
        "correct": False,
        "invalid_cardinality_policy": "preserve",
        "invalid_stereotype_policy": "preserve",
        "language": "",
        "model_only": False,
        "unresolved_model_element_policy": "omit",
    }
    assert (configuration_entity, DCTERMS["format"], URIRef(IANA_MEDIA_TYPES + "application/json")) in output_graph
    assert str(tmp_path) not in " ".join(str(value) for value in output_graph.objects(None, None))
    assert not (tmp_path / "cardinality.provenance.ttl").exists()


def test_sidecar_metadata_keeps_the_model_output_unchanged(tmp_path: Path) -> None:
    """Verify that sidecar mode writes provenance separately from the model graph."""
    input_file = write_cardinality_project(tmp_path, "0..1")
    default_directory = tmp_path / "default"
    sidecar_directory = tmp_path / "sidecar"
    default_directory.mkdir()
    sidecar_directory.mkdir()

    default_result = run_metadata_cli(input_file, default_directory)
    sidecar_result = run_metadata_cli(input_file, sidecar_directory, "sidecar")

    assert default_result.returncode == 0, default_result.stderr
    assert sidecar_result.returncode == 0, sidecar_result.stderr

    default_graph = Graph().parse(default_directory / "cardinality.ttl", format="turtle")
    sidecar_model_graph = Graph().parse(sidecar_directory / "cardinality.ttl", format="turtle")
    metadata_graph = Graph().parse(sidecar_directory / "cardinality.provenance.ttl", format="turtle")

    assert set(sidecar_model_graph) == set(default_graph)
    assert not any(sidecar_model_graph.triples((None, RDF.type, PROV.Entity)))
    output_artifact = get_output_artifact(metadata_graph)
    assert (output_artifact, DCTERMS.title, Literal("cardinality.ttl")) in metadata_graph
    assert (output_artifact, DCTERMS.conformsTo, ONTOUML_VOCABULARY_111) in metadata_graph


def test_conformance_is_omitted_when_output_uses_an_undeclared_ontouml_term(tmp_path: Path) -> None:
    """Verify that the transformer does not make a false vocabulary-conformance claim."""
    input_file = write_invalid_stereotype_project(tmp_path)

    result = run_metadata_cli(input_file, tmp_path, "embedded")

    assert result.returncode == 0, result.stderr
    output_graph = Graph().parse(tmp_path / "invalid-stereotype.ttl", format="turtle")
    output_artifact = get_output_artifact(output_graph)
    assert not any(output_graph.triples((output_artifact, DCTERMS.conformsTo, None)))


def test_library_embedded_metadata_never_creates_a_sidecar(tmp_path: Path) -> None:
    """Verify that in-memory library decoding has no implicit file-writing side effect."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    output_graph = decode_json_model(
        json_file_path=str(input_file),
        transformation_metadata="embedded",
    )

    output_artifact = get_output_artifact(output_graph)
    assert (output_artifact, DCTERMS.conformsTo, ONTOUML_VOCABULARY_111) in output_graph
    assert not list(tmp_path.glob("*.provenance.ttl"))


def test_library_rejects_sidecar_without_an_output_operation(tmp_path: Path) -> None:
    """Verify that sidecar mode cannot silently write from an in-memory decoding API."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    with pytest.raises(ValueError, match="Software's requirement not met"):
        decode_json_model(
            json_file_path=str(input_file),
            transformation_metadata="sidecar",
        )

    assert not list(tmp_path.glob("*.provenance.ttl"))


@pytest.mark.parametrize(
    ("graph_format", "media_type"),
    [
        ("ttl", "text/turtle"),
        ("xml", "application/rdf+xml"),
        ("json-ld", "application/ld+json"),
        ("nt", "application/n-triples"),
        ("n3", "text/n3"),
        ("trig", "application/trig"),
        ("nquads", "application/n-quads"),
    ],
)
def test_serialization_formats_use_registered_iana_media_types(graph_format: str, media_type: str) -> None:
    """Verify that output formats use their registered IANA media-type resources."""
    assert get_rdf_media_type(graph_format) == URIRef(IANA_MEDIA_TYPES + media_type)


def test_trix_does_not_invent_an_unregistered_iana_media_type() -> None:
    """Verify that TriX provenance omits a media type absent from the IANA registry."""
    assert get_rdf_media_type("trix") is None


def test_batch_sidecars_describe_each_actual_source_file(tmp_path: Path) -> None:
    """Verify that batch output keeps each input filename and digest traceable."""
    input_directory = tmp_path / "inputs"
    output_directory = tmp_path / "outputs"
    input_directory.mkdir()
    output_directory.mkdir()

    first_input = write_cardinality_project(input_directory, "0..1")
    first_input = first_input.rename(input_directory / "first.json")
    second_input = write_cardinality_project(input_directory, "1..*")
    second_input = second_input.rename(input_directory / "second.json")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-a",
            "-i",
            str(input_directory),
            "-o",
            str(output_directory),
            "--silent",
            "--transformation-metadata",
            "sidecar",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    for input_file in (first_input, second_input):
        assert (output_directory / f"{input_file.stem}.ttl").exists()
        metadata_graph = Graph().parse(
            output_directory / f"{input_file.stem}.provenance.ttl",
            format="turtle",
        )
        transformation = metadata_graph.value(get_output_artifact(metadata_graph), PROV.wasGeneratedBy)
        source_artifact = next(
            entity
            for entity in metadata_graph.objects(transformation, PROV.used)
            if (entity, DCTERMS.title, Literal(input_file.name)) in metadata_graph
        )
        expected_digest = hashlib.sha256(input_file.read_bytes()).hexdigest()
        assert (
            source_artifact,
            DCTERMS.identifier,
            Literal(f"sha256:{expected_digest}"),
        ) in metadata_graph
