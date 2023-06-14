""" Argument Treatments """

import argparse

from scior.modules.logger_config import initialize_logger

LOGGER = initialize_logger()
ARGUMENTS = {}


def treat_user_arguments(software_acronym: str, software_name: str, software_version: str, software_url: str) -> dict:
    """ Treat arguments provided by the user when starting software execution. """

    LOGGER.debug("Parsing arguments...")

    about_message = software_acronym + " - version " + software_version

    # PARSING ARGUMENTS
    arguments_parser = argparse.ArgumentParser(prog="scior",
                                               description=software_acronym + " - " + software_name,
                                               allow_abbrev=False,
                                               epilog="Asterisks indicate default values. More information at: "
                                                      + software_url)

    arguments_parser.version = about_message

    # AUTOMATION LEVEL ARGUMENTS

    automation_group = arguments_parser.add_mutually_exclusive_group()

    automation_group.add_argument("-i", "--interactive", action='store_true', default=False,
                                  help="Execute automatic rules whenever possible, interactive rules when necessary.")

    automation_group.add_argument("-a", "--automatic", action='store_true', default=True,
                                  help="* Execute only automatic rules. Interactive rules are not performed.")

    # ONTOLOGY COMPLETENESS ARGUMENTS

    completeness_group = arguments_parser.add_mutually_exclusive_group()

    completeness_group.add_argument("-cwa", "--is_cwa", action='store_true', default=False,
                                    help="Operate in Closed-World Assumption (CWA).")

    # Regular Mode: Assume that single instances can be automatically classified.
    completeness_group.add_argument("-owa", "--is_owa", action='store_true', default=True,
                                    help="* Operate in Open-World Assumption (OWA) - Regular Mode.")

    # Light Mode: Single instances cannot be automatically classified.
    completeness_group.add_argument("-owaf", "--is_owaf", action='store_true', default=False,
                                    help="Operate in Open-World Assumption (OWA) - Forced Mode.")

    # VERBOSITY ARGUMENTS

    verbosity_group = arguments_parser.add_mutually_exclusive_group()

    verbosity_group.add_argument("-s", "--silent", action='store_true', default=False,
                                 help="Silent mode. Print only basic execution status information.")

    verbosity_group.add_argument("-r", "--verbose", action='store_true', default=True,
                                 help="* Print basic execution information and results.")

    verbosity_group.add_argument("-d", "--debug", action='store_true', default=False,
                                 help="Generates tons of log for debugging.")

    # REGISTER GUFO IN FILE ARGUMENTS

    gufo_in_file = arguments_parser.add_mutually_exclusive_group()

    gufo_in_file.add_argument("-gr", "--gufo_results", action='store_true', default=True,
                              help="* Write in the output ontology file only the gUFO classifications found.")

    gufo_in_file.add_argument("-gi", "--gufo_import", action='store_true', default=False,
                              help="Import gUFO ontology in the output ontology file.")

    gufo_in_file.add_argument("-gw", "--gufo_write", action='store_true', default=False,
                              help="Write all gUFO statements in the output ontology file.")

    # AUTOMATIC ARGUMENTS
    arguments_parser.add_argument("-v", "--version", action="version",
                                  help="Print the software version and exit.")

    # POSITIONAL ARGUMENT
    arguments_parser.add_argument("ontology_file", type=str, action="store",
                                  help="The path of the ontology file to be loaded.")

    # Execute arguments parser
    arguments = arguments_parser.parse_args()

    # Manually cleaning defaults when they are not used
    if arguments.interactive:
        arguments.automatic = False

    if arguments.is_cwa or arguments.is_owaf:
        arguments.is_owa = False

    if arguments.gufo_import or arguments.gufo_write:
        arguments.gufo_results = False

    if arguments.silent or arguments.debug:
        arguments.verbose = False

    # Asserting dictionary keys
    arguments_dictionary = {
        "is_automatic": arguments.automatic,
        "is_interactive": arguments.interactive,

        "is_cwa": arguments.is_cwa,
        "is_owa": arguments.is_owa,
        "is_owaf": arguments.is_owaf,

        "gufo_results": arguments.gufo_results,
        "gufo_import": arguments.gufo_import,
        "gufo_write": arguments.gufo_write,

        "is_silent": arguments.silent,
        "is_verbose": arguments.verbose,
        "is_debug": arguments.debug,

        "ontology_path": arguments.ontology_file
    }

    return arguments_dictionary


def publish_global_arguments(software_acronym: str, software_name: str, software_version: str, software_url: str,
                             arguments_dictionary: dict = None) -> None:
    """ Makes ARGUMENTS a global variable. """

    # Scior: dict equals None. Scior-Tester: the dictionary is directly received as argument.
    if arguments_dictionary is None:
        arguments_dictionary = treat_user_arguments(software_acronym, software_name, software_version, software_url)

    global ARGUMENTS
    ARGUMENTS = arguments_dictionary

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")
