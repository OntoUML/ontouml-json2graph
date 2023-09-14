""" IO functions used in diverse occasions. """

import json
import os

from rdflib import Graph

from .errors import report_error_io_read, report_error_io_write
from .logger import initialize_logger

LOGGER = initialize_logger()


def create_directory_if_not_exists(directory_path: str, file_description: str) -> None:
    """Checks if the directory that has the path received as argument exists.
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
    """Safely loads the JSON file inputted by the user as an argument into a dictionary.

    :param json_path: Path to the JSON file to be loaded.
    :type json_path: str
    :return: Dictionary with loaded JSON's data.
    :rtype: dict
    """

    try:
        with open(json_path, "r") as read_file:
            json_data = json.load(read_file)
    except IOError as error:
        file_description = "input json file"
        report_error_io_read(json_path, file_description, error)

    LOGGER.debug(f"JSON file {json_path} successfully loaded to dictionary.")

    return json_data


def safe_write_graph_file(
    ontouml_graph: Graph, output_file_path: str, syntax: str
) -> None:
    """Safely saves the graph into a file in the informed destination with the desired syntax.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param output_file_path: Complete path of the output file to be created (including name and extension).
    :type output_file_path: str
    :param syntax: Syntax to be used for saving the ontology file.
    :type syntax: str
    """

    try:
        ontouml_graph.serialize(
            destination=output_file_path, encoding="utf-8", format=syntax
        )
    except OSError as error:
        file_description = "output graph file"
        report_error_io_write(output_file_path, file_description, error)
