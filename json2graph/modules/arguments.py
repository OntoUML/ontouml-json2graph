""" Argument Treatments Module.

This module provides functions for parsing and validating user-provided arguments when starting the software execution
as a script.

It also makes the ARGUMENTS variable globally accessible with the user's arguments (when executed as a script) or with
default values (when executed as test or as a library).
"""

import argparse
import os

import validators

from .errors import report_error_requirement_not_met
from .globals import METADATA
from .input_output import create_directory_if_not_exists
from .logger import initialize_logger
from .utils_validations import validate_arg_input

ARGUMENTS = {}

LOGGER = initialize_logger()


def initialize_args_script() -> None:
    """ This function parses the command-line arguments provided by the user and performs necessary validations.
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

    # OPTIONAL ARGUMENT
    args_parser.add_argument("-i", "--input_path", type=str, action="store", required=True,
                             help="The path of the JSON file or directory with JSON files to be decoded.")
    args_parser.add_argument("-o", "--output_path", type=str, action="store", default=os.getcwd(),
                             help="The path of the directory in which the resulting decoded file(s) will be saved. "
                                  "Default is the working directory.")

    args_parser.add_argument("-a", "--decode_all", action="store_true",
                             help="Converts all JSON files in the informed path.")
    args_parser.add_argument("-f", "--format", type=str, action="store", choices=allowed_graph_formats, default="ttl",
                             help="Format to save the decoded file. Default is 'ttl'.")
    args_parser.add_argument("-l", "--language", type=str, action="store", default="",
                             help="Language tag for the ontology's concepts. Default is 'None'.")
    args_parser.add_argument("-c", "--correct", action="store_true", default=False,
                             help="Enables syntactical and semantic validations and corrections.")
    args_parser.add_argument("-s", "--silent", action="store_true", default=False,
                             help="Silent mode. Does not present validation warnings and errors.")
    args_parser.add_argument("-u", "--base_uri", type=str, action="store", default="https://example.org#",
                             help="Base URI of the resulting graph. Default is 'https://example.org#'.")
    args_parser.add_argument("-m", "--model_only", action="store_true",
                             help="Keep only model elements, eliminating all diagrammatic data from output.")

    # AUTOMATIC ARGUMENTS
    args_parser.add_argument("-v", "--version", action="version", help="Print the software version and exit.")

    # Execute arguments parser
    arguments = args_parser.parse_args()

    # Asserting dictionary keys
    arguments_dictionary = {
        "base_uri": arguments.base_uri,
        "correct": arguments.correct,
        "decode_all": arguments.decode_all,
        "format": arguments.format,
        "input_path": os.path.abspath(arguments.input_path),
        "language": arguments.language,
        "model_only": arguments.model_only,
        "output_path": os.path.abspath(arguments.output_path),
        "silent": arguments.silent,
    }

    # Input validation
    validate_arg_input(arguments.input_path, arguments.decode_all)

    # Output validation
    if os.path.isfile(arguments.output_path):
        report_error_requirement_not_met("Provided output path is not a directory. Execution finished.")
    if not os.path.exists(arguments.output_path):
        create_directory_if_not_exists(arguments.output_path, "output directory")
        LOGGER.info("The provided output directory did not exist and was created.")

    # Checking if provided URI is valid. I.e., if it has '/' or '#' at the end. If it does not, add a '#'
    if not validators.url(arguments.base_uri):
        report_error_requirement_not_met("Provided base URI is invalid. Execution finished.")
    elif (arguments.base_uri[-1] != '#') and (arguments.base_uri[-1] != '/'):
        arguments_dictionary["base_uri"] += '#'

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")

    global ARGUMENTS
    ARGUMENTS = arguments_dictionary


def initialize_args_import(input_path: str = "not_initialized",
                           output_path: str = os.getcwd(),
                           base_uri: str = "https://example.org#",
                           graph_format: str = "ttl",
                           language: str = "",
                           model_only: bool = False,
                           silent: bool = True,
                           correct: bool = False):
    """ This function initializes the global variable ARGUMENTS of type dictionary, which contains user-provided
    (when executed in script mode) or default arguments (when executed as a library or for testing).
    The ARGUMENTS variable must be initialized in every possible execution mode.

    :param input_path: Path to the directory or JSON file to be decoded. (Optional)
    :type input_path: str
    :param output_path: Path to the directory in which the result file(s) will be saved. (Optional)
    :type output_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts. (Optional)
                     Default is "https://example.org#".
    :type base_uri: str
    :param graph_format: Format for saving the resulting knowledge graph. (Optional)
                         Default value is 'ttl' (Turtle syntax).
    :type graph_format: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param model_only: If True, only the OntoUML model will be extracted without diagrammatic information. (Optional)
    :type model_only: bool
    :param silent: If True, suppresses intermediate communications and log messages during execution. (Optional)
    :type silent: bool
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool
    """

    global ARGUMENTS

    ARGUMENTS["base_uri"] = base_uri
    ARGUMENTS["correct"] = correct
    ARGUMENTS["format"] = graph_format
    ARGUMENTS["input_path"] = input_path
    ARGUMENTS["language"] = language
    ARGUMENTS["model_only"] = model_only
    ARGUMENTS["output_path"] = output_path
    ARGUMENTS["silent"] = silent


def initialize_args_test(input_path: str = "not_initialized",
                         language: str = ""):
    """ This function initializes the global variable ARGUMENTS of type dictionary, which contains user-provided
    (when executed in script mode) or default arguments (when executed as a library or for testing).
    The ARGUMENTS variable must be initialized in every possible execution mode.

    :param input_path: Path to the directory or JSON file to be decoded. (Optional)
    :type input_path: str
    :param output_path: Path to the directory in which the result file(s) will be saved. (Optional)
    :type output_path: str
    :param decode_all: Informs if user wants to convert all json files in the input_path performing the decode
                        function multiple times. (Optional)
    :type decode_all: bool
    :param base_uri: Base URI to be used for generating URIs for ontology concepts. (Optional)
                     Default is "https://example.org#".
    :type base_uri: str
    :param graph_format: Format for saving the resulting knowledge graph. (Optional)
                         Default value is 'ttl' (Turtle syntax).
    :type graph_format: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param model_only: If True, only the OntoUML model will be extracted without diagrammatic information. (Optional)
    :type model_only: bool
    :param silent: If True, suppresses intermediate communications and log messages during execution. (Optional)
    :type silent: bool
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool
    """

    global ARGUMENTS

    ARGUMENTS["base_uri"] = "https://example.org#"
    ARGUMENTS["correct"] = True
    ARGUMENTS["format"] = "ttl"
    ARGUMENTS["input_path"] = input_path
    ARGUMENTS["language"] = language
    ARGUMENTS["model_only"] = False
    ARGUMENTS["output_path"] = "tests" + os.path.sep + "results"
    ARGUMENTS["silent"] = True
