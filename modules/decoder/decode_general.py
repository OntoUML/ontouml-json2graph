from rdflib import Graph, URIRef, RDF, Literal

from globals import USER_BASE_URI, ONTOUML_URI


def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a dictionary and decode every value that is not a dictionary to the OntoUML Graph.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Creating instance
    instance_uri = USER_BASE_URI + dictionary_data["id"]
    new_instance = URIRef(instance_uri)

    # Setting instance type
    instance_type = URIRef(ONTOUML_URI + dictionary_data["type"])
    ontouml_graph.add((new_instance, RDF.type, instance_type))

    # Adding other attributes
    for key in list(dictionary_data.keys()):

        # Values that are dictionaries are not treated
        if type(dictionary_data[key]) is dict:
            continue

        # id and type were already treated and are skipped
        if key == "id" or key == "type":
            continue

        new_attribute_type = URIRef(ONTOUML_URI + key)
        new_attribute_value = Literal(dictionary_data[key])
        ontouml_graph.add((new_instance, new_attribute_type, new_attribute_value))


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
        if type(dictionary_data[key]) is dict:
            clean_null_data(dictionary_data[key])

        if dictionary_data[key] is None:
            dictionary_data.pop(key)

    return dictionary_data
