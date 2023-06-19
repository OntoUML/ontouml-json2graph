""" Functions to decode specificities of the object Project. """
from rdflib import Graph


def set_package_containsmodelelement_property(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Set object property ontouml:containsModelElement between a Package and its containing ModelElements.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Get ids of all objects Package
    list_package_ids = get_


    # For each object, get the list inside the 'contents' key and filter all ids there available.
    # Set containsModelElement relation between the Project object id and these ids.

    pass


def create_package_properties(dictionary_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Package.
    It only calls other specific functions for setting the object's specific properties.

    :param dictionary_data: Dictionary to have its fields decoded.
    :type dictionary_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    set_package_containsmodelelement_property(dictionary_data, ontouml_graph)
