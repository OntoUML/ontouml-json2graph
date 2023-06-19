""" JSON decode functions. """

from rdflib import Graph

from globals import ONTOUML_URI, ONTOLOGY_URI
from modules.decoder.decode_general import clean_null_data, decode_dictionary
from modules.decoder.decode_obj_package import create_package_properties
from modules.decoder.decode_obj_project import create_project_properties


def decode_json_to_graph(json_data: dict) -> Graph:
    """ Receives the loaded JSON data and decodes it into a graph that complies to the OntoUML Vocabulary.

    :param json_data: Input JSON data loaded as a dictionary.
    :type json_data: dict
    :return: Knowledge graph that complies with the OntoUML Vocabulary
    :rtype: Graph
    """

    # Creating OntoUML Graph
    ontouml_graph = Graph()
    ontouml_graph.bind("ontouml", ONTOUML_URI)
    ontouml_graph.bind("", ONTOLOGY_URI)

    # Get clean data
    dictionary_data = clean_null_data(json_data)

    # GENERAL DECODING: creating all instances and setting their types
    decode_dictionary(dictionary_data, ontouml_graph)

    # SPECIFIC DECODING: create specific properties according to different object types
    create_project_properties(dictionary_data, ontouml_graph)
    create_package_properties(dictionary_data, ontouml_graph)

    return ontouml_graph
