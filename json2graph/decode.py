""" It provides a convenient interface for converting OntoUML JSON files into knowledge graphs,
with the flexibility to customize the output and control the execution mode for different use cases.

Usage:
1. Standalone Execution:
    When this module is executed as a standalone script:
    - The user can provide arguments via the command line to control the conversion process.
    - The `ontouml_json2graph` function is called with the provided arguments for the transformation.

2. Library Usage:
    This module can be used as a library by importing and calling the `ontouml_json2graph` function directly
    with appropriate parameters.

Note:
- Ensure that the required OntoUML JSON file is available before executing the transformation.


"""
import os
import time
from pathlib import Path

from rdflib import RDF, Graph

try:
    from .modules import arguments as args
    from .modules.decoder.decode_main import decode_json_to_graph
    from .modules.globals import METADATA
    from .modules.input_output import safe_load_json_file, create_directory_if_not_exists, safe_write_graph_file
    from .modules.logger import initialize_logger
    from .modules.utils_general import get_date_time
except ImportError:
    from modules import arguments as args
    from modules.decoder.decode_main import decode_json_to_graph
    from modules.globals import METADATA
    from modules.input_output import safe_load_json_file, create_directory_if_not_exists, safe_write_graph_file
    from modules.logger import initialize_logger
    from modules.utils_general import get_date_time


def decode_ontouml_json2graph(json_path: str,
                              base_uri: str = "https://example.org#",
                              graph_format: str = "ttl",
                              language: str = "",
                              model_only: bool = False,
                              silent: bool = True,
                              correct: bool = False,
                              execution_mode: str = "import") -> str | Graph:
    """ Main function for converting OntoUML JSON data to a Knowledge Graph.

    This function takes the path to a JSON file representing OntoUML model data provided by the user
    and converts it into a knowledge graph following the specified options.

    :param json_path: Path to the JSON file to be decoded provided by the user.
    :type json_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
    Default is "https://example.org#". (Optional)
    :type base_uri: str
    :param graph_format: Format for saving the resulting knowledge graph.
    Default value is 'ttl' (Turtle syntax). (Optional)
    :type graph_format: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param model_only: If True, only the OntoUML model will be extracted without diagrammatic information. (Optional)
    :type model_only: bool
    :param silent: If True, suppresses intermediate communications and log messages during execution. (Optional)
    :type silent: bool
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool
    :param execution_mode: Information about the execution mode.
    Valid values are 'import' (default), 'script', and 'test'. (Optional)
    :type execution_mode: str

    :returns: Saved output file path. Used for testing.
    :rtype: str
    """

    logger = initialize_logger(execution_mode)

    model_elements = ["Class", "Property", "Generalization", "GeneralizationSet", "Relation", "Cardinality"]

    if execution_mode != "script":
        args.initialize_arguments(json_path, base_uri, graph_format, language, model_only, silent, correct,
                                  execution_mode)

    if execution_mode == "script" and not args.ARGUMENTS["silent"]:
        # Initial time information
        time_screen_format = "%d-%m-%Y %H:%M:%S"
        start_date_time = get_date_time(time_screen_format)
        st = time.perf_counter()

        logger.info(f"{METADATA['name']} v{METADATA['version']} started on {start_date_time}!")
        logger.debug(f"Selected arguments are: {args.ARGUMENTS}")
        logger.info(f"Decoding JSON file {json_path} to {(args.ARGUMENTS['format']).upper()} graph format.\n")

        if not args.ARGUMENTS['language']:
            logger.warning("Ontology's language not informed by the user. "
                           "Transformation will not generate language tag.")
        if not args.ARGUMENTS['correct']:
            logger.warning("Basic correction feature not enabled by the user. "
                           "The transformation may generate an invalid result.")

    # Load JSON
    json_data = safe_load_json_file(json_path)

    # Decode JSON into Graph
    ontouml_graph = decode_json_to_graph(json_data, language, execution_mode)

    # If set by user, remove all diagrammatic elements
    if args.ARGUMENTS["model_only"]:
        for s, p, o in ontouml_graph.triples((None, RDF.type, None)):
            s_type = s.toPython()
            o_type = o.fragment
            # Remove if not a model element and if it is defined by of the ontology being handled
            if (args.ARGUMENTS["base_uri"] in s_type) and (o_type not in model_elements):
                ontouml_graph.remove((s, None, None))
                ontouml_graph.remove((None, None, s))
        if not args.ARGUMENTS["silent"]:
            logger.info("All diagrammatic data removed from the output. The output contains only model elements.")

    if execution_mode == "script" and not args.ARGUMENTS["silent"]:
        # Get software's execution conclusion time
        end_date_time = get_date_time(time_screen_format)
        et = time.perf_counter()
        elapsed_time = round((et - st), 3)
        logger.info(f"Decoding concluded on {end_date_time}. Total execution time: {elapsed_time} seconds.")

    # For execution as a script and for test, the file is always written
    if execution_mode != "import":
        # Save graph as specified format
        output_file_path = write_graph_file(ontouml_graph, json_path, graph_format)
        logger.info(f"Output graph file successfully saved at {output_file_path}.")
        if execution_mode == "test":
            return output_file_path
    # If execution_mode == "import", than the graph is returned to be processed by the user's application
    else:
        return ontouml_graph


def write_graph_file(ontouml_graph: Graph, json_path: str, graph_format: str) -> str:
    """Saves the ontology graph into a file with syntax defined by the user.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param json_path: Path to the input json file.
    :type json_path: str
    :param graph_format: Syntax selected by the user to save the graph.
    :type graph_format: str
    :return: Saved output file path.
    :rtype: str
    """

    # Collecting information for result file name and path
    project_directory = os.getcwd()
    results_directory = "results"
    loaded_file_name = Path(json_path).stem

    # If directory 'results_directory' not exists, create it
    create_directory_if_not_exists(results_directory, "results directory")

    # Setting file complete path
    output_file_name = loaded_file_name + "." + graph_format
    output_file_path = project_directory + "\\" + results_directory + "\\" + output_file_name

    safe_write_graph_file(ontouml_graph, output_file_path, graph_format)

    return output_file_path


if __name__ == '__main__':
    """Execute OntoUML JSON to Graph Transformation.

    This block of code is executed when the script is run as a standalone application. 
    It processes user-provided arguments and executes the OntoUML JSON to Graph transformation.
    """

    # Treat and publish user's arguments
    args.initialize_arguments(execution_mode="script")

    # Execute the transformation
    decode_ontouml_json2graph(json_path=args.ARGUMENTS["json_path"], execution_mode="script")
