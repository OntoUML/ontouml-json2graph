""" Main test function. """
from pathlib import Path

import pytest

from main import ontouml_json2graph
from test_aux import get_test_list, compare_graphs

LIST_OF_TESTS = get_test_list()


@pytest.mark.parametrize("input_file", LIST_OF_TESTS)
def test_ontouml_json2graph(input_file: str) -> None:
    """ Main function for testing the OntoUML JSON2Graph software.

    The test is based on the comparison of the generated graph (from a JSON file provided in the test folder)
    with an expected resulting graph (also provided in the test folder).

    :param input_file: Path to the JSON file to be tested.
    :type input_file: str
    """

    test_name = Path(input_file).stem

    language = "en" if (int(test_name[-2:]) > 41) else ""

    # Create resulting Graph in ttl syntax
    resulting_graph_file = ontouml_json2graph(input_file, "ttl", language, "test")

    # Getting expected result
    expected_graph_file = input_file.replace(".json", ".ttl")

    # Comparing resulting and expected graphs
    is_equal = compare_graphs(resulting_graph_file, expected_graph_file, test_name)

    assert is_equal
