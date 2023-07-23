""" Util functions related to graphs. """

from rdflib import Graph, URIRef, RDF

from modules.errors import report_error_io_read
from modules.globals import URI_ONTOUML
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def load_ontouml_vocabulary() -> Graph:
    """ Loads the OntoUML Vocabulary to the working memory. First tries to load from web resource, if fails, it tries to
    load form the local resource. If both options fail, calls error reporting function.

    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """

    ontology_graph = Graph()

    remote_option = "https://w3id.org/ontouml"
    local_option = "resources/ontouml.ttl"

    try:
        ontology_graph.parse(remote_option, encoding='utf-8', format="ttl")
        LOGGER.debug(f"OntoUML Vocabulary successfully loaded to working memory from remote option.")
    except:
        try:
            ontology_graph.parse(local_option, encoding='utf-8', format="ttl")
            LOGGER.debug(f"OntoUML Vocabulary successfully loaded to working memory from local option.")
        except OSError as error:
            report_error_io_read("OntoUML Vocabulary", "from remote or local sources the", error)

    return ontology_graph


def load_graph_safely(ontology_file: str) -> Graph:
    """ Safely load graph from file to working memory.

    :param ontology_file: Path to the ontology file to be loaded into the working memory.
    :type ontology_file: str
    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """

    ontology_graph = Graph()

    try:
        ontology_graph.parse(ontology_file, encoding='utf-8')
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
    for element in ontology_graph.subjects(RDF.type, URIRef(URI_ONTOUML + element_type)):
        element = element.fragment
        list_of_ids_of_type.append(element)

    return list_of_ids_of_type
