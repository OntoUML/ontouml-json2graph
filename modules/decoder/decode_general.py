""" General decoding functions. """

from rdflib import Graph, URIRef, RDF, Literal

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.sparql_queries import GET_ELEMENT_AND_TYPE
from modules.utils_graph import load_all_graph_safely


def count_elements(ontouml_graph: Graph) -> dict:
    """ Returns a dictionary with all element types on graphs and their respective quantity.

    :param ontouml_graph: Knowledge graph with loaded objects' ids and types
    :type ontouml_graph: Graph
    :return: Dictionary with types and respective quantities present on graph.
    :rtype: dict
    """

    element_counting = {}

    ontouml_meta_graph = load_all_graph_safely("resources/ontouml.ttl")
    aggregated_graph = ontouml_meta_graph + ontouml_graph
    query_answer = aggregated_graph.query(GET_ELEMENT_AND_TYPE)

    for row in query_answer:
        element_type = row.inst_type.toPython().replace(URI_ONTOUML, "")

        if element_type in element_counting:
            element_counting[element_type] += 1
        else:
            element_counting[element_type] = 1

    return element_counting


def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a dictionary and decode every value to the OntoUML Graph.
    Recursively evaluate the dictionary to create all possible instances, setting their types and attributes.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

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


def clean_null_data(dictionary_data) -> dict:
    """ Removes all empty values (i.e., keys associated with None) from the received dictionary.
    If a value of the dictionary is another dictionary, this function recursively verify this sub-dictionary elements.
    I.e., all empty fields, from all dictionaries composing the main dictionary are also cleaned.

    :param dictionary_data: Dictionary to have its empty fields cleaned.
    :type dictionary_data: dict
    :return: Dictionary without empty fields.
    :rtype: dict
    """

    # Using list() to force a copy of the keys. Avoids "RuntimeError: dictionary changed size during iteration".
    for key in list(dictionary_data.keys()):

        # Recursively treats sub-dictionaries inside lists
        if type(dictionary_data[key]) is list:
            for item in dictionary_data[key]:
                clean_null_data(item)

        # Recursively treats sub-dictionaries
        if type(dictionary_data[key]) is dict:
            clean_null_data(dictionary_data[key])

        if dictionary_data[key] is None:
            dictionary_data.pop(key)

    return dictionary_data
