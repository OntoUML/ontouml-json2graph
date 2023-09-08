""" Functions that performs validations for different functions or parameters used in the software. """

import inspect
import os

from .errors import report_error_invalid_parameter, report_error_requirement_not_met


def validate_arg_input(input_path: str, decode_all: bool) -> None:
    """ Validates the input path received as argument.

    :param input_path: The path to the input file or directory.
    :type input_path: str
    :param decode_all: A flag indicating whether to decode all files in the directory.
    :type decode_all: bool
    """

    # Verification 1: Checking if path or file exists
    if not os.path.exists(input_path):
        report_error_requirement_not_met("Provided input path does not exist. Execution finished.")

    # Verification 2: Checking if it is a file or a directory according to the decode_all argument
    if decode_all and (not os.path.isdir(input_path)):
        report_error_requirement_not_met("Provided input is not a directory. Execution finished.")
    elif (not decode_all) and (not os.path.isfile(input_path)):
        report_error_requirement_not_met("Provided input is not a file. Execution finished.")

    # Verification 3: Checking if provided input file type is valid
    if (not decode_all) and (".json" not in input_path):
        report_error_requirement_not_met("Provided input file must be of JSON type. Execution finished.")


def validate_execution_mode(execution_mode):
    """ Validate the provided execution mode against a list of valid modes.

    This function validates the given execution mode against a predefined list of valid modes: ["script", "import",
    "test"]. It ensures that the provided mode is one of the accepted values, and if not, raises an error indicating
    the invalid parameter.

    :param execution_mode: The execution mode to be validated.
    :type execution_mode: str
    """

    valid_execution_modes = ["script", "import", "test"]
    if execution_mode not in valid_execution_modes:
        current_function = inspect.stack()[0][3]
        report_error_invalid_parameter(execution_mode, valid_execution_modes, current_function)
