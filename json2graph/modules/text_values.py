"""Validation helpers for legacy textual values on diagrammatic Text shapes."""

import warnings


class UnsupportedTextValueWarning(UserWarning):
    """Warn that a Text shape contains content unsupported by the vocabulary."""


def warn_if_text_value_is_unsupported(text_shape: dict) -> None:
    """Warn when a legacy Text shape contains a non-empty ``value`` field.

    OntoUML Vocabulary v1.1.1 represents ``ontouml:Text`` as a diagrammatic
    shape and does not define a data property for content stored directly on
    that shape. Empty legacy values carry no information and are omitted
    silently. Non-empty values are also omitted, but produce an explicit
    warning so that source information is never discarded silently.

    :param text_shape: Text shape dictionary being decoded.
    :type text_shape: dict
    """
    value = text_shape.get("value")

    if value not in (None, ""):
        warnings.warn(
            f"Text shape '{text_shape['id']}' contains unsupported non-empty field 'value' ({value!r}). "
            "OntoUML Vocabulary v1.1.1 does not define a property for Text shape content, so the value was omitted.",
            UnsupportedTextValueWarning,
            stacklevel=3,
        )
