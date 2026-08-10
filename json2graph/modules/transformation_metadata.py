"""Build optional provenance metadata for OntoUML JSON transformations."""

import hashlib
import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Mapping

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef, XSD

from .metadata import METADATA
from .utils_graph import load_ontouml_vocabulary

TRANSFORMATION_METADATA_MODES = ("none", "embedded", "sidecar")

DCTERMS = Namespace("http://purl.org/dc/terms/")
PROV = Namespace("http://www.w3.org/ns/prov#")

ONTOUML_VOCABULARY_VERSION_IRI = URIRef(f"{METADATA['conformsTo']}/vocabulary/{METADATA['conformsToVersion']}")

IANA_MEDIA_TYPE_BASE = "https://www.iana.org/assignments/media-types/"
JSON_MEDIA_TYPE = URIRef(IANA_MEDIA_TYPE_BASE + "application/json")

# Only registered IANA media types are included. RDFLib's TriX serializer has
# no corresponding registered media type, so its format statement is omitted.
RDF_MEDIA_TYPES = {
    "turtle": "text/turtle",
    "ttl": "text/turtle",
    "turtle2": "text/turtle",
    "xml": "application/rdf+xml",
    "pretty-xml": "application/rdf+xml",
    "json-ld": "application/ld+json",
    "ntriples": "application/n-triples",
    "nt": "application/n-triples",
    "nt11": "application/n-triples",
    "n3": "text/n3",
    "trig": "application/trig",
    "nquads": "application/n-quads",
}

CONFIGURATION_FIELDS = (
    "language",
    "model_only",
    "correct",
    "invalid_cardinality_policy",
    "invalid_stereotype_policy",
    "transformation_metadata",
    "unresolved_model_element_policy",
)


def get_transformation_configuration(
    arguments: Mapping[str, object],
    graph_format: str | None,
) -> dict[str, object]:
    """Return the requested and effective output options as a stable dictionary."""
    configuration = {
        "append_content_hash": arguments["append_content_hash"],
        "base_uri": arguments["base_uri_input"],
        "effective_base_uri": arguments["base_uri"],
        "format": graph_format,
    }
    configuration.update({field: arguments[field] for field in CONFIGURATION_FIELDS})
    return configuration


def get_rdf_media_type(graph_format: str) -> URIRef | None:
    """Return the registered IANA media-type URI for an RDFLib serialization name."""
    media_type = RDF_MEDIA_TYPES.get(graph_format)
    if media_type is None:
        return None
    return URIRef(IANA_MEDIA_TYPE_BASE + media_type)


def _sha256_identifier(input_file_path: str) -> str:
    """Return a SHA-256 identifier for an input file without exposing its path."""
    digest = hashlib.sha256()
    with open(input_file_path, "rb") as input_file:
        for chunk in iter(lambda: input_file.read(65536), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


@lru_cache(maxsize=1)
def _defined_ontouml_terms() -> frozenset[URIRef]:
    """Return the terms declared by the bundled OntoUML Vocabulary revision."""
    vocabulary_graph = load_ontouml_vocabulary()
    namespace = METADATA["conformsToBase"]
    return frozenset(
        subject
        for subject in vocabulary_graph.subjects()
        if isinstance(subject, URIRef) and str(subject).startswith(namespace)
    )


def uses_only_declared_ontouml_terms(ontouml_graph: Graph) -> bool:
    """Check that every used OntoUML predicate and object term is declared."""
    namespace = METADATA["conformsToBase"]
    used_terms = {
        term
        for _, predicate, obj in ontouml_graph
        for term in (predicate, obj)
        if isinstance(term, URIRef) and str(term).startswith(namespace)
    }
    return used_terms.issubset(_defined_ontouml_terms())


def build_transformation_metadata(
    ontouml_graph: Graph,
    input_file_path: str,
    output_file_name: str,
    graph_format: str,
    configuration: Mapping[str, object],
    generated_at: datetime | None = None,
) -> Graph:
    """Describe the output artifact and the activity that generated it."""
    metadata_graph = Graph()
    metadata_graph.bind("dct", DCTERMS)
    metadata_graph.bind("prov", PROV)
    metadata_graph.bind("xsd", XSD)

    output_artifact = BNode("output-artifact")
    transformation = BNode("transformation-activity")
    source_artifact = BNode("source-artifact")
    software_agent = BNode("software-agent")
    configuration_entity = BNode("transformation-configuration")

    generation_time = generated_at or datetime.now(timezone.utc)
    generation_time = generation_time.astimezone(timezone.utc)
    generation_literal = Literal(generation_time.isoformat().replace("+00:00", "Z"), datatype=XSD.dateTime)

    metadata_graph.add((output_artifact, RDF.type, PROV.Entity))
    metadata_graph.add((output_artifact, DCTERMS.title, Literal(output_file_name)))
    metadata_graph.add((output_artifact, PROV.wasGeneratedBy, transformation))
    metadata_graph.add((output_artifact, PROV.generatedAtTime, generation_literal))

    output_media_type = get_rdf_media_type(graph_format)
    if output_media_type is not None:
        metadata_graph.add((output_artifact, DCTERMS["format"], output_media_type))

    if uses_only_declared_ontouml_terms(ontouml_graph):
        metadata_graph.add((output_artifact, DCTERMS.conformsTo, ONTOUML_VOCABULARY_VERSION_IRI))

    metadata_graph.add((transformation, RDF.type, PROV.Activity))
    metadata_graph.add((transformation, DCTERMS.title, Literal("OntoUML JSON-to-RDF transformation")))
    metadata_graph.add((transformation, PROV.used, source_artifact))
    metadata_graph.add((transformation, PROV.used, configuration_entity))
    metadata_graph.add((transformation, PROV.wasAssociatedWith, software_agent))

    metadata_graph.add((source_artifact, RDF.type, PROV.Entity))
    metadata_graph.add((source_artifact, DCTERMS.title, Literal(Path(input_file_path).name)))
    metadata_graph.add((source_artifact, DCTERMS.identifier, Literal(_sha256_identifier(input_file_path))))
    metadata_graph.add((source_artifact, DCTERMS["format"], JSON_MEDIA_TYPE))

    metadata_graph.add((software_agent, RDF.type, PROV.SoftwareAgent))
    metadata_graph.add((software_agent, DCTERMS.title, Literal(METADATA["Name"])))
    metadata_graph.add(
        (
            software_agent,
            DCTERMS.identifier,
            Literal(f"{METADATA['Name']}/{METADATA['Version']}"),
        )
    )

    canonical_configuration = json.dumps(
        dict(configuration),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    metadata_graph.add((configuration_entity, RDF.type, PROV.Entity))
    metadata_graph.add((configuration_entity, DCTERMS["format"], JSON_MEDIA_TYPE))
    metadata_graph.add((configuration_entity, PROV.value, Literal(canonical_configuration)))

    return metadata_graph


def graph_with_metadata(ontouml_graph: Graph, metadata_graph: Graph) -> Graph:
    """Return a graph containing model and metadata triples without mutating the model graph."""
    combined_graph = Graph()
    for prefix, namespace in ontouml_graph.namespaces():
        combined_graph.bind(prefix, namespace)
    combined_graph += ontouml_graph
    combined_graph += metadata_graph
    return combined_graph
