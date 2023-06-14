""" Argument Treatments """

import argparse

from modules.globals import ALLOWED_GRAPH_FORMATS, SOFTWARE_ACRONYM, SOFTWARE_VERSION, SOFTWARE_NAME, SOFTWARE_URL
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def treat_user_arguments() -> dict:
    """
    Treat arguments provided by the user when starting software execution.

    :return: Dictionary with json path (key 'json_path') and final file format (key 'format').
    :rtype: dict
    """

    LOGGER.debug("Parsing user's arguments...")

    about_message = SOFTWARE_ACRONYM + " - version " + SOFTWARE_VERSION

    # PARSING ARGUMENTS
    arguments_parser = argparse.ArgumentParser(prog="ontouml-json2graph",
                                               description=SOFTWARE_ACRONYM + " - " + SOFTWARE_NAME, allow_abbrev=False,
                                               epilog="More information at: " + SOFTWARE_URL)

    arguments_parser.version = about_message

    # POSITIONAL ARGUMENT
    arguments_parser.add_argument("json_file", type=str, action="store", help="The path of the json file to be loaded.")

    # OPTION ARGUMENT
    arguments_parser.add_argument("-f", "--format", action="store", choices=ALLOWED_GRAPH_FORMATS, default="ttl",
                                  help="Format to save the decoded file Must be a valid format according to: "
                                       "https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf")

    # AUTOMATIC ARGUMENTS
    arguments_parser.add_argument("-v", "--version", action="version", help="Print the software version and exit.")

    # Execute arguments parser
    arguments = arguments_parser.parse_args()

    # Asserting dictionary keys
    arguments_dictionary = {"format": arguments.format, "json_path": arguments.ontology_file}

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")

    return arguments_dictionary
