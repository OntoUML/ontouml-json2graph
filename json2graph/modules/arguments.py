""" Argument Treatments Module.

This module provides functions for parsing and validating user-provided arguments when starting the software execution
as a script.

It also makes the ARGUMENTS variable globally accessible with the user's arguments (when executed as a script) or with
default values (when executed as test or as a library).
"""

import argparse

import validators

from .errors import report_error_requirement_not_met
from .globals import METADATA
from .logger import initialize_logger

ARGUMENTS = {}

LOGGER = initialize_logger()


def treat_user_arguments() -> dict:
    """ This function parses the command-line arguments provided by the user and performs necessary validations.

    :return: Dictionary with json path (key 'json_path') and final file format (key 'format').
    :rtype: dict
    """

    # Formats for saving graphs supported by RDFLib
    # https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf
    allowed_graph_formats = ["turtle", "ttl", "turtle2", "xml", "pretty-xml", "json-ld", "ntriples", "nt", "nt11", "n3",
                             "trig", "trix", "nquads"]

    LOGGER.debug("Parsing user's arguments...")

    about_message = METADATA["name"] + " - version " + METADATA["version"]

    # PARSING ARGUMENTS
    args_parser = argparse.ArgumentParser(prog=METADATA["name"],
                                          description=METADATA["description"] + ". Version: " + METADATA["version"],
                                          allow_abbrev=False, epilog="More information at: " + METADATA["repository"])

    args_parser.version = about_message

    # POSITIONAL ARGUMENT
    args_parser.add_argument("json_path", type=str, action="store",
                             help="The path of the JSON file to be encoded.")

    # OPTIONAL ARGUMENT
    args_parser.add_argument("-f", "--format", action="store", choices=allowed_graph_formats, default="ttl",
                             help="Format to save the decoded file. Default is 'ttl'.")
    args_parser.add_argument("-l", "--language", action="store", type=str, default="",
                             help="Language tag for the ontology's concepts. Default is 'None'.")
    args_parser.add_argument("-c", "--correct", action="store_true",
                             help="Enables syntactical and semantic validations and corrections.")
    args_parser.add_argument("-s", "--silent", action="store_true",
                             help="Silent mode. Does not present validation warnings and errors.")
    args_parser.add_argument("-u", "--base_uri", action="store", type=str, default="https://example.org#",
                             help="Base URI of the resulting graph. Default is 'https://example.org#'.")
    args_parser.add_argument("-m", "--model_only", action="store_true",
                             help="Keep only model elements, eliminating all diagrammatic data from output.")

    # AUTOMATIC ARGUMENTS
    args_parser.add_argument("-v", "--version", action="version", help="Print the software version and exit.")

    # Execute arguments parser
    arguments = args_parser.parse_args()

    # Asserting dictionary keys
    arguments_dictionary = {"format": arguments.format,
                            "language": arguments.language,
                            "correct": arguments.correct,
                            "silent": arguments.silent,
                            "json_path": arguments.json_path,
                            "base_uri": arguments.base_uri,
                            "model_only": arguments.model_only}

    # Checking if provided input file type is valid
    if ".json" not in arguments.json_path:
        report_error_requirement_not_met("Provided input file must be of JSON type. Execution finished.")

    # Checking if provided URI is valid. I.e., if it has '/' or '#' at the end. If it does not, add a '#'
    if not validators.url(arguments.base_uri):
        report_error_requirement_not_met("Provided base URI is invalid. Execution finished.")
    elif (arguments.base_uri[-1] != '#') and (arguments.base_uri[-1] != '/'):
        arguments_dictionary["base_uri"] += '#'

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")

    return arguments_dictionary


def initialize_arguments(json_path: str = "not_initialized",
                         base_uri: str = "https://example.org#",
                         graph_format: str = "ttl",
                         language: str = "",
                         model_only: bool = False,
                         silent: bool = True,
                         correct: bool = False,
                         execution_mode: str = "import"):
    """ This function initializes the global variable ARGUMENTS of type dictionary, which contains user-provided
    (when executed in script mode) or default arguments (when executed as a library or for testing).
    The ARGUMENTS variable must be initialized in every possible execution mode.

    The valid execution modes are:
    - 'script': If used as a script, use user's arguments parsed from the command line.
    - 'package': When imported into external code, working as a library package.
    - 'test': Used for testing.


    :param json_path: Path to the JSON file to be decoded provided by the user. (Optional)
    :type json_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
    Default is "https://example.org#". (Optional)
    :type base_uri: str
    :param graph_format: Format for saving the resulting knowledge graph.
    Default value is 'ttl' (Turtle syntax). (Optional)
    :type graph_format: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param model_only: If True, only the OntoUML model will be extracted without diagrammatic information. (Optional)
    :type model_only: bool
    :param silent: If True, suppresses intermediate communications and log messages during execution. (Optional)
    :type silent: bool
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool
    :param execution_mode: Information about the execution mode.
    Valid values are 'import' (default), 'script', and 'test'. (Optional)
    :type execution_mode: str
    """

    global ARGUMENTS

    if execution_mode == "script":
        ARGUMENTS = treat_user_arguments()
    else:
        ARGUMENTS["base_uri"] = base_uri
        ARGUMENTS["correct"] = correct
        ARGUMENTS["format"] = graph_format
        ARGUMENTS["json_path"] = json_path
        ARGUMENTS["language"] = language
        ARGUMENTS["model_only"] = model_only
        ARGUMENTS["silent"] = silent

    if execution_mode == "test":
        ARGUMENTS["correct"] = True
