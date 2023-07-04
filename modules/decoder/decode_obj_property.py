""" Functions to decode specificities of the object Property.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type


def set_property_aggregationkind_aggregationkind(property_dict: dict, ontouml_graph: Graph):
    """ Set the ontouml:aggregationKind property between an ontouml:Property and its corresponding
    ontouml:AggregationKind instance.

    :param property_dict: Diagram object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    statement_subject = URIRef(URI_ONTOLOGY + property_dict["id"])
    statement_predicate = URIRef(URI_ONTOUML + "aggregationKind")
    statement_object = URIRef(URI_ONTOUML + property_dict["aggregationKind"].lower())
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def create_property_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Property.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:aggregationKind (domain ontouml:Property, range ontouml:AggregationKind)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Getting Property dictionaries
    property_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Property")

    for property_dict in property_dicts_list:
        set_property_aggregationkind_aggregationkind(property_dict, ontouml_graph)
