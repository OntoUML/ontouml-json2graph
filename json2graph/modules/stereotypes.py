"""Normalize OntoUML stereotypes and apply the configured handling policy."""

import re
import warnings

from rdflib import Graph, URIRef

from .utils_graph import ontouml_ref

INVALID_STEREOTYPE_POLICIES = ("preserve", "omit", "error")

CLASS_STEREOTYPES = frozenset(
    {
        "abstract",
        "category",
        "collective",
        "datatype",
        "enumeration",
        "event",
        "historicalRole",
        "historicalRoleMixin",
        "kind",
        "mixin",
        "mode",
        "phase",
        "phaseMixin",
        "quality",
        "quantity",
        "relator",
        "role",
        "roleMixin",
        "situation",
        "subkind",
        "type",
    }
)

RELATION_STEREOTYPES = frozenset(
    {
        "bringsAbout",
        "characterization",
        "comparative",
        "componentOf",
        "creation",
        "derivation",
        "externalDependence",
        "historicalDependence",
        "instantiation",
        "manifestation",
        "material",
        "mediation",
        "memberOf",
        "participation",
        "participational",
        "subCollectionOf",
        "subQuantityOf",
        "termination",
        "triggers",
    }
)

PROPERTY_STEREOTYPES = frozenset({"begin", "end"})

VALID_STEREOTYPES = CLASS_STEREOTYPES | RELATION_STEREOTYPES | PROPERTY_STEREOTYPES


class InvalidStereotypeWarning(UserWarning):
    """Warn that a stereotype is absent from the OntoUML stereotype list."""


class InvalidStereotypeError(ValueError):
    """Report that error policy rejected a nonexistent stereotype."""


def normalize_stereotype(stereotype: str) -> str:
    """Convert a stereotype value to lowerCamelCase for use as an IRI fragment."""
    words = re.findall(
        r"[A-Z]+(?=[A-Z][a-z]|[0-9]|$)|[A-Z]?[a-z]+|[0-9]+",
        stereotype.strip(),
    )
    if not words:
        return ""

    first_word = words[0].lower()
    return first_word + "".join(word.lower().capitalize() for word in words[1:])


def set_stereotype_relation(element_dict: dict, ontouml_graph: Graph, policy: str, base_uri: str) -> None:
    """Normalize and set an element's stereotype according to the selected policy."""
    if policy not in INVALID_STEREOTYPE_POLICIES:
        raise ValueError(
            f"Invalid stereotype policy '{policy}'. Valid values are: {list(INVALID_STEREOTYPE_POLICIES)}."
        )

    original_stereotype = element_dict["stereotype"]
    normalized_stereotype = normalize_stereotype(original_stereotype)
    stereotype_exists = normalized_stereotype in VALID_STEREOTYPES

    if not stereotype_exists:
        element_type = element_dict["type"]
        element_id = element_dict["id"]
        message = (
            f"{element_type} with ID '{element_id}' has stereotype '{original_stereotype}', normalized as "
            f"'{normalized_stereotype}', which is not in the recognized OntoUML stereotype list."
        )

        if policy == "error":
            raise InvalidStereotypeError(f"{message} Transformation aborted.")

        action = "preserved" if policy == "preserve" else "omitted"
        warnings.warn(
            f"{message} The stereotype triple was {action} because the invalid stereotype policy is '{policy}'.",
            InvalidStereotypeWarning,
            stacklevel=2,
        )

        if policy == "omit":
            return

    element_uri = URIRef(base_uri + element_dict["id"])
    ontouml_graph.add((element_uri, ontouml_ref("stereotype"), ontouml_ref(normalized_stereotype)))
