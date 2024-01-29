"""Diverse util and auxiliary functions."""

from datetime import datetime


def get_date_time(date_time_format: str) -> str:
    """Return a string with date and time according to the specified format received as argument.

    For valid formats: https://docs.python.org/3.11/library/datetime.html#strftime-and-strptime-format-codes

    :param date_time_format: Valid format accepted by the datetime function.
    :type date_time_format: str
    :return: Formatted current date and time.
    :rtype: str
    """
    now = datetime.now()
    date_time = now.strftime(date_time_format)

    return date_time
