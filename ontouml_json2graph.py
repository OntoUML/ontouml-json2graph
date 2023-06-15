""" Main file for ontouml-json2graph. """
import time

from modules.arguments import treat_user_arguments
from modules.decoder.decode_main import decode_json_to_graph
from modules.input_output import safe_load_json_file, save_graph_file
from modules.logger import initialize_logger
from modules.utils import get_date_time


def ontouml_json2graph(json_path: str, graph_format: str, execution_mode: str = "production") -> str:
    """ Main function for ontouml-json2graph.

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param graph_format: Format for saving the resulting knowledge graph.
    :type graph_format: str
    :param execution_mode: Information about execution mode. Valid values are 'production' (default) and 'test'.
    :type execution_mode: str
    :return: Saved output file path.
    :rtype: str
    """

    logger = initialize_logger(execution_mode)

    if execution_mode == "production":
        # Initial time information
        time_screen_format = "%d-%m-%Y %H:%M:%S"
        start_date_time = get_date_time(time_screen_format)
        st = time.perf_counter()

        logger.info(f"OntoUML JSON2Graph decoder started on {start_date_time}!")

    # Load JSON
    json_data = safe_load_json_file(json_path)

    # Decode JSON into Graph
    ontouml_graph = decode_json_to_graph(json_data)

    if execution_mode == "production":
        # Get software's execution conclusion time
        end_date_time = get_date_time(time_screen_format)
        et = time.perf_counter()
        elapsed_time = round((et - st), 3)

        logger.info(f"Decoding concluded on {end_date_time}. Total execution time: {elapsed_time} seconds.")

    # Save graph as specified format
    output_file_path = save_graph_file(ontouml_graph, json_path, graph_format)
    logger.info(f"Output graph file successfully saved at {output_file_path}.")

    return output_file_path


if __name__ == '__main__':
    # Treat arguments
    arguments_dictionary = treat_user_arguments()
    json_path = arguments_dictionary["json_path"]
    graph_format = arguments_dictionary["format"]

    # Execute
    ontouml_json2graph(json_path, graph_format, "production")

# TODO (@pedropaulofb): Use validator for JSON (https://json-schema.org/implementations.html#validator-python)
# TODO (@pedropaulofb): Use validator for Graph (https://pypi.org/project/pyshacl/)
# TODO (@pedropaulofb): Create argument for defining base URI
# TODO (@pedropaulofb): Create argument for defining ontology's language tag (@en, @pt-br, etc.).
#  Default is to generate without language tag.
# TODO (@pedropaulofb): Create an option to update the resource/ontouml.ttl
