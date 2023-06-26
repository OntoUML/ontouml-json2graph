""" Decode objects from type Diagram. """

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_utils import get_list_subdictionaries_for_specific_type


def set_diagram_owner(diagram_dict: dict, ontouml_graph: Graph) -> None:
    """ Set the owner property between a Diagram and its related Package.

    :param diagram_dict: Diagram object loaded as a dictionary.
    :type diagram_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    statement_subject = URIRef(URI_ONTOLOGY + diagram_dict["id"])
    statement_predicate = URIRef(URI_ONTOUML + "owner")
    statement_object = URIRef(URI_ONTOLOGY + diagram_dict["owner"]["id"])
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_diagram_containsview(diagram_dict: dict, ontouml_graph: Graph) -> bool:
    """ Set the containsView property between a Diagram and its related ClassView.

    :param diagram_dict: Diagram object loaded as a dictionary.
    :type diagram_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    :return: Boolean value indication if a containsView property was set (True) or not (False).
    :rtype: bool
    """

    list_related_classviews = get_list_subdictionaries_for_specific_type(diagram_dict, "ClassView")

    for related_classview in list_related_classviews:
        statement_subject = URIRef(URI_ONTOLOGY + diagram_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "containsView")
        statement_object = URIRef(URI_ONTOLOGY + related_classview["id"])

        ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    if len(list_related_classviews):
        return True
    else:
        return False


def create_diagram_properties(json_data: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Main function for decoding an object of type Diagram.
    Receives the whole JSON loaded data as a dictionary to be manipulated and create all properties related to
    objects from type 'Diagram'.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # Used for performance improvement
    if "ClassView" in element_counting:
        num_classview = element_counting["ClassView"]
    else:
        num_classview = 0

    # Setting diagram properties
    diagrams_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Diagram")

    for diagram_dict in diagrams_dicts_list:

        set_diagram_owner(diagram_dict, ontouml_graph)

        # Treats relations between Diagrams and ClassView only while there are ClassViews still untreated
        if num_classview > 0:
            property_set = set_diagram_containsview(diagram_dict, ontouml_graph)
            if property_set:
                num_classview -= 1
