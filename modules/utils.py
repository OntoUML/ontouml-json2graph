""" Diverse util and auxiliary functions. """
from datetime import datetime

from rdflib import Graph

from modules.errors import report_error_io_read
from modules.logger import initialize_logger

LOGGER = initialize_logger()


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


def load_all_graph_safely(ontology_file: str) -> Graph:
    """ Safely load graph from file to working memory.

    :param ontology_file: Path to the ontology file to be loaded into the working memory.
    :type ontology_file: str
    :return: RDFLib graph loaded as object.
    :rtype: Graph
    """

    ontology_graph = Graph()

    try:
        ontology_graph.parse(ontology_file, encoding='utf-8')
    except OSError as error:
        file_description = f"input ontology file"
        report_error_io_read(ontology_file, file_description, error)

    LOGGER.info(f"Ontology file {ontology_file} successfully loaded to working memory.")

    return ontology_graph
