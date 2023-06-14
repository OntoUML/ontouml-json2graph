""" Main file for ontouml-json2graph. """
import time

from modules.arguments import treat_user_arguments
from modules.decode import decode_json_to_graph
from modules.input_output import safe_load_json_file, save_graph_file
from modules.logger import initialize_logger
from modules.utils import get_date_time

LOGGER = initialize_logger()


def ontouml_json2graph() -> None:
    """ Main function for ontouml-json2graph. """

    # Initial time information
    time_screen_format = "%d-%m-%Y %H:%M:%S"
    start_date_time = get_date_time(time_screen_format)
    st = time.perf_counter()

    LOGGER.info(f"OntoUML JSON2Graph decoder started on {start_date_time}!")

    # Treat arguments
    arguments_dictionary = treat_user_arguments()
    json_path = arguments_dictionary["json_path"]
    graph_format = arguments_dictionary["format"]

    # Load JSON
    json_data = safe_load_json_file(json_path)

    # Decode JSON into Graph
    ontouml_graph = decode_json_to_graph(json_data)

    # Get software's execution conclusion time
    end_date_time = get_date_time(time_screen_format)
    et = time.perf_counter()
    elapsed_time = round((et - st), 3)

    LOGGER.info(f"Decoding concluded on {end_date_time}. Total execution time: {elapsed_time} seconds.")

    # Save graph as specified format
    save_graph_file(ontouml_graph, json_path, graph_format)


if __name__ == '__main__':
    ontouml_json2graph()
