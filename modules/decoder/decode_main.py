""" JSON decode functions. """

from rdflib import Graph

from globals import ONTOUML_URI
from modules.decoder.decode_general import clean_null_data
from modules.decoder.decode_project import decode_project


# TODO (@pedropaulofb): Every dictionary must have an id and a type. Validate.

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

    # Get clean Project and decode
    project_data = clean_null_data(json_data)
    decode_project(project_data, ontouml_graph)

    # Get clean Model and decode
    # if "model" in project_data.keys():
    #     model_data = project_data["model"]
    #     decode_models(models_data, ontouml_graph)

    # Get clean Diagrams and decode
    # if "diagrams" in project_data.keys():
    #     diagrams_data = project_data["diagrams"]
    #     decode_diagrams(diagrams_data, ontouml_graph)

    return ontouml_graph
