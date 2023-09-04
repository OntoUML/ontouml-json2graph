""" Main function used as script to convert OntoUML JSON files into knowledge graphs, with the flexibility to
customize the output and control the execution mode for different use cases.
"""
import glob
import inspect
import os
import time
from pathlib import Path

from rdflib import RDF, Graph

try:
    from .modules import arguments as args
    from .modules.globals import METADATA
    from .modules.input_output import safe_load_json_file, create_directory_if_not_exists, safe_write_graph_file
    from .modules.logger import initialize_logger
    from .modules.utils_general import get_date_time
    from .modules.utils_validations import validate_execution_mode
    from .modules.errors import report_error_end_of_switch
    from .decoder.decode_main import decode_json_to_graph
except ImportError:
    from modules import arguments as args
    from modules.globals import METADATA
    from modules.input_output import safe_load_json_file, create_directory_if_not_exists, safe_write_graph_file
    from modules.logger import initialize_logger
    from modules.utils_general import get_date_time
    from modules.utils_validations import validate_execution_mode
    from modules.errors import report_error_end_of_switch
    from decoder.decode_main import decode_json_to_graph


def decode_ontouml_json2graph(json_file_path: str, base_uri: str = "https://example.org#", language: str = "",
                              model_only: bool = False, silent: bool = True, correct: bool = False,
                              execution_mode: str = "import") -> Graph:
    """ Main function for converting OntoUML JSON data to a Knowledge Graph.

    This function takes the path to a JSON file representing OntoUML model data provided by the user
    and converts it into a knowledge graph following the specified options.

    :param json_file_path: Path to the JSON file to be decoded provided by the user.
    :type json_file_path: str
    :param base_uri: Base URI to be used for generating URIs for ontology concepts.
                     Default is https://example.org#. (Optional)
    :type base_uri: str
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

    :return: JSON data decoded into a RDFLib's Graph that is compliant with the OntoUML Vocabulary.
    :rtype: Graph
    """

    logger = initialize_logger(execution_mode)

    model_elements = ["Class", "Property", "Generalization", "GeneralizationSet", "Relation", "Cardinality"]

    validate_execution_mode(execution_mode)

    if execution_mode == "test":
        args.initialize_ars_test(input_path=json_file_path, language=language)
    elif execution_mode == "import":
        args.initialize_ars_import(input_path=json_file_path, base_uri=base_uri, language=language,
                                   model_only=model_only, silent=silent, correct=correct)

    if execution_mode == "script" and not args.ARGUMENTS["silent"]:
        # Initial time information
        time_screen_format = "%d-%m-%Y %H:%M:%S"
        start_date_time = get_date_time(time_screen_format)
        st = time.perf_counter()

        logger.info(f"{METADATA['description']} v{METADATA['version']} started on {start_date_time}!")
        logger.debug(f"Selected arguments are: {args.ARGUMENTS}")
        logger.info(f"Decoding JSON file {args.ARGUMENTS['input_path']} to {(args.ARGUMENTS['format']).upper()} graph "
                    f"format.\n")

        if not args.ARGUMENTS['language']:
            logger.warning("Ontology's language not informed by the user. "
                           "Transformation will not generate language tag.")
        if not args.ARGUMENTS['correct']:
            logger.warning("Basic correction feature not enabled by the user. "
                           "The transformation may generate an invalid result.")

    # Load JSON
    json_data = safe_load_json_file(json_file_path)

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

    return ontouml_graph


def write_graph_file(ontouml_graph: Graph, execution_mode: str = "script") -> str:
    """ Saves the ontology graph received as argument into a file using the syntax defined by the user.

    When running in script mode, the result is saved in the folder specified by the user as argument.
    When running in test mode, the file is saved inside the 'results' directory created by this function.
    Execution on

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param execution_mode: Information about the execution mode.
                           Valid values are 'import' (default), 'script', and 'test'. (Optional)
    :type execution_mode: str

    :return: Saved output file path.
    :rtype: str
    """

    logger = initialize_logger()
    loaded_file_name = Path(args.ARGUMENTS["input_path"]).stem

    if execution_mode == "test":
        # Collecting information for result file name and path
        project_directory = os.getcwd()
        results_directory = "results"

        # If directory 'results_directory' not exists, create it
        create_directory_if_not_exists(results_directory, "results directory")

        base_path = project_directory + os.path.sep + results_directory
    elif execution_mode == "script":
        base_path = args.ARGUMENTS["output_path"]
    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("execution_mode", current_function)

    # Setting file complete path
    output_file_name = loaded_file_name + "." + args.ARGUMENTS["format"]
    output_file_path = base_path + os.path.sep + output_file_name

    safe_write_graph_file(ontouml_graph, output_file_path, args.ARGUMENTS["format"])

    if not args.ARGUMENTS["silent"]:
        logger.info(f"Output graph file successfully saved at {output_file_path}.\n")

    return output_file_path


def decode_all_ontouml_json2graph() -> None:
    """ Decode multiple OntoUML JSON files.

    This function processes a directory of OntoUML JSON files and converts each file into a corresponding
    knowledge graph using the specified options. The output graphs are saved in the 'results' directory.
    """

    # Getting all
    list_input_files = glob.glob(os.path.join(args.ARGUMENTS["input_path"], '*.json'))

    for input_file in list_input_files:
        result_graph = decode_ontouml_json2graph(json_file_path=input_file, base_uri=args.ARGUMENTS["base_uri"],
                                                 language=args.ARGUMENTS["language"],
                                                 model_only=args.ARGUMENTS["model_only"],
                                                 silent=args.ARGUMENTS["silent"], correct=args.ARGUMENTS["correct"],
                                                 execution_mode="script")

        new_file_name = input_file.replace(".json", "." + args.ARGUMENTS["format"])
        args.ARGUMENTS["input_path"] = new_file_name
        write_graph_file(result_graph, execution_mode="script")


if __name__ == '__main__':
    """Execute OntoUML JSON to Graph Transformation.

    This block of code is executed when the script is run as a standalone application (i.e., as a script). 
    It processes user-provided arguments and executes the OntoUML JSON to Graph transformation.
    """

    # Treat and publish user's arguments
    args.initialize_args_script()

    if args.ARGUMENTS["decode_all"]:
        decode_all_ontouml_json2graph()
    else:
        # Convert JSON to Knowledge Graph
        decoded_graph = decode_ontouml_json2graph(json_file_path=args.ARGUMENTS["input_path"], execution_mode="script")
        # Saves knowledge graph
        write_graph_file(decoded_graph, execution_mode="script")
