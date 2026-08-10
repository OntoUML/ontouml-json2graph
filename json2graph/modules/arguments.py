"""Argument Treatments Module.

This module provides functions for parsing and validating user-provided arguments when starting the software execution
as a script.

It also makes the ARGUMENTS variable globally accessible with the user's arguments (when executed as a script) or with
default values (when executed as test or as a library).
"""

import argparse
import os

from .errors import report_error_requirement_not_met
from .cardinalities import INVALID_CARDINALITY_POLICIES
from .input_output import create_directory_if_not_exists
from .logger import initialize_logger
from .metadata import METADATA
from .model_element_references import UNRESOLVED_MODEL_ELEMENT_POLICIES
from .path_order import PATH_ORDER_POLICIES
from .property_assignments import PROPERTY_ASSIGNMENT_POLICIES
from .stereotypes import INVALID_STEREOTYPE_POLICIES
from .transformation_metadata import TRANSFORMATION_METADATA_MODES
from .utils_validations import validate_arg_input

ARGUMENTS = {}

LOGGER = initialize_logger()


def initialize_args_script() -> None:
    """Parse the command-line arguments provided by the user and performs necessary validations.

    The ARGUMENTS variable must be initialized in every possible execution mode.
    """
    # Formats for saving graphs supported by RDFLib
    # https://rdflib.readthedocs.io/en/stable/intro_to_parsing.html#saving-rdf
    allowed_graph_formats = [
        "turtle",
        "ttl",
        "turtle2",
        "xml",
        "pretty-xml",
        "json-ld",
        "ntriples",
        "nt",
        "nt11",
        "n3",
        "trig",
        "trix",
        "nquads",
    ]

    # Parsing user's arguments

    # PARSING ARGUMENTS

    args_parser = argparse.ArgumentParser(
        prog=METADATA["Name"],
        description=METADATA["Summary"] + ". Version: " + METADATA["Version"],
        allow_abbrev=False,
        epilog="More information at: " + METADATA["Home-page"],
    )

    # Building -v argument information
    about_message = METADATA["Name"] + " - version " + METADATA["Version"]
    args_parser.version = about_message

    # This LOGGER.debug was inserted to prevent vulture from reporting false positive dead code
    LOGGER.debug(args_parser.version)

    # OPTIONAL ARGUMENTS
    args_parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        action="store",
        required=True,
        help="The path of the JSON file or directory with JSON files to be decoded.",
    )
    args_parser.add_argument(
        "-o",
        "--output_path",
        type=str,
        action="store",
        default=os.getcwd(),
        help="The path of the directory in which the resulting decoded file(s) will be saved. "
        "Default is the working directory.",
    )
    args_parser.add_argument(
        "-a",
        "--decode_all",
        action="store_true",
        help="Converts all JSON files in the informed path.",
    )
    args_parser.add_argument(
        "-f",
        "--format",
        type=str,
        action="store",
        choices=allowed_graph_formats,
        default="ttl",
        help="Format to save the decoded file. Default is 'ttl'.",
    )
    args_parser.add_argument(
        "-l",
        "--language",
        type=str,
        action="store",
        default="",
        help="Language tag for the ontology's concepts. Default is 'None'.",
    )
    args_parser.add_argument(
        "-c",
        "--correct",
        action="store_true",
        default=False,
        help="Enables syntactical and semantic validations and corrections.",
    )
    args_parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        default=False,
        help="Silent mode. Does not present validation warnings and errors.",
    )
    base_uri_group = args_parser.add_mutually_exclusive_group()
    base_uri_group.add_argument(
        "-u",
        "--base-uri",
        "--base_uri",
        type=str,
        action="store",
        default=None,
        help="Use this exact base URI for generated resources. By default, a deterministic urn:uuid base is derived "
        "from each JSON document.",
    )
    base_uri_group.add_argument(
        "--base-uri-with-content-id",
        type=str,
        action="store",
        default=None,
        help="Use this URI as a parent and append the document's deterministic content UUID.",
    )
    args_parser.add_argument(
        "-m",
        "--model_only",
        action="store_true",
        help="Keep only model elements, eliminating all diagrammatic data from output.",
    )
    args_parser.add_argument(
        "--invalid-cardinality-policy",
        type=str,
        action="store",
        choices=INVALID_CARDINALITY_POLICIES,
        default="preserve",
        help="Handle invalid cardinalities: preserve, repair known corpus patterns, or error. Default is 'preserve'.",
    )
    args_parser.add_argument(
        "--invalid-stereotype-policy",
        type=str,
        action="store",
        choices=INVALID_STEREOTYPE_POLICIES,
        default="preserve",
        help="Handle stereotypes invalid for their element type: preserve, omit, or error. Default is 'preserve'.",
    )
    args_parser.add_argument(
        "--unresolved-model-element-policy",
        type=str,
        action="store",
        choices=UNRESOLVED_MODEL_ELEMENT_POLICIES,
        default="omit",
        help="Handle unresolved modelElement references: preserve, omit, or error. Default is 'omit'.",
    )
    args_parser.add_argument(
        "--path-order-policy",
        type=str,
        action="store",
        choices=PATH_ORDER_POLICIES,
        default="warn",
        help="Handle path-point order: warn without representing it, or add a non-normative rdfs:comment. "
        "Default is 'warn'.",
    )
    args_parser.add_argument(
        "--property-assignment-policy",
        type=str,
        action="store",
        choices=PROPERTY_ASSIGNMENT_POLICIES,
        default="warn",
        help="Handle non-empty propertyAssignments maps: warn and omit them, or add canonical JSON in a "
        "non-normative rdfs:comment. Default is 'warn'.",
    )
    args_parser.add_argument(
        "--transformation-metadata",
        type=str,
        action="store",
        choices=TRANSFORMATION_METADATA_MODES,
        default="none",
        help="Transformation provenance: none, embedded in the output, or a separate Turtle sidecar. "
        "Default is 'none'.",
    )

    # AUTOMATIC ARGUMENTS
    args_parser.add_argument("-v", "--version", action="version", help="Print the software version and exit.")

    # Execute arguments parser
    arguments = args_parser.parse_args()

    # Asserting dictionary keys
    requested_base_uri = arguments.base_uri if arguments.base_uri is not None else arguments.base_uri_with_content_id
    append_content_hash = arguments.base_uri_with_content_id is not None
    arguments_dictionary = {
        "append_content_hash": append_content_hash,
        "base_uri": requested_base_uri,
        "base_uri_input": requested_base_uri,
        "correct": arguments.correct,
        "decode_all": arguments.decode_all,
        "format": arguments.format,
        "input_path": os.path.abspath(arguments.input_path),
        "invalid_cardinality_policy": arguments.invalid_cardinality_policy,
        "invalid_stereotype_policy": arguments.invalid_stereotype_policy,
        "language": arguments.language,
        "model_only": arguments.model_only,
        "output_path": os.path.abspath(arguments.output_path),
        "path_order_policy": arguments.path_order_policy,
        "property_assignment_policy": arguments.property_assignment_policy,
        "silent": arguments.silent,
        "transformation_metadata": arguments.transformation_metadata,
        "unresolved_model_element_policy": arguments.unresolved_model_element_policy,
    }

    # Input validation
    validate_arg_input(arguments.input_path, arguments.decode_all)

    # Output validation
    if os.path.isfile(arguments.output_path):
        report_error_requirement_not_met("Provided output path is not a directory. Execution finished.")
    if not os.path.exists(arguments.output_path):
        create_directory_if_not_exists(arguments.output_path, "output directory")
        LOGGER.info("The provided output directory did not exist and was created.")

    LOGGER.debug(f"Arguments parsed. Obtained values are: {arguments_dictionary}.")

    global ARGUMENTS
    ARGUMENTS = arguments_dictionary


def initialize_args_import(
    input_path: str = "not_initialized",
    output_path: str = os.getcwd(),
    base_uri: str | None = None,
    graph_format: str = "ttl",
    language: str = "",
    model_only: bool = False,
    silent: bool = True,
    correct: bool = False,
    invalid_stereotype_policy: str = "preserve",
    invalid_cardinality_policy: str = "preserve",
    unresolved_model_element_policy: str = "omit",
    transformation_metadata: str = "none",
    append_content_hash: bool = False,
    path_order_policy: str = "warn",
    property_assignment_policy: str = "warn",
):
    """Initialize the global variable ARGUMENTS of type dictionary, which contains user-provided \
    (when executed in script mode) or default arguments (when executed as a library or for testing).

    The ARGUMENTS variable must be initialized in every possible execution mode.

    :param input_path: Path to the directory or JSON file to be decoded. (Optional)
    :type input_path: str
    :param output_path: Path to the directory in which the result file(s) will be saved. (Optional)
    :type output_path: str
    :param base_uri: Optional explicit base URI for generated resources. When omitted, a deterministic urn:uuid base
                     is derived from the parsed JSON document. (Optional)
    :type base_uri: str or None
    :param graph_format: Format for saving the resulting knowledge graph. (Optional)
                         Default value is 'ttl' (Turtle syntax).
    :type graph_format: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param model_only: If True, only the OntoUML model will be extracted without diagrammatic information. (Optional)
    :type model_only: bool
    :param silent: If True, suppresses intermediate communications and log messages during execution. (Optional)
    :type silent: bool
    :param correct: If True, attempts to correct potential errors during the conversion process. (Optional)
    :type correct: bool
    :param invalid_stereotype_policy: How to handle stereotypes invalid for their element type. Valid values are
                                      'preserve', 'omit', and 'error'. (Optional)
    :type invalid_stereotype_policy: str
    :param invalid_cardinality_policy: How to handle invalid cardinalities. Valid values are 'preserve', 'repair',
                                       and 'error'. (Optional)
    :type invalid_cardinality_policy: str
    :param unresolved_model_element_policy: How to handle unresolved modelElement references. Valid values are
                                            'preserve', 'omit', and 'error'. (Optional)
    :type unresolved_model_element_policy: str
    :param transformation_metadata: How transformation provenance is returned. Library decoding supports 'none' and
                                    'embedded'; sidecar output is available in script mode. (Optional)
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
    """
    validate_arg_input(input_path, decode_all=False)

    if invalid_cardinality_policy not in INVALID_CARDINALITY_POLICIES:
        report_error_requirement_not_met(
            f"Invalid cardinality policy '{invalid_cardinality_policy}'. Valid values are: "
            f"{list(INVALID_CARDINALITY_POLICIES)}."
        )

    if invalid_stereotype_policy not in INVALID_STEREOTYPE_POLICIES:
        report_error_requirement_not_met(
            f"Invalid stereotype policy '{invalid_stereotype_policy}'. Valid values are: "
            f"{list(INVALID_STEREOTYPE_POLICIES)}."
        )

    if unresolved_model_element_policy not in UNRESOLVED_MODEL_ELEMENT_POLICIES:
        report_error_requirement_not_met(
            f"Invalid unresolved modelElement policy '{unresolved_model_element_policy}'. Valid values are: "
            f"{list(UNRESOLVED_MODEL_ELEMENT_POLICIES)}."
        )

    if path_order_policy not in PATH_ORDER_POLICIES:
        report_error_requirement_not_met(
            f"Invalid path order policy '{path_order_policy}'. Valid values are: {list(PATH_ORDER_POLICIES)}."
        )

    if property_assignment_policy not in PROPERTY_ASSIGNMENT_POLICIES:
        report_error_requirement_not_met(
            f"Invalid property assignment policy '{property_assignment_policy}'. Valid values are: "
            f"{list(PROPERTY_ASSIGNMENT_POLICIES)}."
        )

    if transformation_metadata not in TRANSFORMATION_METADATA_MODES:
        report_error_requirement_not_met(
            f"Invalid transformation metadata mode '{transformation_metadata}'. Valid values are: "
            f"{list(TRANSFORMATION_METADATA_MODES)}."
        )
    if transformation_metadata == "sidecar":
        report_error_requirement_not_met(
            "Sidecar transformation metadata requires file output and is only available in script mode."
        )

    ARGUMENTS["append_content_hash"] = append_content_hash
    ARGUMENTS["base_uri"] = base_uri
    ARGUMENTS["base_uri_input"] = base_uri
    ARGUMENTS["correct"] = correct
    ARGUMENTS["format"] = graph_format
    ARGUMENTS["input_path"] = input_path
    ARGUMENTS["invalid_cardinality_policy"] = invalid_cardinality_policy
    ARGUMENTS["invalid_stereotype_policy"] = invalid_stereotype_policy
    ARGUMENTS["language"] = language
    ARGUMENTS["model_only"] = model_only
    ARGUMENTS["output_path"] = output_path
    ARGUMENTS["path_order_policy"] = path_order_policy
    ARGUMENTS["property_assignment_policy"] = property_assignment_policy
    ARGUMENTS["silent"] = silent
    ARGUMENTS["transformation_metadata"] = transformation_metadata
    ARGUMENTS["unresolved_model_element_policy"] = unresolved_model_element_policy


def initialize_args_test(
    input_path: str = "not_initialized",
    language: str = "",
    invalid_stereotype_policy: str = "preserve",
    invalid_cardinality_policy: str = "preserve",
    unresolved_model_element_policy: str = "omit",
    transformation_metadata: str = "none",
    path_order_policy: str = "warn",
    property_assignment_policy: str = "warn",
):
    """Initialize the global variable ARGUMENTS of type dictionary, which contains user-provided \
    (when executed in script mode) or default arguments (when executed as a library or for testing).

    The ARGUMENTS variable must be initialized in every possible execution mode.

    :param input_path: Path to the directory or JSON file to be decoded. (Optional)
    :type input_path: str
    :param language: Language tag to be added to the ontology's concepts. (Optional)
    :type language: str
    :param invalid_stereotype_policy: How to handle stereotypes invalid for their element type. (Optional)
    :type invalid_stereotype_policy: str
    :param invalid_cardinality_policy: How to handle invalid cardinalities. (Optional)
    :type invalid_cardinality_policy: str
    :param unresolved_model_element_policy: How to handle unresolved modelElement references. (Optional)
    :type unresolved_model_element_policy: str
    :param transformation_metadata: How transformation provenance is returned. (Optional)
    :type transformation_metadata: str
    :param path_order_policy: How to handle path-point order. Valid values are 'warn' and 'comment'. (Optional)
    :type path_order_policy: str
    :param property_assignment_policy: How to handle non-empty propertyAssignments maps. Valid values are 'warn' and
                                       'comment'. (Optional)
    :type property_assignment_policy: str
    """
    validate_arg_input(input_path, decode_all=False)

    if invalid_cardinality_policy not in INVALID_CARDINALITY_POLICIES:
        report_error_requirement_not_met(
            f"Invalid cardinality policy '{invalid_cardinality_policy}'. Valid values are: "
            f"{list(INVALID_CARDINALITY_POLICIES)}."
        )

    if invalid_stereotype_policy not in INVALID_STEREOTYPE_POLICIES:
        report_error_requirement_not_met(
            f"Invalid stereotype policy '{invalid_stereotype_policy}'. Valid values are: "
            f"{list(INVALID_STEREOTYPE_POLICIES)}."
        )

    if unresolved_model_element_policy not in UNRESOLVED_MODEL_ELEMENT_POLICIES:
        report_error_requirement_not_met(
            f"Invalid unresolved modelElement policy '{unresolved_model_element_policy}'. Valid values are: "
            f"{list(UNRESOLVED_MODEL_ELEMENT_POLICIES)}."
        )

    if path_order_policy not in PATH_ORDER_POLICIES:
        report_error_requirement_not_met(
            f"Invalid path order policy '{path_order_policy}'. Valid values are: {list(PATH_ORDER_POLICIES)}."
        )

    if property_assignment_policy not in PROPERTY_ASSIGNMENT_POLICIES:
        report_error_requirement_not_met(
            f"Invalid property assignment policy '{property_assignment_policy}'. Valid values are: "
            f"{list(PROPERTY_ASSIGNMENT_POLICIES)}."
        )

    if transformation_metadata not in TRANSFORMATION_METADATA_MODES:
        report_error_requirement_not_met(
            f"Invalid transformation metadata mode '{transformation_metadata}'. Valid values are: "
            f"{list(TRANSFORMATION_METADATA_MODES)}."
        )

    ARGUMENTS["append_content_hash"] = False
    ARGUMENTS["base_uri"] = "https://example.org#"
    ARGUMENTS["base_uri_input"] = "https://example.org#"
    ARGUMENTS["correct"] = True
    ARGUMENTS["format"] = "ttl"
    ARGUMENTS["input_path"] = input_path
    ARGUMENTS["invalid_cardinality_policy"] = invalid_cardinality_policy
    ARGUMENTS["invalid_stereotype_policy"] = invalid_stereotype_policy
    ARGUMENTS["language"] = language
    ARGUMENTS["model_only"] = False
    ARGUMENTS["output_path"] = "tests" + os.path.sep + "results"
    ARGUMENTS["path_order_policy"] = path_order_policy
    ARGUMENTS["property_assignment_policy"] = property_assignment_policy
    ARGUMENTS["silent"] = True
    ARGUMENTS["transformation_metadata"] = transformation_metadata
    ARGUMENTS["unresolved_model_element_policy"] = unresolved_model_element_policy
