"""Validate OntoUML cardinalities and apply the configured handling policy."""

import re
import warnings

INVALID_CARDINALITY_POLICIES = ("preserve", "repair", "error")

_EXACT_CARDINALITY = re.compile(r"^[0-9]+$")
_RANGE_CARDINALITY = re.compile(r"^(?P<lower>[0-9]+)\.\.(?P<upper>[0-9]+|\*)$")
_REPAIR_PATTERNS = (
    (re.compile(r"^(?P<lower>[0-9]+),,(?P<upper>[0-9]+|\*)$"), "{lower}..{upper}"),
    (re.compile(r"^(?P<lower>[0-9]+):(?P<upper>[0-9]+|\*)$"), "{lower}..{upper}"),
    (re.compile(r"^(?P<lower>[0-9]+)\.{3}(?P<upper>[0-9]+|\*)$"), "{lower}..{upper}"),
    (re.compile(r"^(?P<lower>[0-9]+)\.\.$"), "{lower}..*"),
)


class InvalidCardinalityWarning(UserWarning):
    """Warn that an invalid cardinality was preserved without inferred bounds."""


class CardinalityRepairWarning(UserWarning):
    """Warn that a known malformed cardinality pattern was repaired."""


class InvalidCardinalityError(ValueError):
    """Report that error policy rejected an invalid cardinality."""


def _parse_valid_cardinality(cardinality: str) -> tuple[str, str, str] | None:
    """Return a normalized cardinality and its bounds, or None when invalid."""
    if cardinality == "*":
        return "0..*", "0", "*"

    if _EXACT_CARDINALITY.fullmatch(cardinality):
        return f"{cardinality}..{cardinality}", cardinality, cardinality

    match = _RANGE_CARDINALITY.fullmatch(cardinality)
    if match is None:
        return None

    lower_bound = match.group("lower")
    upper_bound = match.group("upper")
    if upper_bound != "*" and int(lower_bound) > int(upper_bound):
        return None

    return cardinality, lower_bound, upper_bound


def _repair_cardinality(cardinality: str) -> tuple[str, str, str] | None:
    """Repair only malformed separator patterns observed in the audited corpus."""
    for pattern, replacement in _REPAIR_PATTERNS:
        match = pattern.fullmatch(cardinality)
        if match is None:
            continue

        repaired = replacement.format(**match.groupdict())
        return _parse_valid_cardinality(repaired)

    return None


def resolve_cardinality(
    cardinality: str,
    property_id: str,
    policy: str,
) -> tuple[str, str | None, str | None]:
    """Resolve a source cardinality according to the selected invalid-value policy."""
    if policy not in INVALID_CARDINALITY_POLICIES:
        raise ValueError(
            f"Invalid cardinality policy '{policy}'. Valid values are: {list(INVALID_CARDINALITY_POLICIES)}."
        )

    parsed = _parse_valid_cardinality(cardinality)
    if parsed is not None:
        return parsed

    message = f"Property with ID '{property_id}' has invalid cardinality value '{cardinality}'."

    if policy == "error":
        raise InvalidCardinalityError(
            f"{message} Transformation aborted because the invalid cardinality policy is 'error'."
        )

    if policy == "repair":
        repaired = _repair_cardinality(cardinality)
        if repaired is not None:
            repaired_value, lower_bound, upper_bound = repaired
            warnings.warn(
                f"{message} It was repaired to '{repaired_value}' because the invalid cardinality policy is "
                "'repair'.",
                CardinalityRepairWarning,
                stacklevel=2,
            )
            return repaired

        action = (
            "It could not be safely repaired. The original cardinalityValue was preserved and lowerBound and "
            "upperBound were omitted."
        )
    else:
        action = "The original cardinalityValue was preserved and lowerBound and upperBound were omitted."

    warnings.warn(
        f"{message} {action} The invalid cardinality policy is '{policy}'.",
        InvalidCardinalityWarning,
        stacklevel=2,
    )
    return cardinality, None, None
