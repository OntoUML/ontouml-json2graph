""" Functions to decode specificities of the object ElementView.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""
import inspect

from rdflib import Graph, URIRef

import modules.arguments as args
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.errors import report_error_end_of_switch
from modules.globals import URI_ONTOUML, ELEMENT_VIEW_TYPES


def set_elementview_relations(elementview_dict: dict, ontouml_graph: Graph) -> None:
    """ Set an ontouml:ElementView's ontouml:shape and ontouml:isViewOf object properties in the resulting graph.

    :param elementview_dict: ElementView object loaded as a dictionary.
    :type elementview_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # An ElementView's shape is always named after it:
    shape_name = elementview_dict['id']
    # When its shape type is 'Rectangle', adding the suffix '_shape'.
    if elementview_dict["shape"]["type"] in ['Rectangle', 'Text']:
        shape_name += "_shape"
    # When its shape type is 'Path', adding the suffix '_path'.
    elif elementview_dict["shape"]["type"] == 'Path':
        shape_name += "_path"
    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("classview_dict['shape']['type']", current_function)

    # Setting shape property
    ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['id']),
                       URIRef(URI_ONTOUML + "shape"),
                       URIRef(args.ARGUMENTS["base_uri"] + shape_name)))

    # Setting isViewOf property
    if "modelElement" in elementview_dict:
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['id']),
                           URIRef(URI_ONTOUML + "isViewOf"),
                           URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['modelElement']['id'])))

    # Setting sourceView and targetView properties
    if "source" in elementview_dict:
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['id']),
                           URIRef(URI_ONTOUML + "sourceView"),
                           URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['source']['id'])))

    if "target" in elementview_dict:
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['id']),
                           URIRef(URI_ONTOUML + "targetView"),
                           URIRef(args.ARGUMENTS["base_uri"] + elementview_dict['target']['id'])))


def create_elementview_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type ElementView.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:shape (domain ontouml:ElementView, range ontouml:Shape)
        - ontouml:isViewOf (domain ontouml:ElementView, range ontouml:ModelElement)
        - ontouml:sourceView (domain ontouml:ConnectorView, range ontouml:ElementView)
        - ontouml:targetView (domain ontouml:ConnectorView, range ontouml:ElementView)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_all_elementview_dicts = []

    # Get all ElementView' dictionaries
    for element_view in ELEMENT_VIEW_TYPES:
        list_all_elementview_dicts += get_list_subdictionaries_for_specific_type(json_data, element_view)

    # Treat each object dictionary
    for elementview_dict in list_all_elementview_dicts:

        # Removing dictionaries that are only references
        if "shape" not in elementview_dict:
            continue

        set_elementview_relations(elementview_dict, ontouml_graph)
