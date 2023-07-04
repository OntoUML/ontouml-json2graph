""" JSON decode functions."""

from rdflib import Graph, URIRef, Literal, RDF, XSD

from globals import URI_ONTOUML, URI_ONTOLOGY, ELEMENT_VIEW_TYPES
from modules.decoder.decode_general import clean_null_data, count_elements_graph
from modules.decoder.decode_obj_class import create_class_properties
from modules.decoder.decode_obj_elementview import create_elementview_properties
from modules.decoder.decode_obj_diagram import create_diagram_properties
from modules.decoder.decode_obj_package import create_package_properties
from modules.decoder.decode_obj_project import create_project_properties
from modules.decoder.decode_obj_rectangularshape import create_rectangularshape_properties
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a dictionary and decode every known value to the OntoUML Graph.
    Recursively evaluate the dictionary to create all possible instances, setting their types and attributes.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    restricted_fields = ["x", "y", "stereotype", "order", "isExtensional", "isPowertype"]
    positive_integer_fields = ["width", "height"]

    # Creating instance
    instance_uri = URI_ONTOLOGY + dictionary_data["id"]
    new_instance = URIRef(instance_uri)

    # Setting instance type
    instance_type = URIRef(URI_ONTOUML + dictionary_data["type"])
    ontouml_graph.add((new_instance, RDF.type, instance_type))

    # Adding other attributes
    for key in dictionary_data.keys():

        # if id or type was already treated, skip
        if key == "id" or key == "type":
            continue

        # If it is of a restricted field, do not add other attributes now
        if key in restricted_fields:
            continue

        # Recursively treats sub-dictionaries inside lists
        if type(dictionary_data[key]) is list:
            for item in dictionary_data[key]:
                if type(item) is dict:
                    decode_dictionary(item, ontouml_graph)
            continue

        # Recursively treats sub-dictionaries
        if type(dictionary_data[key]) is dict:
            decode_dictionary(dictionary_data[key], ontouml_graph)
            continue

        # Graph's PREDICATE definition
        new_predicate = URIRef(URI_ONTOUML + key)

        # Graph's OBJECT definition
        if key in positive_integer_fields:
            # Checking if is not integer (as int or as string)
            if type(dictionary_data[key]) is not int:
                if not dictionary_data[key].isdigit():
                    LOGGER.warning(f"The object with ID {dictionary_data['id']} has an invalid type for its "
                                   f"field '{key}' and was not transformed (expected type 'int', "
                                   f"received '{type(dictionary_data[key]).__name__}').")
            else:
                new_object = Literal(dictionary_data[key], datatype=XSD.positiveInteger)
        else:
            new_object = Literal(dictionary_data[key])

        # Adding to graph
        ontouml_graph.add((new_instance, new_predicate, new_object))


def decode_json_to_graph(json_data: dict) -> Graph:
    """ Receives the loaded JSON data and decodes it into a graph that complies to the OntoUML Vocabulary.

    :param json_data: Input JSON data loaded as a dictionary.
    :type json_data: dict
    :return: Knowledge graph that complies with the OntoUML Vocabulary
    :rtype: Graph
    """

    # Creating OntoUML Graph
    ontouml_graph = Graph()
    ontouml_graph.bind("ontouml", URI_ONTOUML)
    ontouml_graph.bind("", URI_ONTOLOGY)

    # Get clean data
    # Dictionary data is all the JSON data loaded as a dictionary to be manipulated
    dictionary_data = clean_null_data(json_data)

    # GENERAL DECODING: creating all instances and setting their types.
    decode_dictionary(dictionary_data, ontouml_graph)

    # Counting elements for performance enhancement
    element_counting = count_elements_graph(ontouml_graph)

    # SPECIFIC DECODING: create specific properties according to different object types
    if "Project" in element_counting:
        create_project_properties(dictionary_data, ontouml_graph, element_counting)
    if "Package" in element_counting:
        create_package_properties(dictionary_data, ontouml_graph)
    if "Diagram" in element_counting:
        create_diagram_properties(dictionary_data, ontouml_graph, element_counting)
    if "Class" in element_counting:
        create_class_properties(dictionary_data, ontouml_graph)
    if ("Rectangle" in element_counting) or ("Text" in element_counting):
        create_rectangularshape_properties(dictionary_data, ontouml_graph)
    if set(ELEMENT_VIEW_TYPES).intersection(element_counting.keys()):
        create_elementview_properties(dictionary_data, ontouml_graph)

    return ontouml_graph
