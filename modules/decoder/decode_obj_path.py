""" Functions to decode specificities of the object Path.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef

import modules.arguments as args
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type, create_point
from modules.globals import URI_ONTOUML


def set_path_path_point(path_dict: dict, ontouml_graph: Graph) -> None:
    """ Creates an ontouml:Point, their properties and the ontouml:point of an ontouml:Path.

    :param path_dict: Path object loaded as a dictionary.
    :type path_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    base_point_name = path_dict["id"] + "_point_"
    point_counter = 0

    for point_dict in path_dict["points"]:
        # Creating new Point instance
        point_name = base_point_name + str(point_counter)
        create_point(point_name, point_dict["x"], point_dict["y"], ontouml_graph)

        # Associating new Point with the Path
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + path_dict["id"]),
                           URIRef(URI_ONTOUML + "point"),
                           URIRef(args.ARGUMENTS["base_uri"] + point_name)))

        point_counter += 1


def create_path_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Path.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created instances of:
        - ontouml:Point

    Created properties:
        - ontouml:point (range ontouml:Point)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_path_dicts = get_list_subdictionaries_for_specific_type(json_data, "Path")

    # Treat each object dictionary
    for path_dict in list_path_dicts:
        set_path_path_point(path_dict, ontouml_graph)
