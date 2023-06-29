""" Functions to decode specificities of the object Class. """
from pprint import pprint

from rdflib import Graph, URIRef, XSD, Literal

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def validate_class_defaults(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Verifies all Class dictionaries and check if their default values (not nullable) were not set (i.e., if they are
    null) and fixes them.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Order default value = 1 when not stereotype 'type'
    # TODO (@pedropaulofb): and value = 2 when stereotype 'type'
    if "order" not in class_dict:
        LOGGER.warning(
            f"The class with id {class_dict['id']} had 'order' attribute (originally null) set to 1 (default).")
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "order"),
                           Literal(1, datatype=XSD.positiveInteger)))

    # isPowertype default value = False
    if "isPowertype" not in class_dict:
        LOGGER.warning(
            f"The class with id {class_dict['id']} had 'isPowertype' attribute (originally null) set to False (default).")
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "isPowertype"),
                           Literal(False)))


def create_class_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Class.
    Receives the whole JSON loaded data as a dictionary to be manipulated and create all properties related to
    objects from this type.

    Dictionaries containing classes IDs are used for reference. One of its characteristics is that they do not have the
    field 'name'. These are not Classes dictionaries and, hence, are not treated here.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get all class' dictionaries
    list_all_class_dicts = get_list_subdictionaries_for_specific_type(json_data, "Class")

    pprint(list_all_class_dicts)

    # Treat each Rectangle
    for class_dict in list_all_class_dicts:

        # Skipping dictionaries that refer to classes
        if "name" not in class_dict:
            continue

        # Validating default values
        validate_class_defaults(class_dict, ontouml_graph)
