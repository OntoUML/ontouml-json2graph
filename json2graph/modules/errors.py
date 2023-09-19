"""Provide a collection of functions for reporting various error scenarios that can occur during the \
software's execution.

These functions are designed to improve the robustness and reliability of the program by providing clear error messages
and raising appropriate exceptions when necessary.
"""
from .logger import initialize_logger

LOGGER = initialize_logger()


def report_error_requirement_not_met(error_message: str) -> None:
    """Report the error caused when a requirement is not met. As this is a generic function, the error message \
    parameter must be used to identify the error to the user.

    :param error_message: Message to be printed to the user indicating the detected error.
    :type error_message: str

    :raises ValueError: Always.
    """
    LOGGER.error(f"{error_message} Program aborted.")
    raise ValueError("Software's requirement not met!")


def report_error_invalid_parameter(
    invalid_parameter: str, list_valid_parameters: list[str], caller_function_name: str
) -> None:
    """Report the error caused when an invalid parameter is passed to a function. E.g., the function accepts (i.e., \
    list_valid_parameters is) ["alfa", "beta"] and the received parameter (invalid_parameter) was "gama".

    NOTE 1: This function must be used only for validation of parameters of type string.
    NOTE 2: caller_function_name can be obtained from 'current_function = inspect.stack()[0][3]'

    :param invalid_parameter: Used parameter value that was evaluated as not valid.
    :type invalid_parameter: str
    :param list_valid_parameters: List of valid values for the evaluated parameter.
    :type list_valid_parameters: list[str]
    :param caller_function_name: Name of the function in which the invalid parameter was used.
    :type caller_function_name: str

    :raises ValueError: Always.
    """
    LOGGER.error(
        f"Value {invalid_parameter} received as parameter in function {caller_function_name} is invalid. "
        f"Valid values for this parameter are: {list_valid_parameters}. Program aborted."
    )
    raise ValueError("Invalid parameter!")


def report_error_end_of_switch(invalid_parameter: str, caller_function_name: str) -> None:
    """Report the error caused when an invalid parameter is provided to a switch case (if-else statements). \
    Used to validate parameters.

    NOTE: caller_function_name can be obtained from 'current_function = inspect.stack()[0][3]'

    :param invalid_parameter: Invalid function parameter that caused the error.
    :type invalid_parameter: str
    :param caller_function_name: Name of the function in which the invalid parameter was used.
    :type caller_function_name: str

    :raises ValueError: Always.
    """
    LOGGER.error(
        f"Unexpected parameter {invalid_parameter} received in function {caller_function_name}. Program aborted."
    )
    raise ValueError("End of switch (if-else statements) without valid parameter!")


def report_error_io_read(desired_content: str, file_description: str, error: OSError) -> None:
    """Report the error caused program cannot read or load the desired content (test_files or directories).

    :param desired_content: Name of the file used by the IO operation caused the error.
    :type desired_content: str
    :param file_description: Description of the file in desired_content.
    :type file_description: str
    :param error: Error raised by the IO operation.
    :type error: OSError

    :raises OSError: Always.
    """
    LOGGER.error(f"Could not load or read the {file_description} {desired_content}. Program aborted.")
    raise OSError(error)


def report_error_io_write(desired_content: str, file_description: str, error: OSError) -> None:
    """Report the error caused program cannot save or write the desired content (test_files or directories).

    :param desired_content: Name of the file used by the IO operation caused the error.
    :type desired_content: str
    :param file_description: Description of the file in desired_content.
    :type file_description: str
    :param error: Error raised by the IO operation.
    :type error: OSError

    :raises OSError: Always.
    """
    LOGGER.error(f"Could not create, write, or save the {file_description} {desired_content}. Program aborted.")
    raise OSError(error)
