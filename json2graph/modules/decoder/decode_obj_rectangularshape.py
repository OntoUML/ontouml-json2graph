""" Functions to decode specificities of the object RectangularShare.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
    - Functions that set default values: set_<subject>_defaults.
"""

import modules.arguments as args
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type, create_point
from modules.utils_graph import ontouml_ref
from rdflib import Graph, URIRef


def set_rectangularshape_coordinates(rectangularshape_dict: dict, ontouml_graph: Graph) -> None:
    """ Creates an ontouml:Point, their properties and the ontouml:topLeftPosition of an ontouml:RectangularShape.

    :param rectangularshape_dict: RectangularShape object loaded as a dictionary.
    :type rectangularshape_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Creating new Point instance
    point_name = rectangularshape_dict["id"] + "_point"
    create_point(point_name, rectangularshape_dict["x"], rectangularshape_dict["y"], ontouml_graph)

    # Associating new Point with Rectangle
    ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + rectangularshape_dict["id"]),
                       ontouml_ref("topLeftPosition"),
                       URIRef(args.ARGUMENTS["base_uri"] + point_name)))


def create_rectangularshape_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type RectangularShape.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created instances of:
        - ontouml:Point

    Created properties:
        - ontouml:topLeftPosition (domain ontouml:RectangularShape, range ontouml:Point)
        - ontouml:xCoordinate (domain ontouml:Point, range xsd:integer)
        - ontouml:yCoordinate (domain ontouml:Point, range xsd:integer)

    # The ontouml:height and ontouml:width data properties are not assigned in this function, as they can be directly
    obtained in the general decoding.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Get all Rectangles' and Texts' dictionaries
    list_all_rectangle_dicts = get_list_subdictionaries_for_specific_type(json_data, "Rectangle")
    list_all_text_dicts = get_list_subdictionaries_for_specific_type(json_data, "Text")
    list_all_rectangularshape_dicts = list_all_rectangle_dicts + list_all_text_dicts

    # Treat each object dictionary
    for rectangularshape_dict in list_all_rectangularshape_dicts:
        set_rectangularshape_coordinates(rectangularshape_dict, ontouml_graph)
