""" Functions to decode specificities of the object ElementView.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef

from globals import URI_ONTOLOGY, URI_ONTOUML, ELEMENT_VIEW_TYPES
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type


def set_elementview_relations(classview_dict: dict, ontouml_graph: Graph) -> None:
    """ Set an ontouml:ElementView's ontouml:shape and ontouml:isViewOf object properties in the resulting graph.

    :param classview_dict: ClassView object loaded as a dictionary.
    :type classview_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # An ElementView's shape is always named after it, adding the suffix '_shape'.
    shape_name = classview_dict['id'] + "_shape"

    # Setting shape property.
    ontouml_graph.add((URIRef(URI_ONTOLOGY + classview_dict['id']),
                       URIRef(URI_ONTOUML + "shape"),
                       URIRef(URI_ONTOLOGY + shape_name)))

    # Setting isViewOf property.
    ontouml_graph.add((URIRef(URI_ONTOLOGY + classview_dict['id']),
                       URIRef(URI_ONTOUML + "isViewOf"),
                       URIRef(URI_ONTOLOGY + classview_dict['modelElement']['id'])))


def create_elementview_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type ElementView.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:shape (domain ontouml:ElementView, range ontouml:Shape)
        - ontouml:isViewOf (domain ontouml:ElementView, range ontouml:ModelElement)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_all_elementview_dicts = []

    # Get all ElementView' dictionaries
    for element_view in ELEMENT_VIEW_TYPES:
        list_elementview_dicts = get_list_subdictionaries_for_specific_type(json_data, element_view)
        list_all_elementview_dicts += list_elementview_dicts

    # Treat each ElementView
    for elementview_dict in list_all_elementview_dicts:
        set_elementview_relations(elementview_dict, ontouml_graph)
