""" Logging configurations. """

import logging
import os
from datetime import datetime


def logger_get_date_time() -> str:
    """ Return a string in a specified format with date and time. Format example: 2022.10.23-14.43

    :return: Formatted date and time.
    :rtype: str
    """

    now = datetime.now()
    date_time = now.strftime("%Y.%m.%d-%H.%M.%S")

    return date_time


def initialize_logger(execution_mode: str = "production") -> logging.Logger:
    """ Create and initialize logger. The created logger is called 'execution-logger'.
    Different triggers are defined for each execution mode:
        - production: INFO
        - test: ERROR

    :param execution_mode: Information about execution mode. Valid values are 'production' and 'test'.
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

        if execution_mode == "production":
            console_handler.setLevel(logging.INFO)
        else:
            console_handler.setLevel(logging.ERROR)

        # If directory "/log" does not exist, create it
        # IMPORTANT: do not substitute for own error function because of circular dependency.
        log_directory = "logs/"
        try:
            if not os.path.exists(log_directory):
                os.makedirs(log_directory)
        except OSError as error:
            print(f"Could not create log directory {log_directory}. Program aborted.")
            raise OSError(error)

        # Creating FILE handler
        file_handler = logging.FileHandler(f"{log_directory}{logger_get_date_time()}.log")
        file_handler.setLevel(logging.DEBUG)

        # Create formatters and add it to handlers
        console_format = logging.Formatter('%(levelname)s - %(message)s')
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s [func: %(funcName)s '
                                        'in %(filename)s]')
        console_handler.setFormatter(console_format)
        file_handler.setFormatter(file_format)

        # Add handlers to the logger
        new_logger.addHandler(console_handler)
        new_logger.addHandler(file_handler)

    return new_logger
