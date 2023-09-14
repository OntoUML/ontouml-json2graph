""" This module provides functions for configuring a logger that outputs messages to the console.
The logger can be customized based on different execution modes, allowing you to control the log level.
"""

import logging
from datetime import datetime


def logger_get_date_time() -> str:
    """Return a string in a specified format with date and time.

    :return: Formatted date and time. Format example: 2022.10.23-14.43
    :rtype: str
    """

    now = datetime.now()
    date_time = now.strftime("%Y.%m.%d-%H.%M.%S")

    return date_time


def initialize_logger(execution_mode: str = "script") -> logging.Logger:
    """Create and initialize logger named 'execution-logger'.

    Different triggers are defined for each execution mode:
        - script: INFO
        - import: ERROR
        - test: ERROR

    :param execution_mode: Information about execution mode. Valid values are 'script', 'import' and 'test'.
    :type execution_mode: str
    :return: Created logger called 'execution-logger'.
    :rtype: logging.Logger
    """

    # Create a custom logger
    new_logger = logging.getLogger("execution-logger")

    # Setting lower level
    new_logger.setLevel(logging.DEBUG)

    # Creates a new logger only if current logger does not exist
    if not logging.getLogger("execution-logger").hasHandlers():
        # Creating CONSOLE handlers
        console_handler = logging.StreamHandler()

        if execution_mode == "script":
            console_handler.setLevel(logging.INFO)
        else:
            console_handler.setLevel(logging.ERROR)

        # Create formatters and add it to handlers
        console_format = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_format)

        # Add handlers to the logger
        new_logger.addHandler(console_handler)

    return new_logger
