""" Util functions related to graphs. """
import os

from rdflib import Graph, URIRef, RDF

from .errors import report_error_io_read
from .globals import METADATA
from .logger import initialize_logger

LOGGER = initialize_logger()


def ontouml_ref(entity: str) -> URIRef:
    """ Receives the name of the OntoUML Vocabulary's entity as a string and returns the corresponding URIRef.

    :param entity: OntoUML Vocabulary entity (class, property, or individual) to have its URIRef returned.
    :type entity: str
    :return: URIRef of the informed OntoUML Vocabulary's entity.
    :rtype: URIRef
    """

    entity_uri = METADATA["conformsTo"] + "#" + entity

    entity_uriref = URIRef(entity_uri)

    return entity_uriref


def load_ontouml_vocabulary() -> Graph:
    """ Loads the OntoUML Vocabulary to the working memory. First tries to load from web resource, if fails, it tries to
    load form the local resource. If both options fail, calls error reporting function.

    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """

    ontology_graph = Graph()

    remote_option = "https://w3id.org/ontouml/vocabulary/" + METADATA['conformsToVersion']

    # Guarantees that the file will be found as it searches using this file as basis
    package_dir = os.path.dirname(os.path.dirname(__file__))
    file_location = "resources\\ontouml_" + METADATA['conformsToVersion'] + ".ttl"
    file_path = os.path.join(package_dir, file_location)

    try:
        ontology_graph.parse(remote_option, encoding='utf-8', format="ttl")
        LOGGER.debug("OntoUML Vocabulary successfully loaded to working memory from remote option.")
    except:
        try:
            ontology_graph.parse(file_path, encoding='utf-8', format="ttl")
            LOGGER.debug("OntoUML Vocabulary successfully loaded to working memory from local option.")
        except OSError as error:
            report_error_io_read("OntoUML Vocabulary", "from remote or local sources the", error)

    return ontology_graph


def load_graph_safely(ontology_file: str, format: str = "not_provided") -> Graph:
    """ Safely load graph from file to working memory using arguments provided by the user, which are the file path
    and (optionally) the file type.

    :param ontology_file: Path to the ontology file to be loaded into the working memory.
    :type ontology_file: str
    :param format: Optional argument. Format of the file to be loaded.
    :type format: str
    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """

    ontology_graph = Graph()

    try:
        if format == "not_provided":
            ontology_graph.parse(ontology_file, encoding='utf-8')
        else:
            ontology_graph.parse(ontology_file, encoding='utf-8', format=format)
    except OSError as error:
        file_description = "input ontology file"
        report_error_io_read(ontology_file, file_description, error)

    LOGGER.debug(f"Ontology file {ontology_file} successfully loaded to working memory.")

    return ontology_graph


def get_all_ids_for_type(ontology_graph: Graph, element_type: str) -> list[str]:
    """ Queries the graph for all elements of the given element_type and returns a list of their ids.

    :param ontology_file: Loaded ontology graph.
    :type ontology_file: Graph
    :param element_type: Type of the element (originally a JSON object) to be queried to have their ids returned .
    :type element_type: list[str]
    """

    list_of_ids_of_type = []

    # Getting the ID of all OntoUML Elements that are of element_type
    for element in ontology_graph.subjects(RDF.type, ontouml_ref(element_type)):
        element = element.fragment
        list_of_ids_of_type.append(element)

    return list_of_ids_of_type
