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


def set_property_relations(property_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the ontouml:aggregationKind and ontouml:propertyType object properties between an ontouml:Property and
    its related elements.

    :param property_dict: Diagram object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    statement_subject = URIRef(URI_ONTOLOGY + property_dict["id"])

    # Setting ontouml:aggregationKind
    statement_predicate = URIRef(URI_ONTOUML + "aggregationKind")
    statement_object = URIRef(URI_ONTOUML + property_dict["aggregationKind"].lower())
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Setting ontouml:propertyType
    if "propertyType" in property_dict:
        statement_predicate = URIRef(URI_ONTOUML + "propertyType")
        statement_object = URIRef(URI_ONTOLOGY + property_dict["propertyType"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def create_property_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Property.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:aggregationKind (range ontouml:AggregationKind)
        - ontouml:propertyType (range ontouml:Classifier)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Getting Property dictionaries
    property_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Property")

    for property_dict in property_dicts_list:
        set_property_relations(property_dict, ontouml_graph)
