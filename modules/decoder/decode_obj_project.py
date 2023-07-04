""" Functions to decode specificities of the object Project. """

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_general import get_all_ids_of_specific_type, get_list_subdictionaries_for_specific_type


def set_project_project(project_dict: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Sets the ontouml:project object property between a ontouml:Project (obj) and all its related entities (subj).

    :param project_dict: Project's data to have its fields decoded.
    :type project_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # The list of available types can be found in the element_counting dictionary.
    for available_type in element_counting.keys():

        # Projects do not have project properties with other projects
        if available_type == "Project":
            continue

        # Get every project's related objects' ids
        list_objects_ids = get_all_ids_of_specific_type(project_dict, available_type)

        for json_object_id in list_objects_ids:
            statement_subject = URIRef(URI_ONTOLOGY + json_object_id)
            statement_predicate = URIRef(URI_ONTOUML + "project")
            statement_object = URIRef(URI_ONTOLOGY + project_dict["id"])
            ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_model(project_data: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:model relation between an ontouml:Project and its related model.

    :param project_data: Project's data to have its fields decoded.
    :type project_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    if "model" in project_data:
        statement_subject = URIRef(URI_ONTOLOGY + project_data["id"])
        statement_predicate = URIRef(URI_ONTOUML + "model")
        statement_object = URIRef(URI_ONTOLOGY + project_data["model"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_diagram(project_dictionary: dict, ontouml_graph: Graph) -> bool:
    """ Sets the ontouml:diagram object property between a ontouml:Project and its related ontouml:Diagram entities.

    :param project_dictionary: Project's data to have its fields decoded.
    :type project_dictionary: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :return: Indication of if there are Diagrams still to be treated.
    :rtype: bool
    """

    # Getting all Diagrams for a specific Project
    list_all_diagram_ids = get_all_ids_of_specific_type(project_dictionary, "Diagram")

    for diagram_id in list_all_diagram_ids:
        statement_subject = URIRef(URI_ONTOLOGY + project_dictionary["id"])
        statement_predicate = URIRef(URI_ONTOUML + "diagram")
        statement_object = URIRef(URI_ONTOLOGY + diagram_id)
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Informs if there are Diagrams still to be treated
    if len(list_all_diagram_ids):
        return True
    else:
        return False


def create_project_properties(json_data: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Main function for decoding objects of type 'Project'.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is range or domain of.

    This function considers that there may be multiple projects in the loaded JSON file.

    Created object properties:
        - ontouml:model (range:Package)
        - ontouml:project (domain:OntoumlElement, range:Project)
        - ontouml:diagram (range:diagram)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # Used for performance improvement
    if "Diagram" in element_counting:
        num_diagrams = element_counting["Diagram"]
    else:
        num_diagrams = 0

    # Getting all Project dictionaries
    projects_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Project")

    for project_dict in projects_dicts_list:

        set_project_project(project_dict, ontouml_graph, element_counting)
        set_project_model(project_dict, ontouml_graph)

        # Treats relations between Projects and Diagrams only while there are Diagrams still untreated
        if num_diagrams > 0:
            property_set = set_project_diagram(project_dict, ontouml_graph)
            if property_set:
                num_diagrams -= 1
