""" Functions to be used """

from rdflib import Graph

from json2graph.decode import decode_ontouml_json2graph
from json2graph.modules.input_output import safe_write_graph_file

def save_graph_file(ontouml_graph: Graph, output_file_name: str, syntax: str) -> None:
    """ Safely saves the graph into a file in the informed destination with the desired syntax.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param output_file_name: Created output file name.
    :type output_file_name: str
    :param syntax: Syntax to be used for saving the ontology file.
    :type syntax: str
    """

    safe_write_graph_file(ontouml_graph, output_file_name, syntax)

def decode_json_project(json_path: str,
                        base_uri: str = "https://example.org#",
                        language: str = "",
                        correct: bool = False) -> Graph:
    """

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
    Default is "https://example.org#". (Optional)
    :type base_uri: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool

    :return: JSON data decoded into a RDFLib's Graph that is compliant with the OntoUML Vocabulary.
    :rtype: Graph
    """
    decoded_graph_project = decode_ontouml_json2graph(json_path=json_path, base_uri=base_uri, language=language,
                                                      model_only=True, silent=True, correct=correct,
                                                      execution_mode="import")

    return decoded_graph_project


def decode_json_model(json_path: str,
                      base_uri: str = "https://example.org#",
                      language: str = "",
                      correct: bool = False) -> Graph:
    """

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
    Default is "https://example.org#". (Optional)
    :type base_uri: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool

    :return: JSON data decoded into a RDFLib's Graph that is compliant with the OntoUML Vocabulary.
    :rtype: Graph
    """
    decoded_graph_model = decode_ontouml_json2graph(json_path=json_path, base_uri=base_uri, language=language,
                                                    model_only=True, silent=True, correct=correct,
                                                    execution_mode="import")

    return decoded_graph_model