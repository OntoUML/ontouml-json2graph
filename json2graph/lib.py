""" Functions to be used """
from rdflib import Graph

from json2graph.decode import decode_ontouml_json2graph
from json2graph.modules.input_output import safe_write_graph_file as write_graph_file


def decode_json_project(json_path: str,
                        base_uri: str = "https://example.org#",
                        language: str = "",
                        correct: bool = False) -> Graph:
    decoded_graph_project = decode_ontouml_json2graph(json_path=json_path, base_uri=base_uri, language=language,
                                                      model_only=True, silent=True, correct=correct,
                                                      execution_mode="import")

    return decoded_graph_project


def decode_json_model(json_path: str,
                      base_uri: str = "https://example.org#",
                      language: str = "",
                      correct: bool = False) -> Graph:
    decoded_graph_model = decode_ontouml_json2graph(json_path=json_path, base_uri=base_uri, language=language,
                                                    model_only=True, silent=True, correct=correct,
                                                    execution_mode="import")

    return decoded_graph_model

# this pieace of code is used only to guarantee that the IDE reformatter is not going to clean the code
if __name__ == "__main__":
    if 1==2:
        write_graph_file()