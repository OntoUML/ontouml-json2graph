""" Project decoder functions. """
from rdflib import Graph, URIRef, RDF

from globals import ONTOUML_URI, USER_BASE_URI
from modules.utils import load_all_graph_safely


def set_project_property(ontouml_graph: Graph) -> None:
    """ Sets relation between Project and it related model.

    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get Project
    graph_project = ontouml_graph.value(predicate=RDF.type, object=URIRef(ONTOUML_URI + 'Project'))

    # If there is a project
    if graph_project:
        # Getting all OntoUML Elements that are not Project

        ontouml_meta_graph = load_all_graph_safely("resources/ontouml.ttl")
        aggregated_graph = ontouml_meta_graph + ontouml_graph
        query_definition = """
        PREFIX ontouml: <https://w3id.org/ontouml#>
        SELECT DISTINCT ?inst
        WHERE {
            ?onto_class rdfs:subClassOf+ ontouml:OntoumlElement .
            ?inst rdf:type ?onto_class .
            FILTER NOT EXISTS {?inst rdf:type ontouml:Project . }
        }"""
        query_answer = aggregated_graph.query(query_definition)

        # Setting all not-Project OntoumlElements to the got Project via ontouml:project
        for row in query_answer:
            ontouml_graph.add((row.inst, URIRef(ONTOUML_URI + "project"), graph_project))


def set_project_model(project_data: dict, ontouml_graph: Graph) -> None:
    """ Sets relation between Project and it related model.

    :param project_data: Inputted JSON's clean dictionary.
    :type project_data: str
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    if "model" in project_data.keys():
        statement_subject = URIRef(USER_BASE_URI + project_data["id"])
        statement_predicate = URIRef(ONTOUML_URI + "model")
        statement_object = URIRef(USER_BASE_URI + project_data["model"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_diagrams(project_data: dict, ontouml_graph: Graph) -> None:
    """ Sets relations between Project and its related diagrams.

    :param project_data: Inputted JSON's clean dictionary.
    :type project_data: str
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    if "diagrams" in project_data.keys():
        # TBD
        pass
