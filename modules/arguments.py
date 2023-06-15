""" Argument Treatments """

import argparse

from globals import SOFTWARE_ACRONYM, SOFTWARE_VERSION, SOFTWARE_NAME, SOFTWARE_URL, ALLOWED_GRAPH_FORMATS
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def treat_user_arguments() -> dict:
    """ Treat arguments provided by the user when starting software execution.

    :return: Dictionary with json path (key 'json_path') and final file format (key 'format').
    :rtype: dict
    :raises OSError: If provided input is not of JSON type.
    """

    LOGGER.debug("Parsing user's arguments...")

    about_message = SOFTWARE_ACRONYM + " - version " + SOFTWARE_VERSION

    # PARSING ARGUMENTS
    arguments_parser = argparse.ArgumentParser(prog=SOFTWARE_ACRONYM,
                                               description=SOFTWARE_NAME + ". Version: " + SOFTWARE_VERSION,
                                               allow_abbrev=False, epilog="More information at: " + SOFTWARE_URL)

    arguments_parser.version = about_message

    # POSITIONAL ARGUMENT
    arguments_parser.add_argument("json_file", type=str, action="store",
                                  help="The path of the JSON file to be encoded.")

    # OPTIONAL ARGUMENT
    arguments_parser.add_argument("-f", "--format", action="store", choices=ALLOWED_GRAPH_FORMATS, default="ttl",
                                  help="Format to save the decoded file. Default is 'ttl'.")

    # AUTOMATIC ARGUMENTS
    arguments_parser.add_argument("-v", "--version", action="version", help="Print the software version and exit.")

    # Execute arguments parser
    arguments = arguments_parser.parse_args()

    # Asserting dictionary keys
    arguments_dictionary = {"format": arguments.format, "json_path": arguments.json_file}

    # Checking if provided input file type is valid
    if ".json" not in arguments.json_file:
        raise OSError("Provided input file must be of JSON type.")

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")

    return arguments_dictionary
