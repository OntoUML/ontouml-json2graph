""" Main file for ontouml-json2graph."""

from lib_json2graph import decode_ontouml_json2graph
from modules import arguments as args

if __name__ == '__main__':
    # Treat and publish user's arguments
    args.initialize_arguments()

    json_path = args.ARGUMENTS["json_path"]
    graph_format = args.ARGUMENTS["format"]
    language = args.ARGUMENTS["language"]

    # Execute the transformation
    decode_ontouml_json2graph(json_path, graph_format, language, "production")
