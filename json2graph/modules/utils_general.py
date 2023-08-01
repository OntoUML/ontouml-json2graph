""" Diverse util and auxiliary functions. """
from datetime import datetime


def count_elements_types(element_type_list: list[str], element_counting: dict) -> int:
    """ Returns the number of elements (in the already counted data) of the types given in a list.
    Receives a dictionary of number of items and returns the value corresponding to the provided argument.

    :param element_type_list: List of types of elements to have their count value returned.
    :type element_type_list: list[str]
    :param element_counting: Dictionary with types and corresponding number of occurrences.
    :type element_counting: dict
    :return: Number of occurrences of the element of the given type.
    :rtype: int
    """

    num_element = 0

    for element_type in element_type_list:
        if element_type in element_counting:
            num_element += element_counting[element_type]

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
