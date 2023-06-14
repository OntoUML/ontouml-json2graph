""" Project decoder functions. """
from rdflib import Graph

from modules.decoder.decode_general import decode_dictionary


def set_project_model(project_data, ontouml_graph):
    pass


def set_project_diagrams(project_data, ontouml_graph):
    pass


def decode_project(project_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a Project dictionary and decode every value to the OntoUML Graph.

    :param project_data: Project dictionary to have its empty fields cleaned.
    :type project_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    decode_dictionary(project_data, ontouml_graph)

    if "model" in project_data.keys():
        set_project_model(project_data, ontouml_graph)

    if "diagrams" in project_data.keys():
        set_project_diagrams(project_data, ontouml_graph)
