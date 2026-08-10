"""Create deterministic, content-derived namespaces for OntoUML JSON documents."""

import hashlib
import json
import uuid
from typing import Any
from urllib.parse import urlsplit

# This namespace is derived once from the JSON2Graph persistent project URI with
# uuid.uuid5(uuid.NAMESPACE_URL, "https://w3id.org/ontouml/json2graph"). It is a
# permanent part of the content-identity algorithm and must not be changed.
JSON2GRAPH_NAMESPACE_UUID = uuid.UUID("3f6e741a-4a05-5962-83d0-343fc9d7dc22")


def canonicalize_json(json_data: Any) -> str:
    """Serialize parsed JSON deterministically while preserving array order."""
    return json.dumps(
        json_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def create_content_uuid(json_data: Any) -> uuid.UUID:
    """Return the deterministic UUIDv5 assigned to canonical JSON content."""
    canonical_json = canonicalize_json(json_data)
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return uuid.uuid5(JSON2GRAPH_NAMESPACE_UUID, digest)


def normalize_base_uri(base_uri: str) -> str:
    """Validate an explicit absolute base URI and ensure an identifier separator."""
    if not isinstance(base_uri, str) or not base_uri or any(character.isspace() for character in base_uri):
        raise ValueError("Base URI must be a non-empty absolute URI without whitespace.")

    parsed_uri = urlsplit(base_uri)
    if not parsed_uri.scheme:
        raise ValueError("Base URI must be an absolute URI with a scheme.")
    if parsed_uri.scheme.lower() in ("http", "https") and not parsed_uri.netloc:
        raise ValueError("HTTP(S) base URI must include a host.")

    if base_uri.endswith(("#", "/")):
        return base_uri
    return f"{base_uri}#"


def resolve_base_uri(
    json_data: Any,
    base_uri: str | None = None,
    append_content_hash: bool = False,
) -> str:
    """Resolve the effective base URI from canonical JSON and user options."""
    content_uuid = create_content_uuid(json_data)

    if base_uri is None:
        return f"urn:uuid:{content_uuid}#"

    normalized_base_uri = normalize_base_uri(base_uri)
    if not append_content_hash:
        return normalized_base_uri

    parsed_uri = urlsplit(base_uri)
    if parsed_uri.query or parsed_uri.fragment:
        raise ValueError("A base URI with a content ID cannot contain a query or non-empty fragment.")

    parent_uri = base_uri.rstrip("/#")
    return f"{parent_uri}/{content_uuid}#"
