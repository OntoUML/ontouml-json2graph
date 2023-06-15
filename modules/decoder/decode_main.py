""" JSON decode functions. """

from rdflib import Graph

from globals import ONTOUML_URI, USER_BASE_URI
from modules.decoder.decode_general import clean_null_data, decode_dictionary
from modules.decoder.decode_project import set_project_model, set_project_diagrams, set_project_property


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
    ontouml_graph.bind("", USER_BASE_URI)

    # Get clean data
    project_data = clean_null_data(json_data)

    # Create all instances and set their types
    decode_dictionary(project_data, ontouml_graph)

    set_project_model(project_data, ontouml_graph)
    set_project_diagrams(project_data, ontouml_graph)

    set_project_property(ontouml_graph)

    return ontouml_graph
