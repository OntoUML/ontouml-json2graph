"""IO functions used in diverse occasions."""
import json
import os
import urllib

from icecream import ic
from rdflib import Graph

from .errors import report_error_io_read, report_error_io_write
from .logger import initialize_logger

LOGGER = initialize_logger()


def create_directory_if_not_exists(directory_path: str, file_description: str) -> None:
    """Check if the directory that has the path received as argument exists. \
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


def fix_uri(url_string) -> str:
    """To do."""
    # Step 1: Parse the URL
    parsed_url = urllib.parse.urlparse(url_string)

    # Step 2: URL Encode Non-URI Characters
    # Encode non-ASCII characters and spaces in the path and query components
    encoded_path = urllib.parse.quote(parsed_url.path)
    encoded_query = urllib.parse.quote(parsed_url.query)
    encoded_scheme = urllib.parse.quote(parsed_url.scheme)
    encoded_netloc = urllib.parse.quote(parsed_url.netloc)
    encoded_fragment = urllib.parse.quote(parsed_url.fragment)

    # Step 3: Reconstruct the URI
    valid_uri = urllib.parse.urlunparse(
        (
            encoded_scheme,
            encoded_netloc,
            encoded_path,
            "",  # Empty string for params
            encoded_query,
            encoded_fragment,
        )
    )

    return valid_uri


def safe_write_graph_file(ontouml_graph: Graph, output_file_path: str, syntax: str) -> None:
    """Safely saves the graph into a file in the informed destination with the desired syntax.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param output_file_path: Complete path of the output file to be created (including name and extension).
    :type output_file_path: str
    :param syntax: Syntax to be used for saving the ontology file.
    :type syntax: str
    """
    try:
        ontouml_graph.serialize(destination=output_file_path, encoding="utf-8", format=syntax)
    except Exception:
        for s, p, o in ontouml_graph:
            if "URIRef" in str(type(s)):
                old_s = s.toPython()
                new_s = fix_uri(old_s)
                if old_s != new_s:
                    ic(old_s, new_s)
            if "URIRef" in str(type(p)):
                old_p = p.toPython()
                new_p = fix_uri(old_p)
                if old_p != new_p:
                    ic(old_p, new_p)
            if "URIRef" in str(type(o)):
                old_o = o.toPython()
                new_o = fix_uri(old_o)
                if old_o != new_o:
                    ic(old_o, new_o)
        # ontouml_graph.serialize(destination=output_file_path, encoding="utf-8", format=syntax)
    except OSError as errorOS:
        file_description = "output graph file - OSError"
        report_error_io_write(output_file_path, file_description, errorOS)
