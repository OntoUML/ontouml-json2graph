""" Functions to decode specificities of the object Project. """

from rdflib import Graph, URIRef

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.utils_graph import get_all_ids_for_type


# TODO (@pedropaulofb): Verify possible use of get_list_subdictionaries_for_specific_type as in Diagram.

def get_package_contents(dictionary_data: dict, package_id: str, list_contents: list = []) -> list[dict]:
    """ Receives the dictionary with all loaded JSON data and returns the value of the 'contents' field for a given
    object (defined by the received value of its ID).

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param package_id: ID of the Package to have its list of contents returned.
    :type package_id: str
    :param list_contents: Optional. Used to identify if the desired value was already found and exit recursion.
    :type list_contents: list
    :return: List of contents for a given Package.
    :rtype: list[dict]
    """

    # End of recursion
    if dictionary_data["id"] == package_id:
        if "contents" in dictionary_data:
            list_contents = dictionary_data["contents"].copy()
        else:
            list_contents = []

    # Recursively treats sub-dictionaries
    else:

        if list_contents:
            return list_contents

        for key in dictionary_data.keys():

            # Treat case dictionary
            if type(dictionary_data[key]) is dict:
                list_contents = get_package_contents(dictionary_data[key], package_id)

            # Treat case list
            elif type(dictionary_data[key]) is list:
                for item in dictionary_data[key]:
                    if type(item) is dict:
                        list_contents = get_package_contents(item, package_id, list_contents)

                    if list_contents:
                        break

    return list_contents


def set_package_containsmodelelement_property(package_id: str, dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Set object property ontouml:containsModelElement between a Package and its containing ModelElements.

    :param package_id: ID of the package being treated.
    :type package_id: str
    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get the list inside the 'contents' key
    package_id_contents_list = get_package_contents(dictionary_data, package_id)

    # Treat only non-empy cases
    if package_id_contents_list:

        # Create a list of all ids inside the returned list
        list_related_ids = []
        for content in package_id_contents_list:
            list_related_ids.append(content["id"])

        # Include found related elements in graph using ontouml:containsModelElement
        for related_id in list_related_ids:
            ontouml_graph.add((URIRef(URI_ONTOLOGY + package_id),
                               URIRef(URI_ONTOUML + "containsModelElement"),
                               URIRef(URI_ONTOLOGY + related_id)))


def create_package_properties(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Package.
    It only calls other specific functions for setting the object's specific properties.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get ids of all objects of type Package
    list_package_ids = get_all_ids_for_type(ontouml_graph, "Package")

    # For each Package (known ids):
    for package_id in list_package_ids:
        set_package_containsmodelelement_property(package_id, dictionary_data, ontouml_graph)
