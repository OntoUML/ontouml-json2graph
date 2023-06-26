""" Functions to decode specificities of the object Project. """

from rdflib import Graph, URIRef, RDF, Literal

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_utils import get_list_subdictionaries_for_specific_type


def set_rectangle_coordinates(rectangle_dict: dict, ontouml_graph: Graph) -> None:
    """ Set width and hight of a rectangle.

    :param rectangle_dict: Rectangle object loaded as a dictionary.
    :type rectangle_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Creating new Point instance
    point_name = rectangle_dict["id"] + "_point"
    ontouml_graph.add((URIRef(URI_ONTOLOGY + point_name), RDF.type, URIRef(URI_ONTOUML + "Point")))

    # Associating new Point with Rectangle
    ontouml_graph.add((URIRef(URI_ONTOLOGY + rectangle_dict["id"]),
                       URIRef(URI_ONTOUML + "topLeftPosition"),
                       URIRef(URI_ONTOLOGY + point_name)))

    # Setting x coordinate
    ontouml_graph.add((URIRef(URI_ONTOLOGY + point_name),
                       URIRef(URI_ONTOUML + "xCoordinate"),
                       Literal(rectangle_dict["x"])))

    # Setting y coordinate
    ontouml_graph.add((URIRef(URI_ONTOLOGY + point_name),
                       URIRef(URI_ONTOUML + "yCoordinate"),
                       Literal(rectangle_dict["y"])))


def create_rectangle_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Rectangle.
    Receives the whole JSON loaded data as a dictionary to be manipulated and create all properties related to
    objects from type 'Rectangle'.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get all Rectangles' dictionaries
    list_all_rectangle_dicts = get_list_subdictionaries_for_specific_type(json_data, "Rectangle")

    # Treat each Rectangle
    for rectangle_dict in list_all_rectangle_dicts:
        # Set width and height
        set_rectangle_coordinates(rectangle_dict, ontouml_graph)
