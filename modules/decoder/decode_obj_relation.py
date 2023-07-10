""" Functions to decode specificities of the object Relation.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type, set_object_stereotype


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

    relation_individual = URIRef(URI_ONTOLOGY + relation_dict['id'])
    uri_relation_end = URIRef(URI_ONTOUML + "relationEnd")
    uri_relation_sourceend = URIRef(URI_ONTOUML + "sourceEnd")
    uri_relation_targetend = URIRef(URI_ONTOUML + "targetEnd")

    ends_list = []
    for property_dict in relation_dict["properties"]:
        ends_list.append(property_dict["id"])

    source_id = URIRef(URI_ONTOLOGY + ends_list[0])
    target_id = URIRef(URI_ONTOLOGY + ends_list[1])

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

        set_relation_relations(relation_dict, ontouml_graph)
        set_object_stereotype(relation_dict, ontouml_graph)
