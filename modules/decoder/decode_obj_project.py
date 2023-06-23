""" Functions to decode specificities of the object Project. """

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_utils import get_all_ids_of_specific_type, get_subdictionary_for_specific_id


def set_project_project_properties(project_id: str, project_data: dict, ontouml_graph: Graph,
                                   element_counting: dict) -> None:
    """ Sets the ontouml:project object property between a ontouml:Project (obj) and all its related entities (subj).

    :param project_id: ID of the Project being treated.
    :type project_id: str
    :param project_data: Project's data to have its fields decoded.
    :type project_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
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
        list_objects_ids = get_all_ids_of_specific_type(project_data, available_type)

        for json_object_id in list_objects_ids:
            statement_subject = URIRef(URI_ONTOLOGY + json_object_id)
            statement_predicate = URIRef(URI_ONTOUML + "project")
            statement_object = URIRef(URI_ONTOLOGY + project_id)
            ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_model_property(project_id: str, project_data: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:model relation between an ontouml:Project and its related model.

    :param project_id: ID of the Project being treated.
    :type project_id: str
    :param project_data: Project's data to have its fields decoded.
    :type project_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    if "model" in project_data:
        statement_subject = URIRef(URI_ONTOLOGY + project_id)
        statement_predicate = URIRef(URI_ONTOUML + "model")
        statement_object = URIRef(URI_ONTOLOGY + project_data["model"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_diagrams_properties(project_id: str, project_dictionary: dict, ontouml_graph: Graph) -> None:
    """ Sets the ontouml:diagram object property between a ontouml:Project and its related ontouml:Diagram entities.

    :param project_id: ID of the Project being treated.
    :type project_id: str
    :param project_dictionary: Project's data to have its fields decoded.
    :type project_dictionary: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    """

    # Getting all Diagrams for a specific Project
    list_all_diagram_ids = get_all_ids_of_specific_type(project_dictionary, "Diagram")

    for diagram_id in list_all_diagram_ids:
        statement_subject = URIRef(URI_ONTOLOGY + project_id)
        statement_predicate = URIRef(URI_ONTOUML + "diagram")
        statement_object = URIRef(URI_ONTOLOGY + diagram_id)
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def create_project_properties(json_data: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Main function for decoding every object of type Project.
    This function considers that there may be multiple projects in the loaded JSON file.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # Get all Projects' IDs
    list_all_project_ids = get_all_ids_of_specific_type(json_data, "Project")

    # For each Project, get all its related Diagrams and set the respective relation in the graph
    for project_id in list_all_project_ids:

        # Getting specific Project's dictionary
        project_dictionary = get_subdictionary_for_specific_id(json_data, project_id)

        set_project_project_properties(project_id, project_dictionary, ontouml_graph, element_counting)
        set_project_model_property(project_id, project_dictionary, ontouml_graph)

        if "Diagram" in element_counting:
            set_project_diagrams_properties(project_id, project_dictionary, ontouml_graph)
