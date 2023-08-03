""" Main file for ontouml-json2graph."""
import os
import sys

import modules.arguments as args

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from main_decode import decode_ontouml_json2graph

if __name__ == '__main__':
    # Treat and publish user's arguments
    args.initialize_arguments()

    json_path = args.ARGUMENTS["json_path"]
    graph_format = args.ARGUMENTS["format"]
    language = args.ARGUMENTS["language"]

    # Execute the transformation
    decode_ontouml_json2graph(json_path, graph_format, language, "production")
