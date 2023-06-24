""" JSON decode functions. """

from rdflib import Graph, URIRef, Literal, RDF

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_obj_diagram import create_diagram_properties
from modules.decoder.decode_obj_package import create_package_properties
from modules.decoder.decode_obj_project import create_project_properties
from modules.decoder.decode_obj_rectangle import create_rectangle_properties
from modules.decoder.decode_utils import clean_null_data, count_elements


def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a dictionary and decode every known value to the OntoUML Graph.
    Recursively evaluate the dictionary to create all possible instances, setting their types and attributes.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    restricted_fields = ["x", "y"]

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
                decode_dictionary(item, ontouml_graph)
            continue

        # Recursively treats sub-dictionaries
        if type(dictionary_data[key]) is dict:
            decode_dictionary(dictionary_data[key], ontouml_graph)
            continue

        new_predicate = URIRef(URI_ONTOUML + key)
        new_object = Literal(dictionary_data[key])
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
    element_counting = count_elements(ontouml_graph)

    # TREAT: Class, ClassView, Rectangle

    # SPECIFIC DECODING: create specific properties according to different object types
    if "Project" in element_counting:
        create_project_properties(dictionary_data, ontouml_graph, element_counting)
    if "Package" in element_counting:
        create_package_properties(dictionary_data, ontouml_graph)
    if "Diagram" in element_counting:
        create_diagram_properties(dictionary_data, ontouml_graph)
    if "Rectangle" in element_counting:
        create_rectangle_properties(dictionary_data, ontouml_graph)

    return ontouml_graph
