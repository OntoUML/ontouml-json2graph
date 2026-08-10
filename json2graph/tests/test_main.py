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
import tomli
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

from .test_aux import compare_graphs, get_test_list
from ..decode import decode_ontouml_json2graph, write_graph_file
from ..library import decode_json_model, decode_json_project
from ..modules.cardinalities import (
    CardinalityRepairWarning,
    InvalidCardinalityError,
    InvalidCardinalityWarning,
)
from ..modules.content_identity import create_content_uuid, resolve_base_uri
from ..modules.input_output import JSONEncodingFallbackWarning, safe_load_json_file
from ..modules.metadata import METADATA, _read_source_project_version
from ..modules.model_element_references import (
    UnresolvedModelElementError,
    UnresolvedModelElementWarning,
)
from ..modules.path_order import PathPointOrderWarning
from ..modules.property_assignments import PropertyAssignmentWarning
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


def write_path_project(tmp_path: Path) -> Path:
    """Write a minimal project containing one ordered diagram Path."""
    input_file = tmp_path / "path-order.json"
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
                                "type": "RelationView",
                                "shape": {
                                    "id": "view-1_path",
                                    "type": "Path",
                                    "points": [
                                        {"x": 10, "y": 20},
                                        {"x": 10, "y": 40},
                                        {"x": 30, "y": 40},
                                    ],
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


def write_property_assignment_project(tmp_path: Path, assignments: object) -> Path:
    """Write a minimal project containing one Class with property assignments."""
    input_file = tmp_path / "property-assignments.json"
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
                            "propertyAssignments": assignments,
                        }
                    ],
                },
            },
            ensure_ascii=False,
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
        base_uri=BASE_URI,
        model_only=True,
        execution_mode="import",
    )

    assert_enumeration_literals_preserved(ontouml_graph)
    assert_diagrammatic_elements_removed(ontouml_graph)


def test_decode_json_model_preserves_enumeration_literals() -> None:
    """Verify that the public model-decoding API preserves enumeration literals."""
    ontouml_graph = decode_json_model(json_file_path=ENUMERATION_INPUT_FILE, base_uri=BASE_URI)

    assert_enumeration_literals_preserved(ontouml_graph)


def test_decode_json_project_preserves_project_and_diagrammatic_elements() -> None:
    """Verify that the public project-decoding API preserves the complete project."""
    ontouml_graph = decode_json_project(
        json_file_path=ENUMERATION_INPUT_FILE,
        base_uri=BASE_URI,
    )

    project_uri = URIRef(BASE_URI + "4NWbZJGFYGjgAQm6")
    package_uri = URIRef(BASE_URI + "4NWbZJGFYGjgAQm6_root")
    diagram_uri = URIRef(BASE_URI + "cD2bZJGFYGjgAQ2V")
    class_view_uri = URIRef(BASE_URI + "SSxbZJGFYGjgAQ3X")
    rectangle_uri = URIRef(BASE_URI + "SSxbZJGFYGjgAQ3X_shape")

    assert_enumeration_literals_preserved(ontouml_graph)
    assert (project_uri, RDF.type, ONTOUML.Project) in ontouml_graph
    assert (project_uri, ONTOUML.model, package_uri) in ontouml_graph
    assert (project_uri, ONTOUML.diagram, diagram_uri) in ontouml_graph
    assert (package_uri, RDF.type, ONTOUML.Package) in ontouml_graph
    assert (diagram_uri, RDF.type, ONTOUML.Diagram) in ontouml_graph
    assert (diagram_uri, ONTOUML.containsView, class_view_uri) in ontouml_graph
    assert (class_view_uri, RDF.type, ONTOUML.ClassView) in ontouml_graph
    assert (class_view_uri, ONTOUML.shape, rectangle_uri) in ontouml_graph
    assert (rectangle_uri, RDF.type, ONTOUML.Rectangle) in ontouml_graph


def test_default_path_order_policy_warns_without_adding_an_annotation(tmp_path: Path) -> None:
    """Verify that the default preserves the existing graph while reporting order loss."""
    input_file = write_path_project(tmp_path)

    with pytest.warns(PathPointOrderWarning, match="point triples were emitted without order"):
        ontouml_graph = decode_json_project(json_file_path=str(input_file), base_uri=BASE_URI)

    path_uri = URIRef(BASE_URI + "view-1_path")
    expected_points = {URIRef(BASE_URI + f"view-1_path_point_{index}") for index in range(3)}

    assert set(ontouml_graph.objects(path_uri, ONTOUML.point)) == expected_points
    assert not any(ontouml_graph.triples((path_uri, RDFS.comment, None)))


def test_comment_path_order_policy_adds_the_source_sequence_as_text(tmp_path: Path) -> None:
    """Verify that explicit comment mode adds a deterministic, non-normative annotation."""
    input_file = write_path_project(tmp_path)

    with pytest.warns(PathPointOrderWarning, match="non-normative rdfs:comment"):
        ontouml_graph = decode_json_project(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
            path_order_policy="comment",
        )

    path_uri = URIRef(BASE_URI + "view-1_path")
    assert set(ontouml_graph.objects(path_uri, RDFS.comment)) == {
        Literal("Source JSON path point order: (10, 20) -> (10, 40) -> (30, 40).")
    }


def test_model_only_decoding_does_not_report_or_annotate_path_order(tmp_path: Path) -> None:
    """Verify that a policy for omitted diagram data does not affect model-only output."""
    input_file = write_path_project(tmp_path)

    with warnings.catch_warnings():
        warnings.simplefilter("error", PathPointOrderWarning)
        ontouml_graph = decode_json_model(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
            path_order_policy="comment",
        )

    assert not any(ontouml_graph.triples((None, RDF.type, ONTOUML.Path)))
    assert not any(ontouml_graph.triples((None, RDFS.comment, None)))


def test_cli_exposes_comment_path_order_policy(tmp_path: Path) -> None:
    """Verify that command-line users can explicitly request textual path order."""
    input_file = write_path_project(tmp_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            str(input_file),
            "-o",
            str(tmp_path),
            "--silent",
            "--base-uri",
            BASE_URI,
            "--path-order-policy",
            "comment",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    output_graph = Graph().parse(tmp_path / "path-order.ttl", format="turtle")
    assert set(output_graph.objects(URIRef(BASE_URI + "view-1_path"), RDFS.comment)) == {
        Literal("Source JSON path point order: (10, 20) -> (10, 40) -> (30, 40).")
    }


def test_invalid_path_order_policy_is_rejected(tmp_path: Path) -> None:
    """Verify that library decoding rejects unsupported path-order behavior."""
    input_file = write_path_project(tmp_path)

    with pytest.raises(ValueError, match="Software's requirement not met"):
        decode_json_project(
            json_file_path=str(input_file),
            path_order_policy="sidecar",
        )


def test_default_property_assignment_policy_warns_and_omits_assignments(tmp_path: Path) -> None:
    """Verify that the default reports each affected element without changing its RDF description."""
    input_file = write_property_assignment_project(
        tmp_path,
        {"documentation": None, "categoryValue": None},
    )

    with pytest.warns(
        PropertyAssignmentWarning,
        match=r"Class ID 'class-1' \(keys: categoryValue, documentation\)",
    ):
        ontouml_graph = decode_json_project(json_file_path=str(input_file), base_uri=BASE_URI)

    class_uri = URIRef(BASE_URI + "class-1")
    assert (class_uri, RDF.type, ONTOUML.Class) in ontouml_graph
    assert not any(ontouml_graph.triples((class_uri, RDFS.comment, None)))
    assert not any(ontouml_graph.triples((class_uri, ONTOUML.propertyAssignments, None)))


def test_comment_property_assignment_policy_adds_canonical_json_as_text(tmp_path: Path) -> None:
    """Verify that comment mode preserves heterogeneous source values as deterministic JSON text."""
    assignments = {
        "rank": 2,
        "nested": {"z": 1, "a": "ação"},
        "labels": ["first", {"type": "Class", "id": "referenced-class"}],
        "enabled": True,
        "documentation": None,
    }
    input_file = write_property_assignment_project(tmp_path, assignments)

    with pytest.warns(PropertyAssignmentWarning, match="non-normative rdfs:comment"):
        ontouml_graph = decode_json_model(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
            property_assignment_policy="comment",
        )

    class_uri = URIRef(BASE_URI + "class-1")
    expected_json = json.dumps(assignments, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    assert set(ontouml_graph.objects(class_uri, RDFS.comment)) == {
        Literal(f"Source JSON propertyAssignments: {expected_json}")
    }


@pytest.mark.parametrize("assignments", [None, {}])
def test_null_and_empty_property_assignments_are_ignored_without_warning(
    tmp_path: Path,
    assignments: object,
) -> None:
    """Verify that absent assignment information does not produce noise or annotations."""
    input_file = write_property_assignment_project(tmp_path, assignments)

    with warnings.catch_warnings():
        warnings.simplefilter("error", PropertyAssignmentWarning)
        ontouml_graph = decode_json_project(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
            property_assignment_policy="comment",
        )

    assert not any(ontouml_graph.triples((URIRef(BASE_URI + "class-1"), RDFS.comment, None)))


def test_cli_exposes_comment_property_assignment_policy(tmp_path: Path) -> None:
    """Verify that command-line users can explicitly request textual assignment preservation."""
    input_file = write_property_assignment_project(tmp_path, {"TABLESPACE": None})

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            str(input_file),
            "-o",
            str(tmp_path),
            "--silent",
            "--base-uri",
            BASE_URI,
            "--property-assignment-policy",
            "comment",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    output_graph = Graph().parse(tmp_path / "property-assignments.ttl", format="turtle")
    assert set(output_graph.objects(URIRef(BASE_URI + "class-1"), RDFS.comment)) == {
        Literal('Source JSON propertyAssignments: {"TABLESPACE":null}')
    }


def test_invalid_property_assignment_policy_is_rejected(tmp_path: Path) -> None:
    """Verify that library decoding rejects unsupported property-assignment behavior."""
    input_file = write_property_assignment_project(tmp_path, {"documentation": None})

    with pytest.raises(ValueError, match="Software's requirement not met"):
        decode_json_project(
            json_file_path=str(input_file),
            property_assignment_policy="sidecar",
        )


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
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

    text_shape_uri = URIRef(BASE_URI + "view-1_shape")
    assert (text_shape_uri, RDF.type, ONTOUML.Text) in ontouml_graph
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.text, None)))
    assert not any(ontouml_graph.triples((text_shape_uri, ONTOUML.value, None)))


def test_non_empty_text_shape_value_is_warned_and_omitted(tmp_path: Path) -> None:
    """Verify defensive handling for an unsupported non-empty legacy Text.value."""
    input_file = write_text_shape_project(tmp_path, width=80, height=42, value="Legacy label")

    with pytest.warns(UnsupportedTextValueWarning, match="Legacy label"):
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

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

    ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

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
            base_uri=BASE_URI,
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
            base_uri=BASE_URI,
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
            base_uri=BASE_URI,
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
            base_uri=BASE_URI,
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
            base_uri=BASE_URI,
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
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

    assert_cardinality(ontouml_graph, normalized, lower_bound, upper_bound)


def test_decode_json_model_applies_cardinality_repair_policy(tmp_path: Path) -> None:
    """Verify that the public library API exposes cardinality repair."""
    input_file = write_cardinality_project(tmp_path, "0..")

    with pytest.warns(CardinalityRepairWarning, match="It was repaired"):
        ontouml_graph = decode_json_model(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
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
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

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
            base_uri=BASE_URI,
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
        ontouml_graph = decode_ontouml_json2graph(json_file_path=str(input_file), base_uri=BASE_URI)

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
            base_uri=BASE_URI,
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


def test_source_execution_reports_the_actual_project_version() -> None:
    """Verify that source-checkout execution reports the version declared by the project."""
    pyproject_file = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with pyproject_file.open("rb") as file:
        expected_version = tomli.load(file)["tool"]["poetry"]["version"]

    assert _read_source_project_version() == expected_version
    assert METADATA["Version"] == expected_version

    result = subprocess.run(
        [sys.executable, "-m", "json2graph.decode", "--version"],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0
    assert result.stdout.strip() == f"ontouml-json2graph - version {expected_version}"

    source_bootstrap = (
        "import importlib.metadata\n"
        "import runpy\n"
        "import sys\n"
        "installed_metadata = importlib.metadata.metadata\n"
        "def missing_distribution(name):\n"
        "    if name == 'ontouml-json2graph':\n"
        "        raise importlib.metadata.PackageNotFoundError(name)\n"
        "    return installed_metadata(name)\n"
        "importlib.metadata.metadata = missing_distribution\n"
        "sys.argv = ['json2graph.decode', '--version']\n"
        "runpy.run_module('json2graph.decode', run_name='__main__')\n"
    )
    source_result = subprocess.run(
        [sys.executable, "-c", source_bootstrap],
        capture_output=True,
        check=False,
        text=True,
    )

    assert source_result.returncode == 0
    assert source_result.stdout.strip() == f"ontouml-json2graph - version {expected_version}"


def test_content_uuid_uses_canonical_json_and_preserves_array_order() -> None:
    """Verify that insignificant object formatting is ignored while array order remains significant."""
    first_document = {"name": "Café", "items": [1, 2], "enabled": True}
    reordered_object = {"enabled": True, "items": [1, 2], "name": "Café"}
    reordered_array = {"name": "Café", "items": [2, 1], "enabled": True}

    assert str(create_content_uuid(first_document)) == "ec1f2fd6-ec3e-536e-851f-1df8e963816f"
    assert create_content_uuid(first_document) == create_content_uuid(reordered_object)
    assert create_content_uuid(first_document) != create_content_uuid(reordered_array)


def test_default_base_uri_is_deterministic_for_the_same_json(tmp_path: Path) -> None:
    """Verify that repeated decoding produces the same content-derived resource identifiers."""
    input_file = write_cardinality_project(tmp_path, "0..1")
    json_data = json.loads(input_file.read_text(encoding="utf-8"))
    expected_base_uri = f"urn:uuid:{create_content_uuid(json_data)}#"
    expected_class = URIRef(expected_base_uri + "class-1")

    first_graph = decode_json_project(json_file_path=str(input_file))
    second_graph = decode_json_project(json_file_path=str(input_file))

    assert set(first_graph) == set(second_graph)
    assert (expected_class, RDF.type, ONTOUML.Class) in first_graph


def test_default_base_uri_ignores_json_whitespace_and_key_order(tmp_path: Path) -> None:
    """Verify that equivalent parsed JSON produces equal graphs and identifiers."""
    first_input = write_cardinality_project(tmp_path, "0..1")
    json_data = json.loads(first_input.read_text(encoding="utf-8"))
    second_input = tmp_path / "reformatted.json"
    second_input.write_text(
        json.dumps(json_data, ensure_ascii=False, indent=4, sort_keys=True),
        encoding="utf-8",
    )

    first_graph = decode_json_project(json_file_path=str(first_input))
    second_graph = decode_json_project(json_file_path=str(second_input))

    assert set(first_graph) == set(second_graph)


def test_content_change_produces_a_different_default_base_uri(tmp_path: Path) -> None:
    """Verify that different canonical JSON documents receive different namespaces."""
    first_input = write_cardinality_project(tmp_path, "0..1").rename(tmp_path / "first.json")
    second_input = write_cardinality_project(tmp_path, "1..*").rename(tmp_path / "second.json")
    first_data = json.loads(first_input.read_text(encoding="utf-8"))
    second_data = json.loads(second_input.read_text(encoding="utf-8"))
    first_class = URIRef(resolve_base_uri(first_data) + "class-1")
    second_class = URIRef(resolve_base_uri(second_data) + "class-1")

    first_graph = decode_json_project(json_file_path=str(first_input))
    second_graph = decode_json_project(json_file_path=str(second_input))

    assert first_class != second_class
    assert (first_class, RDF.type, ONTOUML.Class) in first_graph
    assert (second_class, RDF.type, ONTOUML.Class) in second_graph


def test_project_and_model_decoding_share_the_same_default_base_uri(tmp_path: Path) -> None:
    """Verify that model-only filtering does not alter document identity."""
    input_file = write_cardinality_project(tmp_path, "0..1")
    json_data = json.loads(input_file.read_text(encoding="utf-8"))
    expected_class = URIRef(resolve_base_uri(json_data) + "class-1")

    project_graph = decode_json_project(json_file_path=str(input_file))
    model_graph = decode_json_model(json_file_path=str(input_file))

    assert (expected_class, RDF.type, ONTOUML.Class) in project_graph
    assert (expected_class, RDF.type, ONTOUML.Class) in model_graph


def test_explicit_base_uri_is_used_without_a_content_id(tmp_path: Path) -> None:
    """Verify exact explicit-base behavior in the library API."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    ontouml_graph = decode_json_project(
        json_file_path=str(input_file),
        base_uri="https://pp.pp/model",
    )

    assert (URIRef("https://pp.pp/model#class-1"), RDF.type, ONTOUML.Class) in ontouml_graph


def test_explicit_base_uri_can_include_the_content_id(tmp_path: Path) -> None:
    """Verify content-scoped explicit-base behavior in the library API."""
    input_file = write_cardinality_project(tmp_path, "0..1")
    json_data = json.loads(input_file.read_text(encoding="utf-8"))
    expected_base_uri = f"https://pp.pp/{create_content_uuid(json_data)}#"

    ontouml_graph = decode_json_project(
        json_file_path=str(input_file),
        base_uri="https://pp.pp#",
        append_content_hash=True,
    )

    assert (URIRef(expected_base_uri + "class-1"), RDF.type, ONTOUML.Class) in ontouml_graph


def test_invalid_explicit_base_uri_is_rejected(tmp_path: Path) -> None:
    """Verify that library users receive the same base-URI validation as CLI users."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    with pytest.raises(ValueError, match="absolute URI"):
        decode_json_project(json_file_path=str(input_file), base_uri="relative/path")


def test_cli_base_uri_options_are_mutually_exclusive(tmp_path: Path) -> None:
    """Verify that the CLI rejects conflicting exact and content-scoped bases."""
    input_file = write_cardinality_project(tmp_path, "0..1")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "json2graph.decode",
            "-i",
            str(input_file),
            "--base-uri",
            "https://pp.pp#",
            "--base-uri-with-content-id",
            "https://pp.pp#",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0
    assert "not allowed with argument" in result.stderr


@pytest.mark.parametrize(
    ("base_option", "expected_parent"),
    [
        ([], None),
        (["--base-uri-with-content-id", "https://pp.pp#"], "https://pp.pp"),
    ],
)
def test_batch_mode_creates_content_scoped_namespaces(
    tmp_path: Path,
    base_option: list[str],
    expected_parent: str | None,
) -> None:
    """Verify safe content-derived namespaces for default and explicitly scoped batches."""
    input_directory = tmp_path / "inputs"
    output_directory = tmp_path / "outputs"
    input_directory.mkdir()
    output_directory.mkdir()
    first_input = write_cardinality_project(input_directory, "0..1").rename(input_directory / "first.json")
    second_input = write_cardinality_project(input_directory, "1..*").rename(input_directory / "second.json")

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
            *base_option,
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    expected_classes = []
    for input_file in (first_input, second_input):
        json_data = json.loads(input_file.read_text(encoding="utf-8"))
        if expected_parent is None:
            base_uri = resolve_base_uri(json_data)
        else:
            base_uri = f"{expected_parent}/{create_content_uuid(json_data)}#"
        expected_class = URIRef(base_uri + "class-1")
        expected_classes.append(expected_class)
        output_graph = Graph().parse(output_directory / f"{input_file.stem}.ttl", format="turtle")
        assert (expected_class, RDF.type, ONTOUML.Class) in output_graph

    assert expected_classes[0] != expected_classes[1]


def test_batch_mode_allows_and_warns_about_an_explicit_shared_base(tmp_path: Path) -> None:
    """Verify that an intentional exact batch namespace is preserved with a collision warning."""
    input_directory = tmp_path / "inputs"
    output_directory = tmp_path / "outputs"
    input_directory.mkdir()
    output_directory.mkdir()
    write_cardinality_project(input_directory, "0..1").rename(input_directory / "first.json")
    write_cardinality_project(input_directory, "1..*").rename(input_directory / "second.json")

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
            "--base-uri",
            BASE_URI,
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "resources can collide" in result.stderr
    for output_file in output_directory.glob("*.ttl"):
        output_graph = Graph().parse(output_file, format="turtle")
        assert (URIRef(BASE_URI + "class-1"), RDF.type, ONTOUML.Class) in output_graph


def get_output_artifact(metadata_graph: Graph) -> URIRef:
    """Return the single entity generated by a recorded transformation activity."""
    output_artifacts = set(metadata_graph.subjects(PROV.wasGeneratedBy, None))
    assert len(output_artifacts) == 1
    return next(iter(output_artifacts))


def get_recorded_configuration(metadata_graph: Graph) -> dict[str, object]:
    """Return the canonical JSON configuration used by the transformation."""
    transformation = metadata_graph.value(get_output_artifact(metadata_graph), PROV.wasGeneratedBy)
    configuration_entities = [
        entity
        for entity in metadata_graph.objects(transformation, PROV.used)
        if (entity, PROV.value, None) in metadata_graph
    ]
    assert len(configuration_entities) == 1
    return json.loads(str(metadata_graph.value(configuration_entities[0], PROV.value)))


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

    configuration = get_recorded_configuration(output_graph)
    expected_base_uri = resolve_base_uri(json.loads(input_file.read_text(encoding="utf-8")))
    assert configuration == {
        "append_content_hash": False,
        "base_uri": None,
        "correct": False,
        "effective_base_uri": expected_base_uri,
        "format": "ttl",
        "invalid_cardinality_policy": "preserve",
        "invalid_stereotype_policy": "preserve",
        "language": "",
        "model_only": False,
        "path_order_policy": "warn",
        "property_assignment_policy": "warn",
        "transformation_metadata": "embedded",
        "unresolved_model_element_policy": "omit",
    }
    assert (configuration_entity, DCTERMS["format"], URIRef(IANA_MEDIA_TYPES + "application/json")) in output_graph
    assert str(tmp_path) not in " ".join(str(value) for value in output_graph.objects(None, None))
    assert not (tmp_path / "cardinality.provenance.ttl").exists()


def test_metadata_records_comment_path_order_policy(tmp_path: Path) -> None:
    """Verify that provenance records the output-affecting path order option."""
    input_file = write_path_project(tmp_path)

    with pytest.warns(PathPointOrderWarning):
        output_graph = decode_json_project(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
            path_order_policy="comment",
            transformation_metadata="embedded",
        )

    configuration = get_recorded_configuration(output_graph)
    assert configuration["path_order_policy"] == "comment"
    assert any(output_graph.triples((URIRef(BASE_URI + "view-1_path"), RDFS.comment, None)))


def test_metadata_records_comment_property_assignment_policy(tmp_path: Path) -> None:
    """Verify that provenance records the output-affecting property-assignment option."""
    input_file = write_property_assignment_project(tmp_path, {"documentation": None})

    with pytest.warns(PropertyAssignmentWarning):
        output_graph = decode_json_project(
            json_file_path=str(input_file),
            base_uri=BASE_URI,
            property_assignment_policy="comment",
            transformation_metadata="embedded",
        )

    configuration = get_recorded_configuration(output_graph)
    assert configuration["property_assignment_policy"] == "comment"
    assert any(output_graph.triples((URIRef(BASE_URI + "class-1"), RDFS.comment, None)))


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
    configuration = get_recorded_configuration(metadata_graph)
    assert configuration["format"] == "ttl"
    assert configuration["transformation_metadata"] == "sidecar"


@pytest.mark.parametrize(
    ("requested_base_uri", "append_content_hash"),
    [
        (None, False),
        (BASE_URI, False),
        ("https://example.org/models", True),
    ],
)
def test_metadata_records_requested_and_effective_base_uri(
    tmp_path: Path,
    requested_base_uri: str | None,
    append_content_hash: bool,
) -> None:
    """Verify provenance distinguishes all three base-URI selection modes."""
    input_file = write_cardinality_project(tmp_path, "0..1")
    json_data = json.loads(input_file.read_text(encoding="utf-8"))

    output_graph = decode_json_project(
        json_file_path=str(input_file),
        base_uri=requested_base_uri,
        append_content_hash=append_content_hash,
        transformation_metadata="embedded",
    )

    configuration = get_recorded_configuration(output_graph)
    assert configuration["base_uri"] == requested_base_uri
    assert configuration["append_content_hash"] is append_content_hash
    assert configuration["effective_base_uri"] == resolve_base_uri(
        json_data,
        base_uri=requested_base_uri,
        append_content_hash=append_content_hash,
    )
    assert configuration["format"] is None
    assert configuration["transformation_metadata"] == "embedded"


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
    configuration = get_recorded_configuration(output_graph)
    assert configuration["format"] is None
    assert configuration["model_only"] is True
    assert configuration["transformation_metadata"] == "embedded"
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
