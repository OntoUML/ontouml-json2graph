""" Functions to be used """

from json2graph.decode import decode_ontouml_json2graph

def decode_json_project(json_path):
    pass


def decode_json_model(json_path, base_uri, graph_format, language, model_only, silent, correct, execution_mode):
    
    decode_ontouml_json2graph(json_path, base_uri, graph_format, language, model_only, silent, correct, execution_mode)

    return None


def save_to_file(file_path:str) -> None:
    pass
