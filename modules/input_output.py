""" IO functions used in diverse occasions. """

import json
import os
from pathlib import Path

from rdflib import Graph

from modules.errors import report_error_io_read, report_error_io_write
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def create_directory_if_not_exists(directory_path: str, file_description: str) -> None:
    """ Checks if the directory that has the path received as argument exists.
    If it does, do nothing. If it does not, create it.

    :param directory_path: Path to the directory to be created (if it does not exist).
    :type directory_path: str
    """

    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except OSError as error:
        if file_description is None:
            file_description = "directory"
        report_error_io_write(directory_path, file_description, error)


def safe_load_json_file(json_path: str) -> dict:
    """ Safely loads the JSON file inputted by the user as an argument into a dictionary.

    :param json_path: Path to the JSON file to be loaded.
    :type json_path: str
    :return: Dictionary with loaded JSON's data.
    :rtype: dict
    """

    try:
        with open(json_path, "r") as read_file:
            json_data = json.load(read_file)
    except IOError as error:
        file_description = f"input json file"
        report_error_io_read(json_path, file_description, error)

    LOGGER.debug(f"JSON file {json_path} successfully loaded to dictionary.")

    return json_data


def save_graph_file(ontouml_graph: Graph, json_path: str, graph_format: str) -> None:
    """Saves the ontology graph into a file with syntax defined by the user.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param end_date_time_file: String containing the software's execution end date and time.
    :type end_date_time_file: str
    :param json_path: Path to the input json file.
    :type json_path: str
    :param graph_format: Syntax selected by the user to save the graph.
    :type graph_format: str
    """

    # Collecting information for result file name and path
    project_directory = os.getcwd()
    results_directory = "results"
    loaded_file_name = Path(json_path).stem

    # If directory 'results_directory' not exists, create it
    create_directory_if_not_exists(results_directory, "results directory")

    # Setting file complete path
    output_file_name = loaded_file_name + "." + graph_format
    output_file_path = project_directory + "\\" + results_directory + "\\" + output_file_name

    safe_save_graph_file(ontouml_graph, output_file_path, graph_format)


def safe_save_graph_file(ontouml_graph: Graph, output_file_name: str, syntax: str) -> None:
    """ Safely saves the graph into a file in the informed destination with the desired syntax.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param output_file_name: Created output file name.
    :type output_file_name: str
    :param syntax: Syntax to be used for saving the ontology file.
    :type syntax: str
    """

    try:
        ontouml_graph.serialize(destination=output_file_name, encoding='utf-8', format=syntax)
    except OSError as error:
        file_description = f"output graph file"
        report_error_io_write(output_file_name, file_description, error)

    LOGGER.info(f"Output graph file successfully saved at {output_file_name}.")
