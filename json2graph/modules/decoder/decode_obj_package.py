""" Functions to decode specificities of the object Package.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
    - Functions that set default values: set_<subject>_defaults.
"""

from rdflib import Graph, URIRef

import modules.arguments as args
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.utils_graph import ontouml_ref


def get_package_contents(package_dict: dict, package_id: str, list_contents: list = []) -> list[dict]:
    """ Receives the dictionary with all loaded JSON data and returns the value of the 'contents' field for a given
    object (defined by the received value of its ID).

    :param package_dict: Package's data to have its fields decoded.
    :type package_dict: dict
    :param package_id: ID of the Package to have its list of contents returned.
    :type package_id: str
    :param list_contents: Optional. Used to identify if the desired value was already found and exit recursion.
    :type list_contents: list
    :return: List of contents for a given Package.
    :rtype: list[dict]
    """

    # End of recursion
    if package_dict["id"] == package_id:
        if "contents" in package_dict:
            list_contents = package_dict["contents"].copy()
        else:
            list_contents = []

    # Recursively treats sub-dictionaries
    else:

        if list_contents:
            return list_contents

        for key in package_dict.keys():

            # Treat case dictionary
            if type(package_dict[key]) is dict:
                list_contents = get_package_contents(package_dict[key], package_id)

            # Treat case list
            elif type(package_dict[key]) is list:
                for item in package_dict[key]:
                    if type(item) is dict:
                        list_contents = get_package_contents(item, package_id, list_contents)

                    if list_contents:
                        break

    return list_contents


def set_package_containsmodelelement_modelelement(package_dict: dict, ontouml_graph: Graph) -> None:
    """ Set object property ontouml:containsModelElement between an ontouml:Package and an ontouml:ModelElement it
    contains.

    :param package_dict: Package's data to have its fields decoded.
    :type package_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Get the list inside the 'contents' key
    package_id_contents_list = get_package_contents(package_dict, package_dict["id"])

    # Treat only non-empy cases
    if package_id_contents_list:

        # Create a list of all ids inside the returned list
        list_related_ids = []
        for content in package_id_contents_list:
            list_related_ids.append(content["id"])

        # Include found related elements in graph using ontouml:containsModelElement
        for related_id in list_related_ids:
            ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + package_dict["id"]),
                               ontouml_ref("containsModelElement"),
                               URIRef(args.ARGUMENTS["base_uri"] + related_id)))


def create_package_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Package.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created object properties:
        - ontouml:containsModelElement (range:ModelElement)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Getting all Project dictionaries
    packages_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Package")

    for package_dict in packages_dicts_list:
        set_package_containsmodelelement_modelelement(package_dict, ontouml_graph)
