""" Functions to decode specificities of the object Class. """

from rdflib import Graph, URIRef, Literal, XSD

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_utils import get_list_subdictionaries_for_specific_type


# TODO (@pedropaulofb): To be done when stereotypes are treted.
def validate_class_order_contraints(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Receives a class dictionary and check if valid values were received for the order attributes. Two constraints
    are verified: CC1 and CC2.

    CC1: Every class that is not a type must have order = 1.
    CC1: Every class that is a type must have order > 1.

    :param class_dict: Rectangle object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Setting class's isPowertype as false when this information is absent
    if "isPowertype" not in class_dict:
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict["id"]),
                           URIRef(URI_ONTOUML + "isPowertype"),
                           Literal(False)))

    # Setting class's order as "1"^^xsd:positiveInteger when this information is absent
    if "order" not in class_dict:
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict["id"]),
                           URIRef(URI_ONTOUML + "order"),
                           Literal(1, datatype=XSD.positiveInteger)))


def create_class_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Class.
    Receives the whole JSON loaded data as a dictionary to be manipulated and create all properties related to
    objects from type 'Class'.

    As classes as referenced as sub dictionaries for other objects, this function only treats dictionaries that
    contains the attribute 'name', indicating the Class object itself and not only a reference.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get all Classes' dictionaries
    list_all_classes_dicts = get_list_subdictionaries_for_specific_type(json_data, "Class")

    # Treat each Class dictionary
    for class_dict in list_all_classes_dicts:

        # Only treats dictionaries that contains name
        if "name" not in class_dict:
            continue

        # Validate order constraint
        # validate_class_order_contraints(class_dict, ontouml_graph)

        # Set class's order attributes
