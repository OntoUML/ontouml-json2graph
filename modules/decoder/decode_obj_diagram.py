""" Functions to decode objects of type Diagram.
Functions to set object properties are named according to the nomenclature: set_<subject>_<predicate>_<object>.
"""

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY, ELEMENT_VIEW_TYPES
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.utils_general import count_elements_types


def set_diagram_owner_modelelement(diagram_dict: dict, ontouml_graph: Graph) -> None:
    """ Set the ontouml:owner property between an ontouml:Diagram and its related ontouml:Package.

    :param diagram_dict: Diagram object loaded as a dictionary.
    :type diagram_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    statement_subject = URIRef(URI_ONTOLOGY + diagram_dict["id"])
    statement_predicate = URIRef(URI_ONTOUML + "owner")
    statement_object = URIRef(URI_ONTOLOGY + diagram_dict["owner"]["id"])
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_diagram_containsview_elementview(diagram_dict: dict, ontouml_graph: Graph) -> bool:
    """ Set the containsView property between a Diagram and its related ClassView.

    :param diagram_dict: Diagram object loaded as a dictionary.
    :type diagram_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :return: Indication if there are ClassViews still to be treated.
    :rtype: bool
    """

    list_related_classviews = get_list_subdictionaries_for_specific_type(diagram_dict, "ClassView")

    for related_classview in list_related_classviews:
        statement_subject = URIRef(URI_ONTOLOGY + diagram_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "containsView")
        statement_object = URIRef(URI_ONTOLOGY + related_classview["id"])

        ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Informs if there are ClassViews still to be treated
    if len(list_related_classviews):
        return True
    else:
        return False


def create_diagram_properties(json_data: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Main function for decoding objects of type 'Diagram'.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created object properties:
        - ontouml:owner (range ontouml:ModelElement)
        - ontouml:containsView (range ontouml:ElementView)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # Used for performance improvement
    num_elementviews = count_elements_types(ELEMENT_VIEW_TYPES, element_counting)

    # Setting diagram properties
    diagrams_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Diagram")

    for diagram_dict in diagrams_dicts_list:

        set_diagram_owner_modelelement(diagram_dict, ontouml_graph)

        # Treats relations between Diagrams and ClassView only while there are ClassViews still untreated
        if num_elementviews > 0:
            property_set = set_diagram_containsview_elementview(diagram_dict, ontouml_graph)
            if property_set:
                num_elementviews -= 1
