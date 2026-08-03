"""Validate diagrammatic references to model elements and apply the configured policy."""

import warnings

UNRESOLVED_MODEL_ELEMENT_POLICIES = ("preserve", "omit", "error")


class UnresolvedModelElementWarning(UserWarning):
    """Warn that an ElementView references an element absent from the project model."""


class UnresolvedModelElementError(ValueError):
    """Report that error policy rejected an unresolved modelElement reference."""


def _collect_model_element_ids(model_package: dict) -> set[str]:
    """Collect IDs of elements canonically defined by Package.contents containment.

    Reference dictionaries elsewhere in the JSON are deliberately excluded so
    that a dangling reference cannot make itself appear resolved.
    """
    model_element_ids = set()

    package_id = model_package.get("id")
    if isinstance(package_id, str):
        model_element_ids.add(package_id)

    for model_element in model_package.get("contents", []):
        if not isinstance(model_element, dict):
            continue

        model_element_id = model_element.get("id")
        if isinstance(model_element_id, str):
            model_element_ids.add(model_element_id)

        if model_element.get("type") == "Package":
            model_element_ids.update(_collect_model_element_ids(model_element))

    return model_element_ids


def apply_unresolved_model_element_policy(
    project_data: dict,
    policy: str,
    input_path: str,
) -> None:
    """Handle unresolved ElementView.modelElement references according to policy.

    Only ``modelElement`` references on objects contained by diagrams are
    evaluated. Other reference categories, including ``source``, ``target``,
    ``propertyType``, ``general``, and ``specific``, are outside this policy.

    :param project_data: Cleaned OntoUML Project dictionary to validate.
    :type project_data: dict
    :param policy: One of ``preserve``, ``omit``, or ``error``.
    :type policy: str
    :param input_path: Path of the JSON file containing the reference.
    :type input_path: str
    """
    if policy not in UNRESOLVED_MODEL_ELEMENT_POLICIES:
        raise ValueError(
            f"Invalid unresolved modelElement policy '{policy}'. Valid values are: "
            f"{list(UNRESOLVED_MODEL_ELEMENT_POLICIES)}."
        )

    model_package = project_data.get("model")
    if not isinstance(model_package, dict):
        model_element_ids = set()
    else:
        model_element_ids = _collect_model_element_ids(model_package)

    for diagram in project_data.get("diagrams", []):
        if not isinstance(diagram, dict):
            continue

        for element_view in diagram.get("contents", []):
            if not isinstance(element_view, dict):
                continue

            model_element = element_view.get("modelElement")
            if not isinstance(model_element, dict):
                continue

            referenced_id = model_element.get("id")
            if not isinstance(referenced_id, str) or referenced_id in model_element_ids:
                continue

            element_view_type = element_view.get("type", "ElementView")
            element_view_id = element_view.get("id", "unknown")
            referenced_type = model_element.get("type", "unknown")
            message = (
                f"Input file '{input_path}': {element_view_type} with ID '{element_view_id}' has unresolved "
                f"modelElement reference '{referenced_id}' (declared type '{referenced_type}'), which is not "
                f"defined in the project's model contents."
            )

            if policy == "error":
                raise UnresolvedModelElementError(
                    f"{message} Transformation aborted because the unresolved modelElement policy is 'error'."
                )

            if policy == "omit":
                element_view.pop("modelElement")
                action = (
                    "The reference was omitted and the unresolved target was not materialized, while the "
                    "ElementView was preserved"
                )
            else:
                action = "The reference was preserved and the unresolved target was materialized"

            warnings.warn(
                f"{message} {action} because the unresolved modelElement policy is '{policy}'.",
                UnresolvedModelElementWarning,
                stacklevel=2,
            )
