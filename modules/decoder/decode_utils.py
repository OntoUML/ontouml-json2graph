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


def get_list_subdictionaries_for_specific_type(dictionary_data: dict, wanted_type: str,
                                               return_list: list[dict] = None) -> list[dict]:
    """ Recursively access all objects in the dictionary until find an object of the desired type. When the id is found,
    add to a copy of its dictionaries to a list to be returned (containing all its sub-dictionaries).

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param wanted_type: ID of the object to have its dictionary (including sub-dictionaries) returned.
    :type wanted_type: str
    :param return_list: Optional. Searched dictionary to be returned. Used for recursion only.
    :type return_list: list[dict]
    :return: List of copy of the object's dictionaries.
    :rtype: list[dict]
    """

    if return_list is None:
        return_list = []

    # When found, add a copy of the dictionary to the return_list
    if dictionary_data["type"] == wanted_type:
        return_list.append(dictionary_data.copy())

    # If not found, recursively search for it
    for dict_field in dictionary_data.keys():

        # Treating dictionary fields
        if type(dictionary_data[dict_field]) is dict:
            return_list = get_list_subdictionaries_for_specific_type(dictionary_data[dict_field], wanted_type,
                                                                     return_list)

        # Treating list fields
        if type(dictionary_data[dict_field]) is list:
            for item in dictionary_data[dict_field]:
                return_list = get_list_subdictionaries_for_specific_type(item, wanted_type, return_list)

    return return_list


def get_subdictionary_for_specific_id(dictionary_data: dict, wanted_id: str, return_dict: dict = None) -> dict:
    """ Recursively access all objects in the dictionary until find the desired ID.
    When the id is found, return a copy of its dictionary (containing all its sub-dictionaries).

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param wanted_id: ID of the object to have its dictionary (including sub-dictionaries) returned.
    :type wanted_id: str
    :param return_dict: Optional. Searched dictionary to be returned. Used for recursion only.
    :type return_dict: dict
    :return: Copy of the object's dictionary.
    :rtype: dict
    """

    # If value is already found, return it and stop recursion.
    if return_dict is not None:
        return return_dict

    # When the value is not found, start search

    # If found, copy (end of recursion)
    if dictionary_data["id"] == wanted_id:
        return_dict = dictionary_data.copy()

    # If not found, recursively search for it
    for dict_field in dictionary_data.keys():

        # Treating dictionary fields
        if type(dictionary_data[dict_field]) is dict:
            return_dict = get_subdictionary_for_specific_id(dictionary_data[dict_field], wanted_id, return_dict)

        # Treating list fields
        if type(dictionary_data[dict_field]) is list:
            for item in dictionary_data[dict_field]:
                return_dict = get_subdictionary_for_specific_id(item, wanted_id, return_dict)

    return return_dict


def get_all_ids_of_specific_type(dictionary_data: dict, wanted_type: str, list_ids_for_type: list[str] = None) -> list[
    str]:
    """ Recursively access all objects in the dictionary and generates a list of all ids of objects for a given type.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param wanted_type: Name of the type of the objects to have their IDs identified.
    :type wanted_type: str
    :return: List of ids from all objects for a given type.
    :rtype: list[str]
    """

    if list_ids_for_type is None:
        list_ids_for_type = []

    # If found, add
    if dictionary_data["type"] == wanted_type:
        list_ids_for_type.append(dictionary_data["id"])

    # Continue searching
    for dict_field in dictionary_data.keys():

        # Treating dictionaries fields
        if type(dictionary_data[dict_field]) is dict:
            list_ids_for_type = get_all_ids_of_specific_type(dictionary_data[dict_field], wanted_type,
                                                             list_ids_for_type)

        # Treating list fields
        if type(dictionary_data[dict_field]) is list:
            for item in dictionary_data[dict_field]:
                list_ids_for_type = get_all_ids_of_specific_type(item, wanted_type, list_ids_for_type)

    # remove duplicates
    list_ids_for_type = list(dict.fromkeys(list_ids_for_type))

    return list_ids_for_type


def decode_dictionary(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Receives a dictionary and decode every known value to the OntoUML Graph.
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