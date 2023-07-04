""" Functions to decode specificities of the object Project. """

from rdflib import Graph, URIRef, RDF, Literal

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type


def set_rectangularshape_coordinates(rectangularshape_dict: dict, ontouml_graph: Graph) -> None:
    """ Creates ontouml:topLeftPosition, ontouml:xCoordinate, and ontouml:yCoordinate of an ontouml:RectangularShape.

    :param rectangularshape_dict: RectangularShape object loaded as a dictionary.
    :type rectangularshape_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Creating new Point instance
    point_name = rectangularshape_dict["id"] + "_point"
    ontouml_graph.add((URIRef(URI_ONTOLOGY + point_name), RDF.type, URIRef(URI_ONTOUML + "Point")))

    # Associating new Point with Rectangle
    ontouml_graph.add((URIRef(URI_ONTOLOGY + rectangularshape_dict["id"]),
                       URIRef(URI_ONTOUML + "topLeftPosition"),
                       URIRef(URI_ONTOLOGY + point_name)))

    # Setting x coordinate
    ontouml_graph.add((URIRef(URI_ONTOLOGY + point_name),
                       URIRef(URI_ONTOUML + "xCoordinate"),
                       Literal(rectangularshape_dict["x"])))

    # Setting y coordinate
    ontouml_graph.add((URIRef(URI_ONTOLOGY + point_name),
                       URIRef(URI_ONTOUML + "yCoordinate"),
                       Literal(rectangularshape_dict["y"])))


def create_rectangularshape_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type RectangularShape.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created instances:
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

    # Treat each RectangularShape
    for rectangularshape_dict in list_all_rectangularshape_dicts:
        set_rectangularshape_coordinates(rectangularshape_dict, ontouml_graph)
