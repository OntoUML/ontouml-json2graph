""" Functions to be used in diverse occasions. """
import json

from modules.errors import report_error_io_read
from modules.logger import initialize_logger

LOGGER = initialize_logger()


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
