"""Main function used as script to convert OntoUML JSON files into knowledge graphs, with the flexibility to \
customize the output and control the execution mode for different use cases."""

import glob
import inspect
import os
import time
import warnings
from pathlib import Path

from rdflib import RDF, Graph

try:
    from .modules import arguments as args
    from .modules.content_identity import resolve_base_uri
    from .modules.metadata import METADATA
    from .modules.property_assignments import (
        apply_property_assignment_policy,
        collect_property_assignments,
    )
    from .modules.input_output import (
        safe_load_json_file,
        create_directory_if_not_exists,
        safe_write_graph_file,
    )
    from .modules.logger import initialize_logger
    from .modules.transformation_metadata import (
        build_transformation_metadata,
        get_transformation_configuration,
        graph_with_metadata,
    )
    from .modules.utils_general import get_date_time
    from .modules.utils_validations import validate_execution_mode
    from .modules.errors import report_error_end_of_switch
    from .decoder.decode_main import decode_json_to_graph
except ImportError:
    from modules import arguments as args
    from modules.content_identity import resolve_base_uri
    from modules.metadata import METADATA
    from modules.property_assignments import (
        apply_property_assignment_policy,
        collect_property_assignments,
    )
    from modules.input_output import (
        safe_load_json_file,
        create_directory_if_not_exists,
        safe_write_graph_file,
    )
    from modules.logger import initialize_logger
    from modules.transformation_metadata import (
        build_transformation_metadata,
        get_transformation_configuration,
        graph_with_metadata,
    )
    from modules.utils_general import get_date_time
    from modules.utils_validations import validate_execution_mode
    from modules.errors import report_error_end_of_switch
    from decoder.decode_main import decode_json_to_graph


class SharedBatchBaseURIWarning(UserWarning):
    """Warn that multiple batch outputs intentionally share one explicit namespace."""


def decode_ontouml_json2graph(
    json_file_path: str,
    base_uri: str | None = None,
    language: str = "",
    model_only: bool = False,
    silent: bool = True,
    correct: bool = False,
    execution_mode: str = "import",
    invalid_stereotype_policy: str = "preserve",
    invalid_cardinality_policy: str = "preserve",
    unresolved_model_element_policy: str = "omit",
    transformation_metadata: str = "none",
    append_content_hash: bool = False,
    path_order_policy: str = "warn",
    property_assignment_policy: str = "warn",
) -> Graph:
    """Convert OntoUML JSON data to a Knowledge Graph.

    This function takes the path to a JSON file representing OntoUML model data provided by the user
    and converts it into a knowledge graph following the specified options.

    :param json_file_path: Path to the JSON file to be decoded provided by the user.
    :type json_file_path: str
    :param base_uri: Optional explicit base URI for generated resources. When omitted, a deterministic urn:uuid base
                     is derived from the parsed JSON document. (Optional)
    :type base_uri: str or None
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
    :param invalid_stereotype_policy: How to handle stereotypes invalid for their element type. Valid values are
                                      'preserve', 'omit', and 'error'. Default is 'preserve'. (Optional)
    :type invalid_stereotype_policy: str
    :param invalid_cardinality_policy: How to handle invalid cardinalities. Valid values are 'preserve', 'repair',
                                       and 'error'. Default is 'preserve'. (Optional)
    :type invalid_cardinality_policy: str
    :param unresolved_model_element_policy: How to handle unresolved modelElement references. Valid values are
                                            'preserve', 'omit', and 'error'. Default is 'omit'. (Optional)
    :type unresolved_model_element_policy: str
    :param transformation_metadata: Optional transformation provenance. Valid values for library use are 'none'
                                    (default) and 'embedded'. Sidecar output is available in script mode. (Optional)
    :type transformation_metadata: str
    :param append_content_hash: If True, append the deterministic content UUID to the supplied base URI. (Optional)
    :type append_content_hash: bool
    :param path_order_policy: How to handle path-point order. Valid values are 'warn' (default) and 'comment'.
                              The latter adds a non-normative rdfs:comment annotation. (Optional)
    :type path_order_policy: str
    :param property_assignment_policy: How to handle non-empty propertyAssignments maps. Valid values are 'warn'
                                       (default) and 'comment'. The latter adds their canonical JSON as a
                                       non-normative rdfs:comment annotation. (Optional)
    :type property_assignment_policy: str

    :return: JSON data decoded into a RDFLib's Graph that is compliant with the OntoUML Vocabulary.
    :rtype: Graph
    """
    logger = initialize_logger(execution_mode)

    model_elements = [
        "Class",
        "Property",
        "Generalization",
        "GeneralizationSet",
        "Relation",
        "Literal",
        "Cardinality",
    ]

    validate_execution_mode(execution_mode)

    if execution_mode == "test":
        args.initialize_args_test(
            input_path=json_file_path,
            language=language,
            invalid_cardinality_policy=invalid_cardinality_policy,
            invalid_stereotype_policy=invalid_stereotype_policy,
            unresolved_model_element_policy=unresolved_model_element_policy,
            transformation_metadata=transformation_metadata,
            path_order_policy=path_order_policy,
            property_assignment_policy=property_assignment_policy,
        )
    elif execution_mode == "import":
        args.initialize_args_import(
            input_path=json_file_path,
            base_uri=base_uri,
            language=language,
            model_only=model_only,
            silent=silent,
            correct=correct,
            invalid_cardinality_policy=invalid_cardinality_policy,
            invalid_stereotype_policy=invalid_stereotype_policy,
            unresolved_model_element_policy=unresolved_model_element_policy,
            transformation_metadata=transformation_metadata,
            append_content_hash=append_content_hash,
            path_order_policy=path_order_policy,
            property_assignment_policy=property_assignment_policy,
        )

    if execution_mode == "script" and not args.ARGUMENTS["silent"]:
        # Initial time information
        time_screen_format = "%d-%m-%Y %H:%M:%S"
        start_date_time = get_date_time(time_screen_format)
        st = time.perf_counter()

        logger.info(f"{METADATA['Summary']} v{METADATA['Version']} started on {start_date_time}!")

        logger.info(
            f"Decoding JSON file {args.ARGUMENTS['input_path']} to {(args.ARGUMENTS['format']).upper()} graph "
            f"format.\n"
        )

        if not args.ARGUMENTS["language"]:
            logger.warning(
                "Ontology's language not informed by the user. Transformation will not generate language tag."
            )
        if not args.ARGUMENTS["correct"]:
            logger.warning(
                "Basic correction feature not enabled by the user. "
                "The transformation may generate an invalid result."
            )

    # Load JSON
    json_data = safe_load_json_file(json_file_path)
    property_assignment_records = collect_property_assignments(json_data)

    if execution_mode != "test":
        args.ARGUMENTS["base_uri"] = resolve_base_uri(
            json_data=json_data,
            base_uri=args.ARGUMENTS["base_uri_input"],
            append_content_hash=args.ARGUMENTS["append_content_hash"],
        )

    # Decode JSON into Graph
    ontouml_graph = decode_json_to_graph(json_data, language, execution_mode)

    # If set by user, remove all diagrammatic elements
    if args.ARGUMENTS["model_only"]:
        for s, _, o in ontouml_graph.triples((None, RDF.type, None)):
            s_type = s.toPython()
            o_type = o.fragment
            # Remove if not a model element and if it is defined by of the ontology being handled
            if (args.ARGUMENTS["base_uri"] in s_type) and (o_type not in model_elements):
                ontouml_graph.remove((s, None, None))
                ontouml_graph.remove((None, None, s))
        if not args.ARGUMENTS["silent"]:
            logger.info("All diagrammatic data removed from the output. The output contains only model elements.")

    apply_property_assignment_policy(
        records=property_assignment_records,
        ontouml_graph=ontouml_graph,
        policy=args.ARGUMENTS["property_assignment_policy"],
        input_path=args.ARGUMENTS["input_path"],
        base_uri=args.ARGUMENTS["base_uri"],
    )

    if execution_mode == "script" and not args.ARGUMENTS["silent"]:
        # Get software's execution conclusion time
        end_date_time = get_date_time(time_screen_format)
        et = time.perf_counter()
        elapsed_time = round((et - st), 3)
        logger.info(f"Decoding concluded on {end_date_time}. Total execution time: {elapsed_time} seconds.")

    if execution_mode != "script" and args.ARGUMENTS["transformation_metadata"] == "embedded":
        metadata_graph = build_transformation_metadata(
            ontouml_graph=ontouml_graph,
            input_file_path=json_file_path,
            output_file_name=f"{Path(json_file_path).stem} in-memory graph",
            graph_format="",
            configuration=get_transformation_configuration(args.ARGUMENTS, graph_format=None),
        )
        return graph_with_metadata(ontouml_graph, metadata_graph)

    return ontouml_graph


def write_graph_file(ontouml_graph: Graph, execution_mode: str = "script") -> str:
    """Save the ontology graph received as argument into a file using the syntax defined by the user.

    When running in script mode, the result is saved in the folder specified by the user as argument.
    When running in test mode, the file is saved inside the 'results' directory created by this function.

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

    transformation_metadata = args.ARGUMENTS["transformation_metadata"]
    output_graph = ontouml_graph
    metadata_graph = Graph()

    if transformation_metadata in ("embedded", "sidecar"):
        metadata_graph = build_transformation_metadata(
            ontouml_graph=ontouml_graph,
            input_file_path=args.ARGUMENTS["input_path"],
            output_file_name=output_file_name,
            graph_format=args.ARGUMENTS["format"],
            configuration=get_transformation_configuration(
                args.ARGUMENTS,
                graph_format=args.ARGUMENTS["format"],
            ),
        )

    if transformation_metadata == "embedded":
        output_graph = graph_with_metadata(ontouml_graph, metadata_graph)

    safe_write_graph_file(output_graph, output_file_path, args.ARGUMENTS["format"])

    if transformation_metadata == "sidecar":
        sidecar_file_path = str(Path(output_file_path).with_suffix(".provenance.ttl"))
        safe_write_graph_file(metadata_graph, sidecar_file_path, "ttl")
        if not args.ARGUMENTS["silent"]:
            logger.info(f"Transformation metadata sidecar successfully saved at {sidecar_file_path}.")

    if not args.ARGUMENTS["silent"]:
        logger.info(f"Output graph file successfully saved at {output_file_path}.\n")

    return output_file_path


def decode_all_ontouml_json2graph() -> None:
    """Decode multiple OntoUML JSON files in batch mode.

    This function processes a directory of OntoUML JSON files and converts each file into a corresponding
    knowledge graph using the specified options.
    The output graphs are saved in the output directory chosen by the user as argument.
    """
    # Getting all
    list_input_files = sorted(glob.glob(os.path.join(args.ARGUMENTS["input_path"], "*.json")))

    if (
        len(list_input_files) > 1
        and args.ARGUMENTS["base_uri_input"] is not None
        and not args.ARGUMENTS["append_content_hash"]
    ):
        warnings.warn(
            "All batch outputs will use the same explicit base URI. Their resources can collide if the graphs are "
            "combined. Use --base-uri-with-content-id to create a separate content-derived namespace for each "
            "distinct JSON document.",
            SharedBatchBaseURIWarning,
            stacklevel=2,
        )

    for input_file in list_input_files:
        args.ARGUMENTS["input_path"] = input_file
        result_graph = decode_ontouml_json2graph(json_file_path=input_file, execution_mode="script")
        write_graph_file(result_graph, execution_mode="script")


if __name__ == "__main__":
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
