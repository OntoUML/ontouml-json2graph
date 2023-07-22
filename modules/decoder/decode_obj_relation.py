""" Functions to decode specificities of the object Relation.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef, Literal

import modules.arguments as args
from globals import URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type, set_object_stereotype
from modules.messages import print_decode_log_message


def set_relation_defaults(relation_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the following attribute's default values for ontouml:Relation:

    DRA1) ontouml:isDerived default value = False
    DRA2) ontouml:isAbstract default value = False

    :param relation_dict: Relation object loaded as a dictionary.
    :type relation_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # DRA1, and DRA2 use the same message DGA1, as they are not associated to their holder's stereotype.

    # DCA3: Setting ontouml:isDerived attribute default value
    if "isDerived" not in relation_dict:
        print_decode_log_message(relation_dict, "DGA1", attribute='isDerived')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + relation_dict['id']),
                           URIRef(URI_ONTOUML + "isDerived"), Literal(False, datatype=XSD.boolean)))

    # DCA4: Setting ontouml:isAbstract attribute default value
    if "isAbstract" not in relation_dict:
        print_decode_log_message(relation_dict, "DGA1", attribute='isAbstract')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + relation_dict['id']),
                           URIRef(URI_ONTOUML + "isAbstract"), Literal(False, datatype=XSD.boolean)))


def set_relation_relations(relation_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the following object properties to instances of ontouml:Relation:
        - ontouml:relationEnd (range ontouml:Property)
        - ontouml:sourceEnd (range ontouml:Property)
        - ontouml:targetEnd (range ontouml:Property)

    :param relation_dict: Relation object loaded as a dictionary.
    :type relation_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    relation_individual = URIRef(args.ARGUMENTS["base_uri"] + relation_dict['id'])
    uri_relation_end = URIRef(URI_ONTOUML + "relationEnd")
    uri_relation_sourceend = URIRef(URI_ONTOUML + "sourceEnd")
    uri_relation_targetend = URIRef(URI_ONTOUML + "targetEnd")

    ends_list = []
    for property_dict in relation_dict["properties"]:
        ends_list.append(property_dict["id"])

    source_id = URIRef(args.ARGUMENTS["base_uri"] + ends_list[0])
    target_id = URIRef(args.ARGUMENTS["base_uri"] + ends_list[1])

    # Setting ontouml:relationEnd
    ontouml_graph.add((relation_individual, uri_relation_end, source_id))
    ontouml_graph.add((relation_individual, uri_relation_end, target_id))

    # Setting ontouml:sourceEnd and ontouml:targetEnd
    ontouml_graph.add((relation_individual, uri_relation_sourceend, source_id))
    ontouml_graph.add((relation_individual, uri_relation_targetend, target_id))


def create_relation_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Relation.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:relationEnd (range ontouml:Property)
        - ontouml:sourceEnd (range ontouml:Property)
        - ontouml:targetEnd (range ontouml:Property)
        - ontouml:stereotype (range ontouml:RelationStereotype)
        - ontouml:isDerived (range xsd:boolean)
        - ontouml:isAbstract (range xsd:boolean)


    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_relation_dicts = get_list_subdictionaries_for_specific_type(json_data, "Relation")

    # Treat each object dictionary
    for relation_dict in list_relation_dicts:

        # Removing possible dictionaries that are only references
        if "properties" not in relation_dict:
            continue

        set_relation_defaults(relation_dict, ontouml_graph)
        set_relation_relations(relation_dict, ontouml_graph)
        set_object_stereotype(relation_dict, ontouml_graph)
