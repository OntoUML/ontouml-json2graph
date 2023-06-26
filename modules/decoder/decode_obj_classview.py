""" Functions to decode specificities of the object ClassView. """

from rdflib import Graph

from modules.decoder.decode_utils import get_list_subdictionaries_for_specific_type


def create_classview_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type ClassView.
    Receives the whole JSON loaded data as a dictionary to be manipulated and create all properties related to
    objects from this type.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get all ClassView' dictionaries
    list_all_classview_dicts = get_list_subdictionaries_for_specific_type(json_data, "ClassView")

    # pprint(list_all_classview_dicts)

    # # Treat each Rectangle
    # for classview_dict in list_all_classview_dicts:
    #
    #     # Set width and height
    #     set_rectangle_coordinates(classview_dict, ontouml_graph)
