""" Auxiliary test functions. """
import glob

import modules.arguments as args
from modules.globals import METADATA
from modules.input_output import safe_write_graph_file
from modules.utils_graph import load_graph_safely
from rdflib import Graph
from rdflib.compare import graph_diff, to_isomorphic


def get_test_list() -> list[str]:
    """ Returns a list with all JSON files in the test_files folder.

    :return: List with complete path of all JSON files in the test_files folder.
    :rtype: list[str]
    """

    test_files_folder = "test_files/"
    list_test_files = glob.glob(test_files_folder + '*.json')
    list_test_files.sort()

    return list_test_files


def print_graphs_differences(iso_result_graph: Graph, iso_expected_graph: Graph, test_name: str):
    """ Print three files:
        - test*_both.ttl: contains the statements that are present in both the resulting and expected graphs.
        - test*_or.ttl: contains the statements that are present only in the resulting graph.
        - test*_oe.ttl: contains the statements that are present only in the expected graph.

    :param iso_result_graph: Isomorphic resulting graph.
    :type iso_result_graph: Graph
    :param iso_expected_graph: Isomorphic expected graph.
    :type iso_expected_graph: Graph
    :param test_name: Name of the test to be used for printing comparison if evaluation result is negative.
    :type test_name: str
    """

    in_both, in_resulting, in_expected = graph_diff(iso_result_graph, iso_expected_graph)

    in_both.bind("ontouml", METADATA["conformsToBase"])
    in_both.bind("", args.ARGUMENTS["base_uri"])

    in_resulting.bind("ontouml", METADATA["conformsToBase"])
    in_resulting.bind("", args.ARGUMENTS["base_uri"])

    in_expected.bind("ontouml", METADATA["conformsToBase"])
    in_expected.bind("", args.ARGUMENTS["base_uri"])

    base_path = "results/"

    safe_write_graph_file(in_both, base_path + test_name + "_both.ttl", "ttl")
    safe_write_graph_file(in_resulting, base_path + test_name + "_only_result.ttl", "ttl")
    safe_write_graph_file(in_expected, base_path + test_name + "_only_expect.ttl", "ttl")


def compare_graphs(resulting_graph_path: str, expected_graph_path: str, test_name: str) -> bool:
    """ Verifies if resulting graph corresponds to expected graph.

    :param resulting_graph_path: Path to the generated resulting graph file.
    :type resulting_graph_path: str
    :param expected_graph_path: Path to the expected graph file.
    :type expected_graph_path: str
    :param test_name: Name of the test to be used for printing comparison if evaluation result is negative.
    :type test_name: str
    :return: Boolean value indicating if the resulting and expected graphs are equal.
    :rtype: bool
    """

    result_graph = load_graph_safely(resulting_graph_path)
    expected_graph = load_graph_safely(expected_graph_path)

    iso_result_graph = to_isomorphic(result_graph)
    iso_expected_graph = to_isomorphic(expected_graph)

    is_equal = (iso_result_graph == iso_expected_graph)

    if not is_equal:
        print_graphs_differences(iso_result_graph, iso_expected_graph, test_name)

    return is_equal
