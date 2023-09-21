"""Util functions related to graphs."""
import os
import urllib

from rdflib import Graph, URIRef

from .errors import report_error_io_read
from .logger import initialize_logger
from .metadata import METADATA

LOGGER = initialize_logger()


def ontouml_ref(entity: str) -> URIRef:
    """Receive the name of the OntoUML Vocabulary's entity as a string and returns the corresponding URIRef.

    :param entity: OntoUML Vocabulary entity (class, property, or individual) to have its URIRef returned.
    :type entity: str
    :return: URIRef of the informed OntoUML Vocabulary's entity.
    :rtype: URIRef
    """
    entity_uri = METADATA["conformsTo"] + "#" + entity

    entity_uriref = URIRef(entity_uri)

    return entity_uriref


def load_ontouml_vocabulary(enable_remote: bool = False) -> Graph:
    """Load the OntoUML Vocabulary to the working memory.

    If the argument enable_remote is enabled (i.e., equals True), it first tries to load from web resource, if fails,
    it tries to load form the local resource. If both options fail, calls error reporting function.

    If the argument enable_remote is disabled, the function tries to load form the local resource and if fails,
    it calls the error reporting function.

    The enable_remote is disabled by default as it can significantly decrease the software performance.
    However, using it can guarantee that the most recent version of vocabulary is always used.

    :param enable_remote: Controls if the software will try to get the ontouml vocabulary ttl file from a remote source.
    :type enable_remote: bool
    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """
    ontology_graph = Graph()

    # Guarantees that the file will be found as it searches using this file as basis
    package_dir = os.path.dirname(os.path.dirname(__file__))
    file_location = "resources" + os.path.sep + "ontouml_" + METADATA["conformsToVersion"] + ".ttl"
    file_path = os.path.join(package_dir, file_location)

    if enable_remote:
        remote_option = "https://w3id.org/ontouml/vocabulary/" + METADATA["conformsToVersion"]
        try:
            ontology_graph.parse(remote_option, encoding="utf-8", format="ttl")
            LOGGER.debug("OntoUML Vocabulary successfully loaded to working memory from REMOTE option.")
        except Exception:
            LOGGER.debug("OntoUML Vocabulary successfully loaded to working memory from LOCAL option.")
            ontology_graph = load_graph_safely(file_path, "ttl")
    else:
        LOGGER.debug("OntoUML Vocabulary successfully loaded to working memory from LOCAL option.")
        ontology_graph = load_graph_safely(file_path, "ttl")

    return ontology_graph


def load_graph_safely(ontology_file: str, out_format: str = "not_provided") -> Graph:
    """Safely load graph from file to working memory using arguments provided by the user, which are the file path \
    and (optionally) the file type.

    :param ontology_file: Path to the ontology file to be loaded into the working memory.
    :type ontology_file: str
    :param out_format: Optional argument. Format of the file to be loaded.
    :type out_format: str
    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """
    ontology_graph = Graph()

    try:
        if out_format == "not_provided":
            ontology_graph.parse(ontology_file, encoding="utf-8")
        else:
            ontology_graph.parse(ontology_file, encoding="utf-8", format=out_format)
    except OSError as error:
        file_description = "input ontology file"
        report_error_io_read(ontology_file, file_description, error)

    LOGGER.debug(f"Ontology file {ontology_file} successfully loaded to working memory.")

    return ontology_graph


def fix_uri(url_string: str) -> str:
    """Received a valid URL, but invalid URI string and converts to a valid URL and valid URI string.

    This function takes a URL string, parses it, encodes non-URI characters, and reconstructs a valid URI.

    :param url_string: The URL string to be fixed.
    :type url_string: str
    :return: The resulting valid URI string.
    :rtype: str
    """
    # Step 1: Parse the URL
    parsed_url = urllib.parse.urlparse(url_string)

    # Step 2: URL Encode Non-URI Characters
    # Encode non-ASCII characters and spaces in the path and query components
    encoded_path = urllib.parse.quote(parsed_url.path)
    encoded_query = urllib.parse.quote(parsed_url.query)
    encoded_scheme = urllib.parse.quote(parsed_url.scheme)
    encoded_netloc = urllib.parse.quote(parsed_url.netloc)
    encoded_fragment = urllib.parse.quote(parsed_url.fragment)

    # Step 3: Reconstruct the URI
    valid_uri = urllib.parse.urlunparse(
        (
            encoded_scheme,
            encoded_netloc,
            encoded_path,
            "",  # Empty string for params
            encoded_query,
            encoded_fragment,
        )
    )

    return valid_uri


def rename_uriref_resource(graph: Graph, old_resource: URIRef, new_resource: URIRef) -> None:
    """Rename a URIRef resource of an RDF graph by replacing it to a new one with a different name.

    :param graph: The RDF graph that contains the resource to be renamed.
    :type graph: Graph
    :param old_resource: The old resource to be replaced.
    :type old_resource: URIRef
    :param new_resource: The new resource to replace the old one.
    :type new_resource: URIRef
    :return: None
    """
    LOGGER.debug(f"Renaming {old_resource} to {new_resource}")

    for s, p, o in graph:
        if s == old_resource:
            graph.add((new_resource, p, o))
            graph.remove((old_resource, p, o))
        if p == old_resource:
            graph.add((s, new_resource, o))
            graph.remove((s, old_resource, o))
        if o == old_resource:
            graph.add((s, p, new_resource))
            graph.remove((s, p, old_resource))
