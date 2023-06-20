""" JSON decode functions. """

from rdflib import Graph

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_general import clean_null_data, decode_dictionary, count_elements
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
    ontouml_graph.bind("ontouml", URI_ONTOUML)
    ontouml_graph.bind("", URI_ONTOLOGY)

    # Get clean data
    dictionary_data = clean_null_data(json_data)

    # GENERAL DECODING: creating all instances and setting their types.
    decode_dictionary(dictionary_data, ontouml_graph)

    # Counting elements for performance enhancement
    element_counting = count_elements(ontouml_graph)

    # SPECIFIC DECODING: create specific properties according to different object types
    if "Project" in element_counting:
        create_project_properties(dictionary_data, ontouml_graph)
    if "Package" in element_counting:
        create_package_properties(dictionary_data, ontouml_graph)

    return ontouml_graph
