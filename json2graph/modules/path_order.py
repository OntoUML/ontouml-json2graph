"""Handle path-point order that the OntoUML Vocabulary cannot represent."""

import warnings
from collections.abc import Iterable

from rdflib import Graph, Literal, RDFS, URIRef

PATH_ORDER_POLICIES = ("warn", "comment")


class PathPointOrderWarning(UserWarning):
    """Warn that path-point order is absent from the vocabulary-defined graph structure."""


def _format_point_sequence(points: Iterable[dict]) -> str:
    """Return a deterministic, human-readable sequence of source coordinates."""
    return " -> ".join(f"({point['x']}, {point['y']})" for point in points)


def apply_path_order_policy(
    path_dicts: list[dict],
    ontouml_graph: Graph,
    policy: str,
    input_path: str,
    base_uri: str,
    model_only: bool,
) -> None:
    """Warn about path-point order loss or preserve it as a non-normative textual annotation."""
    if policy not in PATH_ORDER_POLICIES:
        raise ValueError(f"Invalid path order policy '{policy}'. Valid values are: {list(PATH_ORDER_POLICIES)}.")

    if model_only:
        return

    affected_paths = [path_dict for path_dict in path_dicts if len(path_dict.get("points", [])) > 1]
    if not affected_paths:
        return

    first_path_id = affected_paths[0]["id"]
    if policy == "comment":
        ontouml_graph.bind("rdfs", RDFS)
        for path_dict in affected_paths:
            point_sequence = _format_point_sequence(path_dict["points"])
            ontouml_graph.add(
                (
                    URIRef(base_uri + path_dict["id"]),
                    RDFS.comment,
                    Literal(f"Source JSON path point order: {point_sequence}."),
                )
            )
        action = (
            "The source sequences were added as non-normative rdfs:comment annotations because the path order "
            "policy is 'comment'."
        )
    else:
        action = "The point triples were emitted without order because the path order policy is 'warn'."

    warnings.warn(
        f"Input file '{input_path}': {len(affected_paths)} Path object(s) contain ordered point sequences that "
        f"the OntoUML Vocabulary does not represent (first affected Path ID: '{first_path_id}'). {action}",
        PathPointOrderWarning,
        stacklevel=2,
    )
