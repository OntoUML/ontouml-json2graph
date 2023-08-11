""" Functions that performs validations for different functions or parameters used in the software. """
import inspect

from json2graph.modules.errors import report_error_invalid_parameter


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