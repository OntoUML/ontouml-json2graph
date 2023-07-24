""" Functions to decode specificities of the object Diagram.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
    - Functions that set default values: set_<subject>_defaults.
"""

from rdflib import Graph, URIRef

import modules.arguments as args
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.globals import URI_ONTOUML, ELEMENT_VIEW_TYPES


def set_diagram_owner_modelelement(diagram_dict: dict, ontouml_graph: Graph) -> None:
    """ Set the ontouml:owner property between an ontouml:Diagram and its related ontouml:Package.

    :param diagram_dict: Diagram object loaded as a dictionary.
    :type diagram_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    statement_subject = URIRef(args.ARGUMENTS["base_uri"] + diagram_dict["id"])
    statement_predicate = URIRef(URI_ONTOUML + "owner")
    statement_object = URIRef(args.ARGUMENTS["base_uri"] + diagram_dict["owner"]["id"])
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_diagram_containsview_elementview(diagram_dict: dict, ontouml_graph: Graph) -> None:
    """ Set the ontouml:containsView property between an ontouml:Diagram and its related ontouml:ElementView.

    :param diagram_dict: Diagram object loaded as a dictionary.
    :type diagram_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_related_elementviews = []

    for view_type in ELEMENT_VIEW_TYPES:
        list_related_elementviews += get_list_subdictionaries_for_specific_type(diagram_dict, view_type)

    for related_elementview in list_related_elementviews:
        statement_subject = URIRef(args.ARGUMENTS["base_uri"] + diagram_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "containsView")
        statement_object = URIRef(args.ARGUMENTS["base_uri"] + related_elementview["id"])

        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


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

    # Setting diagram properties
    diagrams_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Diagram")

    for diagram_dict in diagrams_dicts_list:

        set_diagram_owner_modelelement(diagram_dict, ontouml_graph)

        # Treats relations between instances of Diagram and ElementView only if the formers exist
        if any(item in ELEMENT_VIEW_TYPES for item in element_counting.keys()):
            set_diagram_containsview_elementview(diagram_dict, ontouml_graph)
