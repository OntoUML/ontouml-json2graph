""" Main file for ontouml-json2graph. """
import json

from modules.arguments import treat_user_arguments
from modules.logger import initialize_logger
from modules.utils import safe_load_json_file

LOGGER = initialize_logger()


def ontouml_json2graph() -> None:
    """ Main function for ontouml-json2graph. """

    # Treat arguments
    arguments_dictionary = treat_user_arguments()
    json_path = arguments_dictionary["json_path"]
    graph_format = arguments_dictionary["format"]

    # Load JSON
    json_data = safe_load_json_file(json_path)
    print(json_data)

    # Decode JSON into Graph
    ontouml_graph = decode_json_to_graph(json_data)

    # Save graph as specified format



if __name__ == '__main__':
    ontouml_json2graph()
