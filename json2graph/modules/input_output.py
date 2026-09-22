"""IO functions used in diverse occasions."""

import json
import os
import warnings

from rdflib import Graph, Literal, URIRef
from rdflib.plugins.serializers.turtle import TurtleSerializer

from .errors import report_error_io_read, report_error_io_write
from .logger import initialize_logger
from .utils_graph import rename_uriref_resource, fix_uri

LOGGER = initialize_logger()
_TURTLE_SYNTAXES = {"ttl", "turtle", "turtle2"}


class JSONEncodingFallbackWarning(UserWarning):
    """Warn that a JSON input required a fallback character encoding."""


class _WhitespaceSafeTurtleSerializer(TurtleSerializer):
    """Serialize multiline literals without physical line breaks in their lexical form."""

    @staticmethod
    def _escaped_multiline_literal(literal: Literal) -> str:
        """Return Turtle syntax preserving a multiline literal's exact lexical value."""
        encoded = str(literal).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        quoted = f'"{encoded}"'

        if literal.language:
            return f"{quoted}@{literal.language}"

        if literal.datatype:
            return f"{quoted}^^<{literal.datatype}>"

        return quoted

    def label(self, node, position: int) -> str:
        """Return a Turtle label, escaping physical newlines in multiline literals."""
        if isinstance(node, Literal) and ("\n" in node or "\r" in node):
            return self._escaped_multiline_literal(node)

        return super().label(node, position)


def create_directory_if_not_exists(directory_path: str, file_description: str) -> None:
    """Check if the directory that has the path received as argument exists. \
    If it does, do nothing. If it does not, create it.

    :param directory_path: Path to the directory to be created (if it does not exist).
    :type directory_path: str
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
    except OSError as error:
        if file_description is None:
            file_description = "directory"
        report_error_io_write(directory_path, file_description, error)


def safe_load_json_file(json_path: str) -> dict:
    """Safely loads the JSON file inputted by the user as an argument into a dictionary.

    :param json_path: Path to the JSON file to be loaded.
    :type json_path: str
    :return: Dictionary with loaded JSON's data.
    :rtype: dict
    """
    try:
        with open(json_path, "r", encoding="utf-8") as read_file:
            json_data = json.load(read_file)
    except UnicodeDecodeError:
        try:
            with open(json_path, "r", encoding="cp1252") as read_file:
                json_data = json.load(read_file)
        except OSError as error:
            file_description = "input json file"
            report_error_io_read(json_path, file_description, error)

        warnings.warn(
            f"JSON file {json_path} is not valid UTF-8; loaded using CP1252.",
            JSONEncodingFallbackWarning,
            stacklevel=2,
        )
    except IOError as error:
        file_description = "input json file"
        report_error_io_read(json_path, file_description, error)

    LOGGER.debug(f"JSON file {json_path} successfully loaded to dictionary.")

    return json_data


def _serialize_graph(ontouml_graph: Graph, output_file_path: str, syntax: str) -> None:
    """Serialize a graph, using whitespace-safe Turtle output for Turtle syntaxes."""
    if syntax in _TURTLE_SYNTAXES:
        with open(output_file_path, "wb") as output_stream:
            serializer = _WhitespaceSafeTurtleSerializer(ontouml_graph)
            serializer.serialize(
                output_stream,
                encoding="utf-8",
                spacious=(syntax == "turtle2"),
            )
        return

    ontouml_graph.serialize(destination=output_file_path, encoding="utf-8", format=syntax)


def safe_write_graph_file(ontouml_graph: Graph, output_file_path: str, syntax: str) -> None:
    """Safely saves the graph into a file in the informed destination with the desired syntax.

    :param ontouml_graph: Graph compliant with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param output_file_path: Complete path of the output file to be created (including name and extension).
    :type output_file_path: str
    :param syntax: Syntax to be used for saving the ontology file.
    :type syntax: str
    """
    # Regular case (all URIRef resources have valid URIs)
    try:
        _serialize_graph(ontouml_graph, output_file_path, syntax)
    except Exception:
        # Special treatment for the cases where the graph has URIRef resources that are not valid URIs
        try:
            for old_s, old_p, old_o in ontouml_graph:
                if "URIRef" in str(type(old_s)):
                    old_s_name = old_s.toPython()
                    new_s = URIRef(fix_uri(old_s_name))
                    new_s_name = new_s.toPython()
                    if old_s_name != new_s_name:
                        rename_uriref_resource(ontouml_graph, old_s, new_s)
                if "URIRef" in str(type(old_p)):
                    old_p_name = old_p.toPython()
                    new_p = URIRef(fix_uri(old_p_name))
                    new_p_name = new_p.toPython()
                    if old_p_name != new_p_name:
                        rename_uriref_resource(ontouml_graph, old_p, new_p)
                if "URIRef" in str(type(old_o)):
                    old_o_name = old_o.toPython()
                    new_o = URIRef(fix_uri(old_o_name))
                    new_o_name = new_o.toPython()
                    if old_o_name != new_o_name:
                        rename_uriref_resource(ontouml_graph, old_o, new_o)
            _serialize_graph(ontouml_graph, output_file_path, syntax)
        except OSError as errorOS:
            file_description = "output graph file"
            report_error_io_write(output_file_path, file_description, errorOS)
