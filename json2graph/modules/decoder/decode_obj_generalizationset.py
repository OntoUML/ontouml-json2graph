""" Functions to decode specificities of the object GeneralizationSet.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
    - Functions that set default values: set_<subject>_defaults.
"""

import modules.arguments as args
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.messages import print_decode_log_message
from modules.utils_graph import ontouml_ref
from rdflib import Graph, URIRef, Literal, XSD


def set_generalizationset_defaults(generalizationset_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the default values to ontouml:generalizationSets to the resulting graph.

    - Default isDisjoint: If isDisjoint is null, set as False.
    - Default isComplete: If isComplete is null, set as False.

    :param generalizationset_dict: GeneralizationSet object loaded as a dictionary.
    :type generalizationset_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    generalizationset_individual = URIRef(args.ARGUMENTS["base_uri"] + generalizationset_dict['id'])
    set_false = Literal(False, datatype=XSD.boolean)

    if "isDisjoint" not in generalizationset_dict:
        print_decode_log_message(generalizationset_dict, "DGA1", property_name="isDisjoint")
        is_disjoint_property = ontouml_ref("isDisjoint")
        ontouml_graph.add((generalizationset_individual, is_disjoint_property, set_false))

    if "isComplete" not in generalizationset_dict:
        print_decode_log_message(generalizationset_dict, "DGA1", property_name="isComplete")
        is_complete_property = ontouml_ref("isComplete")
        ontouml_graph.add((generalizationset_individual, is_complete_property, set_false))


def set_generalizationset_relations(generalizationset_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the ontouml:generalization and ontouml:categorizer property to the resulting graph.

    :param generalizationset_dict: GeneralizationSet object loaded as a dictionary.
    :type generalizationset_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    generalizationset_individual = URIRef(args.ARGUMENTS["base_uri"] + generalizationset_dict['id'])
    generalization_property = ontouml_ref("generalization")
    categorizer_property = ontouml_ref("categorizer")

    # Setting ontouml:generalization property
    for generalization_dict in generalizationset_dict["generalizations"]:
        generalization_individual = URIRef(args.ARGUMENTS["base_uri"] + generalization_dict["id"])
        ontouml_graph.add((generalizationset_individual, generalization_property, generalization_individual))

    # Setting ontouml:categorizer property
    if "categorizer" in generalizationset_dict:
        categorizer_individual = URIRef(args.ARGUMENTS["base_uri"] + generalizationset_dict["categorizer"]["id"])
        ontouml_graph.add((generalizationset_individual, categorizer_property, categorizer_individual))


def create_generalizationset_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type GeneralizationSet.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:generalization (range ontouml:Generalization)
        - ontouml:categorizer (range ontouml:Class)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_generalizationset_dicts = get_list_subdictionaries_for_specific_type(json_data, "GeneralizationSet")

    # Treat each object dictionary
    for generalizationset_dict in list_generalizationset_dicts:

        # Removing dictionaries that are only references
        if len(generalizationset_dict) < 3:
            continue

        set_generalizationset_defaults(generalizationset_dict, ontouml_graph)
        set_generalizationset_relations(generalizationset_dict, ontouml_graph)
