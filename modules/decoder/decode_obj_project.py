""" Functions to decode specificities of the object Project. """

from rdflib import Graph, URIRef, RDF

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.sparql_queries import NOT_PROJECT_ELEMENTS
from modules.utils_graph import load_all_graph_safely


def set_project_project_properties(ontouml_graph: Graph) -> None:
    """ Sets ontouml:project object property between Project and its related elements.

    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get Project
    graph_project = ontouml_graph.value(predicate=RDF.type, object=URIRef(URI_ONTOUML + 'Project'))

    # Getting all OntoUML Elements that are not Project
    ontouml_meta_graph = load_all_graph_safely("resources/ontouml.ttl")
    aggregated_graph = ontouml_meta_graph + ontouml_graph
    query_answer = aggregated_graph.query(NOT_PROJECT_ELEMENTS)

    # Setting all not-Project OntoumlElements to the got Project via ontouml:project
    for row in query_answer:
        ontouml_graph.add((row.inst, URIRef(URI_ONTOUML + "project"), graph_project))


def set_project_model_property(project_data: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:model relation between a Project and its related model.

    :param project_data: Inputted JSON's clean dictionary.
    :type project_data: str
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    if "model" in project_data.keys():
        statement_subject = URIRef(URI_ONTOLOGY + project_data["id"])
        statement_predicate = URIRef(URI_ONTOUML + "model")
        statement_object = URIRef(URI_ONTOLOGY + project_data["model"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_diagrams_properties(project_data: dict, ontouml_graph: Graph) -> None:
    """ Sets relations between Project and its related diagrams.

    :param project_data: Inputted JSON's clean dictionary.
    :type project_data: str
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    if "diagrams" in project_data.keys():
        # TODO (@pedropaulofb): To be implemented.
        pass


def create_project_properties(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding a Project object.
    It only calls other specific functions for setting the object's specific properties.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    set_project_project_properties(ontouml_graph)
    set_project_model_property(dictionary_data, ontouml_graph)
    set_project_diagrams_properties(dictionary_data, ontouml_graph)
