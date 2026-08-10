"""Handle property assignments that the OntoUML Vocabulary cannot represent."""

import json
import warnings
from dataclasses import dataclass

from rdflib import Graph, Literal, RDFS, URIRef

PROPERTY_ASSIGNMENT_POLICIES = ("warn", "comment")


class PropertyAssignmentWarning(UserWarning):
    """Warn that property assignments have no formal vocabulary representation."""


@dataclass(frozen=True)
class PropertyAssignmentRecord:
    """Preserve one source element's non-empty property-assignment map."""

    element_id: str
    element_type: str
    canonical_json: str
    keys: tuple[str, ...]


def collect_property_assignments(json_data: object) -> list[PropertyAssignmentRecord]:
    """Collect non-empty property-assignment maps before null cleanup mutates the source data."""
    records = []

    def visit(value: object) -> None:
        if isinstance(value, dict):
            assignments = value.get("propertyAssignments")
            element_id = value.get("id")
            if isinstance(assignments, dict) and assignments and isinstance(element_id, str):
                records.append(
                    PropertyAssignmentRecord(
                        element_id=element_id,
                        element_type=str(value.get("type", "Element")),
                        canonical_json=json.dumps(
                            assignments,
                            ensure_ascii=False,
                            separators=(",", ":"),
                            sort_keys=True,
                        ),
                        keys=tuple(sorted(assignments)),
                    )
                )

            for nested_value in value.values():
                visit(nested_value)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(json_data)
    return records


def apply_property_assignment_policy(
    records: list[PropertyAssignmentRecord],
    ontouml_graph: Graph,
    policy: str,
    input_path: str,
    base_uri: str,
) -> None:
    """Warn about omitted assignments or preserve them as non-normative textual annotations."""
    if policy not in PROPERTY_ASSIGNMENT_POLICIES:
        raise ValueError(
            f"Invalid property assignment policy '{policy}'. Valid values are: "
            f"{list(PROPERTY_ASSIGNMENT_POLICIES)}."
        )

    affected_records = [
        record
        for record in records
        if next(ontouml_graph.triples((URIRef(base_uri + record.element_id), None, None)), None) is not None
    ]
    if not affected_records:
        return

    affected_elements = "; ".join(
        f"{record.element_type} ID '{record.element_id}' (keys: {', '.join(record.keys)})"
        for record in affected_records
    )

    if policy == "comment":
        ontouml_graph.bind("rdfs", RDFS)
        for record in affected_records:
            ontouml_graph.add(
                (
                    URIRef(base_uri + record.element_id),
                    RDFS.comment,
                    Literal(f"Source JSON propertyAssignments: {record.canonical_json}"),
                )
            )
        action = (
            "The source maps were added as non-normative rdfs:comment annotations because the property assignment "
            "policy is 'comment'; they still have no formal OntoUML Vocabulary semantics."
        )
    else:
        action = "The assignments were omitted because the property assignment policy is 'warn'."

    warnings.warn(
        f"Input file '{input_path}': {len(affected_records)} converted element(s) contain non-empty "
        f"propertyAssignments maps that the OntoUML Vocabulary does not represent: {affected_elements}. {action}",
        PropertyAssignmentWarning,
        stacklevel=2,
    )
