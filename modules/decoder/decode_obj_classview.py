""" Functions to decode specificities of the object ClassView. """

from rdflib import Graph, URIRef

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type


def set_classview_properties(classview_dict: dict, ontouml_graph: Graph) -> None:
    """ Set ClassView's shape and isViewOf properties.

    :param classview_dict: ClassView object loaded as a dictionary.
    :type classview_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Setting shape property. A ClassView's shape is always named after it, adding the suffix '_shape'.
    shape_name = classview_dict['id'] + "_shape"

    ontouml_graph.add((URIRef(URI_ONTOLOGY + classview_dict['id']),
                       URIRef(URI_ONTOUML + "shape"),
                       URIRef(URI_ONTOLOGY + shape_name)))

    # Setting isViewOf property.
    ontouml_graph.add((URIRef(URI_ONTOLOGY + classview_dict['id']),
                       URIRef(URI_ONTOUML + "isViewOf"),
                       URIRef(URI_ONTOLOGY + classview_dict['modelElement']['id'])))


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

    # Treat each Rectangle
    for classview_dict in list_all_classview_dicts:
        # Setting shape and isViewOf properties
        set_classview_properties(classview_dict, ontouml_graph)
