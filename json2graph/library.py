""" The `library.py` module serves as a versatile and user-friendly library within the broader ontouml-json2graph
package.

It offers a streamlined way for users to convert OntoUML model data in JSON format into RDF graphs that adhere to the
OntoUML Vocabulary. By encapsulating the underlying functionalities, this library empowers users to effortlessly
integrate OntoUML JSON conversion capabilities into their projects.

In addition to conversion functions, the library provides the `save_graph_file` utility, enabling users to safely save
OntoUML graphs to files in their desired syntax.
"""

from rdflib import Graph

from json2graph.decode import decode_ontouml_json2graph
from json2graph.modules.errors import report_error_requirement_not_met
from json2graph.modules.input_output import safe_write_graph_file


def decode_json_project(json_path: str,
                        base_uri: str = "https://example.org#",
                        language: str = "",
                        correct: bool = False) -> Graph:
    """ Decodes elements from OntoUML's abstract and concrete syntax from JSON format into a Knowledge Graph.
    I.e., domain-level and diagrammatic data are converted to Knowledge Graph.

    This function decodes OntoUML JSON data representing a project-level model into a knowledge graph
    that adheres to the OntoUML Vocabulary. It provides customization options for URI generation, language tags,
    error correction, and returns the resulting knowledge graph.

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
                     Default is "https://example.org#". (Optional)
    :type base_uri: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
                     This tag specifies the language in which labels and descriptions are provided.
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
    """ Decodes elements from OntoUML's abstract syntax from JSON format into a Knowledge Graph.
    I.e., only domain-level (and not diagrammatic) data is converted to Knowledge Graph.

    This function decodes OntoUML JSON data representing a model-level view into a knowledge graph
    that adheres to the OntoUML Vocabulary. It provides customization options for URI generation, language tags,
    error correction, and returns the resulting knowledge graph.

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
                     Default is "https://example.org#". (Optional)
    :type base_uri: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
                     This tag specifies the language in which labels and descriptions are provided.
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


def save_graph_file(ontouml_graph: Graph, output_file_path: str, syntax: str) -> None:
    """ The save_graph_file function is designed to securely save an OntoUML graph, represented as an RDFLib's Graph
    object, into a file at a specified destination while using the user's informed syntax.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param output_file_path: Complete path of the output file to be created (including name and extension).
    :type output_file_path: str
    :param syntax: Syntax to be used for saving the ontology file. A syntax allowed by RDFLib must be informed.
    :type syntax: str
    """

    valid_syntaxes = ['turtle', 'ttl', 'turtle2', 'xml', 'pretty-xml', 'json-ld', 'ntriples', 'nt', 'nt11', 'n3',
                      'trig', 'trix', 'nquads']

    if syntax not in valid_syntaxes:
        report_error_requirement_not_met("Invalid syntax used as argument.")
    else:
        safe_write_graph_file(ontouml_graph, output_file_path, syntax)
