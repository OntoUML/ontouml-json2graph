""" Main file for ontouml-json2graph. """

import time

import modules.arguments as args
from globals import SOFTWARE_NAME, SOFTWARE_VERSION
from modules.decoder.decode_main import decode_json_to_graph
from modules.input_output import safe_load_json_file, write_graph_file
from modules.logger import initialize_logger
from modules.utils_general import get_date_time


def ontouml_json2graph(json_path: str, graph_format: str, language: str = "",
                       execution_mode: str = "production") -> str:
    """ Main function for ontouml-json2graph.

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param graph_format: Format for saving the resulting knowledge graph.
    :type graph_format: str
    :param language: Language tag to be added to the ontology's concepts.
    :type language: str
    :param execution_mode: Information about execution mode. Valid values are 'production' (default) and 'test'.
    :type execution_mode: str
    :return: Saved output file path. Used for testing.
    :rtype: str
    """

    logger = initialize_logger(execution_mode)

    if execution_mode == "test":
        args.ARGUMENTS["correct"] = True
        args.ARGUMENTS["silent"] = True

    if execution_mode == "production" and not args.ARGUMENTS["silent"]:
        # Initial time information
        time_screen_format = "%d-%m-%Y %H:%M:%S"
        start_date_time = get_date_time(time_screen_format)
        st = time.perf_counter()

        logger.info(f"{SOFTWARE_NAME} v{SOFTWARE_VERSION} started on {start_date_time}!")
        logger.debug(f"Selected arguments are: {args.ARGUMENTS}")
        logger.info(f"Decoding JSON file {json_path} to {(args.ARGUMENTS['format']).upper()} graph format.\n")

        if not args.ARGUMENTS['language']:
            logger.warning("Ontology's language not informed by the user. "
                           "Transformation will not generate language tag.")
        if not args.ARGUMENTS['correct']:
            logger.warning("Basic correction feature not enabled by the user. "
                           "The transformation may generate an invalid result.")

    # Load JSON
    json_data = safe_load_json_file(json_path)

    # Decode JSON into Graph
    # TODO (@pedropaulofb): Add execution_mode as parameter to the decoder and only add metadata if not test
    ontouml_graph = decode_json_to_graph(json_data, language, execution_mode)

    if execution_mode == "production" and not args.ARGUMENTS["silent"]:
        # Get software's execution conclusion time
        end_date_time = get_date_time(time_screen_format)
        et = time.perf_counter()
        elapsed_time = round((et - st), 3)
        logger.info(f"Decoding concluded on {end_date_time}. Total execution time: {elapsed_time} seconds.")

    # Save graph as specified format
    output_file_path = write_graph_file(ontouml_graph, json_path, graph_format)
    logger.info(f"Output graph file successfully saved at {output_file_path}.")

    return output_file_path


if __name__ == '__main__':
    # Treat and publish user's arguments
    args.publish_user_arguments()

    json_path = args.ARGUMENTS["json_path"]
    graph_format = args.ARGUMENTS["format"]
    language = args.ARGUMENTS["language"]

    # Execute the transformation
    ontouml_json2graph(json_path, graph_format, language, "production")
