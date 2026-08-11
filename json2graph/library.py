"""Expose the supported Python interface for OntoUML JSON-to-RDF conversion."""

from rdflib import Graph

from .decode import decode_ontouml_json2graph
from .modules.errors import report_error_requirement_not_met
from .modules.input_output import safe_write_graph_file


def decode_json_project(
    json_file_path: str,
    base_uri: str | None = None,
    language: str = "",
    correct: bool = False,
    invalid_stereotype_policy: str = "preserve",
    invalid_cardinality_policy: str = "preserve",
    unresolved_model_element_policy: str = "omit",
    transformation_metadata: str = "none",
    append_content_hash: bool = False,
    path_order_policy: str = "warn",
    property_assignment_policy: str = "warn",
) -> Graph:
    """Decode an OntoUML JSON project, including supported diagrammatic data.

    The returned RDFLib graph contains the project, domain-level model, and
    supported diagrammatic resources. The decoder expects the OntoUML JSON
    structure but does not perform JSON Schema validation.

    :param json_file_path: Path to the OntoUML JSON file.
    :type json_file_path: str
    :param base_uri: Explicit absolute base URI for generated resources. When
                     omitted, a deterministic ``urn:uuid:`` base is derived
                     from the parsed JSON document.
    :type base_uri: str or None
    :param language: Language tag applied to source ``name`` literals. An empty
                     string leaves names without a language tag.
    :type language: str
    :param correct: Enable the legacy class and property correction pass. This
                    is independent of the explicit policy parameters.
    :type correct: bool
    :param invalid_stereotype_policy: Handle stereotypes invalid for their
                                      element type with ``preserve``, ``omit``,
                                      or ``error``. Default is ``preserve``.
    :type invalid_stereotype_policy: str
    :param invalid_cardinality_policy: Handle invalid cardinalities with
                                       ``preserve``, limited safe ``repair``,
                                       or ``error``. Default is ``preserve``.
    :type invalid_cardinality_policy: str
    :param unresolved_model_element_policy: Handle unresolved diagrammatic
                                            ``modelElement`` references with
                                            ``preserve``, ``omit``, or
                                            ``error``. Default is ``omit``.
    :type unresolved_model_element_policy: str
    :param transformation_metadata: Return no provenance with ``none`` or add
                                    it to the graph with ``embedded``. Sidecar
                                    output is not available through the library.
    :type transformation_metadata: str
    :param append_content_hash: Append the deterministic content UUID below a
                                supplied ``base_uri``.
    :type append_content_hash: bool
    :param path_order_policy: Handle path-point order with ``warn`` or add a
                              non-normative ``rdfs:comment`` with ``comment``.
                              Default is ``warn``.
    :type path_order_policy: str
    :param property_assignment_policy: Handle non-empty ``propertyAssignments``
                                       with ``warn`` or preserve canonical JSON
                                       in a non-normative comment with
                                       ``comment``. Default is ``warn``.
    :type property_assignment_policy: str
    :return: Decoded RDF graph.
    :rtype: Graph
    :raises ValueError: If an option is invalid or an ``error`` policy rejects
                        source content.
    :raises OSError: If the input file cannot be read.
    """
    decoded_graph_project = decode_ontouml_json2graph(
        json_file_path=json_file_path,
        base_uri=base_uri,
        language=language,
        model_only=False,
        silent=True,
        correct=correct,
        execution_mode="import",
        invalid_cardinality_policy=invalid_cardinality_policy,
        invalid_stereotype_policy=invalid_stereotype_policy,
        unresolved_model_element_policy=unresolved_model_element_policy,
        transformation_metadata=transformation_metadata,
        append_content_hash=append_content_hash,
        path_order_policy=path_order_policy,
        property_assignment_policy=property_assignment_policy,
    )

    return decoded_graph_project


def decode_json_model(
    json_file_path: str,
    base_uri: str | None = None,
    language: str = "",
    correct: bool = False,
    invalid_stereotype_policy: str = "preserve",
    invalid_cardinality_policy: str = "preserve",
    unresolved_model_element_policy: str = "omit",
    transformation_metadata: str = "none",
    append_content_hash: bool = False,
    path_order_policy: str = "warn",
    property_assignment_policy: str = "warn",
) -> Graph:
    """Decode the domain-level model from an OntoUML JSON project.

    The returned RDFLib graph excludes project and diagrammatic resources while
    retaining model elements, including enumeration literals. The decoder
    expects the OntoUML JSON structure but does not perform JSON Schema
    validation.

    :param json_file_path: Path to the OntoUML JSON file.
    :type json_file_path: str
    :param base_uri: Explicit absolute base URI for generated resources. When
                     omitted, a deterministic ``urn:uuid:`` base is derived
                     from the parsed JSON document.
    :type base_uri: str or None
    :param language: Language tag applied to source ``name`` literals. An empty
                     string leaves names without a language tag.
    :type language: str
    :param correct: Enable the legacy class and property correction pass. This
                    is independent of the explicit policy parameters.
    :type correct: bool
    :param invalid_stereotype_policy: Handle stereotypes invalid for their
                                      element type with ``preserve``, ``omit``,
                                      or ``error``. Default is ``preserve``.
    :type invalid_stereotype_policy: str
    :param invalid_cardinality_policy: Handle invalid cardinalities with
                                       ``preserve``, limited safe ``repair``,
                                       or ``error``. Default is ``preserve``.
    :type invalid_cardinality_policy: str
    :param unresolved_model_element_policy: Handle unresolved diagrammatic
                                            ``modelElement`` references with
                                            ``preserve``, ``omit``, or
                                            ``error``. Default is ``omit``.
    :type unresolved_model_element_policy: str
    :param transformation_metadata: Return no provenance with ``none`` or add
                                    it to the graph with ``embedded``. Sidecar
                                    output is not available through the library.
    :type transformation_metadata: str
    :param append_content_hash: Append the deterministic content UUID below a
                                supplied ``base_uri``.
    :type append_content_hash: bool
    :param path_order_policy: Accepted for parity with project decoding.
                              Model-only output contains no paths, so this
                              option does not change the graph.
    :type path_order_policy: str
    :param property_assignment_policy: Handle non-empty ``propertyAssignments``
                                       on retained model elements with ``warn``
                                       or ``comment``. Default is ``warn``.
    :type property_assignment_policy: str
    :return: Decoded model-only RDF graph.
    :rtype: Graph
    :raises ValueError: If an option is invalid or an ``error`` policy rejects
                        source content.
    :raises OSError: If the input file cannot be read.
    """
    decoded_graph_model = decode_ontouml_json2graph(
        json_file_path=json_file_path,
        base_uri=base_uri,
        language=language,
        model_only=True,
        silent=True,
        correct=correct,
        execution_mode="import",
        invalid_cardinality_policy=invalid_cardinality_policy,
        invalid_stereotype_policy=invalid_stereotype_policy,
        unresolved_model_element_policy=unresolved_model_element_policy,
        transformation_metadata=transformation_metadata,
        append_content_hash=append_content_hash,
        path_order_policy=path_order_policy,
        property_assignment_policy=property_assignment_policy,
    )

    return decoded_graph_model


def save_graph_file(ontouml_graph: Graph, output_file_path: str, syntax: str) -> None:
    """Serialize an RDFLib graph to the requested file.

    Accepted syntax names are ``turtle``, ``ttl``, ``turtle2``, ``xml``,
    ``pretty-xml``, ``json-ld``, ``ntriples``, ``nt``, ``nt11``, ``n3``,
    ``trig``, ``trix``, and ``nquads``.

    :param ontouml_graph: Graph to serialize.
    :type ontouml_graph: Graph
    :param output_file_path: Complete destination path, including filename and
                             extension.
    :type output_file_path: str
    :param syntax: Supported RDFLib serialization name.
    :type syntax: str
    :raises ValueError: If ``syntax`` is not supported.
    :raises OSError: If the output file cannot be written.
    """
    valid_syntaxes = [
        "turtle",
        "ttl",
        "turtle2",
        "xml",
        "pretty-xml",
        "json-ld",
        "ntriples",
        "nt",
        "nt11",
        "n3",
        "trig",
        "trix",
        "nquads",
    ]

    if syntax not in valid_syntaxes:
        report_error_requirement_not_met("Invalid syntax used as argument.")
    else:
        safe_write_graph_file(ontouml_graph, output_file_path, syntax)
