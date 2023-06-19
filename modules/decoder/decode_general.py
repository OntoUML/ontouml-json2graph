""" General decoding functions. """

from rdflib import Graph, URIRef, RDF, Literal

from globals import ONTOLOGY_URI, ONTOUML_URI


def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a dictionary and decode every value to the OntoUML Graph.
    Recursively evaluate the dictionary to create all possible instances, setting their types and attributes.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Creating instance
    instance_uri = ONTOLOGY_URI + dictionary_data["id"]
    new_instance = URIRef(instance_uri)

    # Setting instance type
    instance_type = URIRef(ONTOUML_URI + dictionary_data["type"])
    ontouml_graph.add((new_instance, RDF.type, instance_type))

    # Adding other attributes
    for key in dictionary_data.keys():

        # id and type were already treated and are skipped
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

        new_predicate = URIRef(ONTOUML_URI + key)
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
