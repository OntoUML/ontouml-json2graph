""" Functions to decode objects of type Project.
Functions to set object properties are named according to the nomenclature: set_<subject>_<predicate>_<object>.
"""

from rdflib import Graph, URIRef

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_general import get_all_ids_of_specific_type, get_list_subdictionaries_for_specific_type


def set_ontoumlelement_project_project(project_dict: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Sets the ontouml:project object property between an ontouml:Project (obj) and all its related entities (subj).

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


def set_project_model_package(project_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:model relation between an ontouml:Project and its related model.

    :param project_dict: Project's data to have its fields decoded.
    :type project_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    if "model" in project_dict:
        statement_subject = URIRef(URI_ONTOLOGY + project_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "model")
        statement_object = URIRef(URI_ONTOLOGY + project_dict["model"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_project_diagram_diagram(project_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the ontouml:diagram object property between a ontouml:Project and its related ontouml:Diagram entities.

    :param project_dict: Project's data to have its fields decoded.
    :type project_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Getting all Diagrams for a specific Project
    list_all_diagram_ids = get_all_ids_of_specific_type(project_dict, "Diagram")

    for diagram_id in list_all_diagram_ids:
        statement_subject = URIRef(URI_ONTOLOGY + project_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "diagram")
        statement_object = URIRef(URI_ONTOLOGY + diagram_id)
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def create_project_properties(json_data: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Main function for decoding objects of type 'Project'.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain (every case) or range of (when related to an abstract class).

    This function considers that there may be multiple projects in the loaded JSON file.

    Created object properties:
        - ontouml:project (domain ontouml:OntoumlElement, range ontouml:Project)
        - ontouml:model (domain ontouml:Project, range ontouml:Package)
        - ontouml:diagram (domain ontouml:Project, range ontouml:Diagram)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # Getting all Project dictionaries
    projects_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Project")

    for project_dict in projects_dicts_list:

        set_ontoumlelement_project_project(project_dict, ontouml_graph, element_counting)
        set_project_model_package(project_dict, ontouml_graph)

        # Treats relations between instances of Project and Diagram only if the formers exist
        if "Diagram" in element_counting:
            set_project_diagram_diagram(project_dict, ontouml_graph)
