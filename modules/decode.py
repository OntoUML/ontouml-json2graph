""" JSON decode functions. """
from rdflib import Graph


def decode_json_to_graph(json_data: dict) -> Graph:
    """ Receives the loaded JSON data and decodes it into a graph that complies to the OntoUML Vocabulary.

    :param json_data: Input JSON data loaded as a dictionary.
    :type json_data: dict
    :return: OntoUML Vocabulary compliant knowledge graph
    :rtype: Graph
    """

    ontouml_graph = Graph()

    return ontouml_graph
