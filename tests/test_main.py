""" Main test function. """

import pytest

from main import ontouml_json2graph
from tests.test_aux import compare_graphs, get_test_list

LIST_OF_TESTS = get_test_list()


@pytest.mark.parametrize("input_file", LIST_OF_TESTS)
def test_ontouml_json2graph(input_file: str) -> None:
    """ Main function for testing the OntoUML JSON2Graph software.

    The test is based on the comparison of the generated graph (from a JSON file provided in the test folder)
    with a expected resulting graph (also provided in the test folder).

    :param input_file: Path to the JSON file to be tested.
    :type input_file: str
    """

    # Create resulting Graph in ttl syntax
    resulting_graph_file = ontouml_json2graph(input_file, "ttl", "test")

    # Getting expected result
    expected_graph_file = input_file.replace(".json", ".ttl")

    # Comparing resulting and expected graphs
    is_equal = compare_graphs(resulting_graph_file, expected_graph_file)

    assert is_equal
