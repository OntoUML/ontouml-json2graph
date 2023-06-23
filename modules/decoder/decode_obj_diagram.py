""" Decode objects from type Diagram. """

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_utils import get_list_subdictionaries_for_specific_type


def create_diagram_properties(json_data: dict, ontouml_graph: Graph):
    """ Main function for decoding an object of type Diagram.
    Receives the whole JSON loaded data as a dictionary to be manipulated and create all properties related to
    objects from type 'Diagram'.

    :param json_data: Dictionary to have its fields decoded.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    diagrams_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Diagram")

    for diagrams_dict in diagrams_dicts_list:
        statement_subject = URIRef(URI_ONTOLOGY + diagrams_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "owner")
        statement_object = URIRef(URI_ONTOLOGY + diagrams_dict["owner"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))
