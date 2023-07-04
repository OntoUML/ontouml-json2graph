""" Diverse util and auxiliary functions. """
from datetime import datetime

from modules.logger import initialize_logger

LOGGER = initialize_logger()

def count_element(element_type:str, element_counting:dict)->int:
    """ Returns the number of elements of a given type in the already counted data.
    Receives a dictionary of number of items and returns the value corresponding to the provided argument.

    :param element_type: Type of the element to have its count value returned.
    :type element_type: str
    :param element_counting: Dictionary with types and corresponding number of occurrences.
    :type element_counting: dict
    :return: Number of occurrences of the element of the given type.
    :rtype: int
    """
    if element_type in element_counting:
        num_element = element_counting[element_type]
    else:
        num_element = 0

    return num_element

def get_date_time(date_time_format: str) -> str:
    """ Return a string with date and time according to the specified format received as argument.
    For valid formats: https://docs.python.org/3.11/library/datetime.html#strftime-and-strptime-format-codes

    :param date_time_format: Valid format accepted by the datetime function.
    :type date_time_format: str
    :return: Formatted current date and time.
    :rtype: str
    """

    now = datetime.now()
    date_time = now.strftime(date_time_format)

    return date_time
