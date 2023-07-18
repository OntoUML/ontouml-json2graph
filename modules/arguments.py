""" Argument Treatments """

import argparse

import validators as validators

from globals import SOFTWARE_ACRONYM, SOFTWARE_VERSION, SOFTWARE_NAME, SOFTWARE_URL, ALLOWED_GRAPH_FORMATS
from modules.logger import initialize_logger

LOGGER = initialize_logger()
ARGUMENTS = {}


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
    arguments_parser.add_argument("-l", "--language", action="store", type=str, default="",
                                  help="Language tag for the ontology's concepts. Default is None.")
    arguments_parser.add_argument("-c", "--correct", action="store_true",
                                  help="Enables syntactical and semantic validations and corrections.")
    arguments_parser.add_argument("-s", "--silent", action="store_true",
                                  help="Silent mode. Does not present validation warnings and errors.")
    arguments_parser.add_argument("-u", "--base_uri", action="store", type=str, default="https://example.org#",
                                  help="Base URI of the resulting graph. Default is 'https://example.org#'.")

    # AUTOMATIC ARGUMENTS
    arguments_parser.add_argument("-v", "--version", action="version", help="Print the software version and exit.")

    # Execute arguments parser
    arguments = arguments_parser.parse_args()

    # Asserting dictionary keys
    arguments_dictionary = {"format": arguments.format,
                            "language": arguments.language,
                            "correct": arguments.correct,
                            "silent": arguments.silent,
                            "json_path": arguments.json_file,
                            "base_uri": arguments.base_uri}

    # Checking if provided input file type is valid
    if ".json" not in arguments.json_file:
        raise ValueError("Provided input file must be of JSON type. Execution finished.")

    # Checking if provided URI is valid and if it has '/' or '#' at the end
    if not validators.url(arguments.base_uri):
        raise ValueError("Provided base URI is invalid. Execution finished.")
    elif (arguments.base_uri[-1] != '#') and (arguments.base_uri[-1] != '/'):
        arguments_dictionary["base_uri"] += '#'

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")

    return arguments_dictionary


def publish_user_arguments():
    arguments_dictionary = treat_user_arguments()
    global ARGUMENTS
    ARGUMENTS = arguments_dictionary
