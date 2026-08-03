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

STEREOTYPES_BY_ELEMENT_TYPE = {
    "Class": CLASS_STEREOTYPES,
    "Relation": RELATION_STEREOTYPES,
    "Property": PROPERTY_STEREOTYPES,
}


class InvalidStereotypeWarning(UserWarning):
    """Warn that a stereotype is invalid for its assigned element type."""


class InvalidStereotypeError(ValueError):
    """Report that error policy rejected an invalid stereotype assignment."""


class StereotypeNormalizationWarning(UserWarning):
    """Warn that a lexical stereotype variant was normalized to its canonical value."""


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

    element_type = element_dict["type"]
    original_stereotype = element_dict["stereotype"]
    normalized_stereotype = normalize_stereotype(original_stereotype)
    valid_stereotypes = STEREOTYPES_BY_ELEMENT_TYPE.get(element_type, frozenset())
    stereotype_is_valid = normalized_stereotype in valid_stereotypes

    if not stereotype_is_valid:
        element_id = element_dict["id"]
        recognized_element_types = [
            recognized_type
            for recognized_type, stereotypes in STEREOTYPES_BY_ELEMENT_TYPE.items()
            if normalized_stereotype in stereotypes
        ]

        if recognized_element_types:
            recognition_details = (
                f" It is recognized for {', '.join(recognized_element_types)}, but not for {element_type}."
            )
        else:
            recognition_details = " It is not recognized for any supported element type."

        message = (
            f"{element_type} with ID '{element_id}' has stereotype '{original_stereotype}', normalized as "
            f"'{normalized_stereotype}', which is not valid for {element_type}.{recognition_details}"
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

    elif original_stereotype != normalized_stereotype:
        warnings.warn(
            f"{element_type} with ID '{element_dict['id']}' has stereotype '{original_stereotype}', which was "
            f"normalized to the canonical {element_type} stereotype '{normalized_stereotype}'.",
            StereotypeNormalizationWarning,
            stacklevel=2,
        )

    element_uri = URIRef(base_uri + element_dict["id"])
    ontouml_graph.add((element_uri, ontouml_ref("stereotype"), ontouml_ref(normalized_stereotype)))
