""" Functions to decode specificities of the object Generalization.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type


def set_generalization_relations(generalization_dict: dict, ontouml_graph: Graph) -> None:
    """ Set the ontouml:general and ontouml:specific properties in the resulting graph.

    :param generalization_dict: Generalization object loaded as a dictionary.
    :type generalization_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    generalization_individual = URIRef(URI_ONTOLOGY + generalization_dict['id'])
    general_individual = URIRef(URI_ONTOLOGY + generalization_dict["general"]['id'])
    specific_individual = URIRef(URI_ONTOLOGY + generalization_dict["specific"]['id'])

    ontouml_graph.add((generalization_individual, URIRef(URI_ONTOUML + "general"), general_individual))
    ontouml_graph.add((generalization_individual, URIRef(URI_ONTOUML + "specific"), specific_individual))


def create_generalization_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Generalization.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:general (range ontouml:Classifier)
        - ontouml:specific (range ontouml:Classifier)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_generalization_dicts = get_list_subdictionaries_for_specific_type(json_data, "Generalization")

    # Treat each object dictionary
    for generalization_dict in list_generalization_dicts:

        # Removing dictionaries that are only references
        if "general" not in generalization_dict:
            continue

        set_generalization_relations(generalization_dict, ontouml_graph)
