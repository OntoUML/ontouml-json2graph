""" Functions to decode specificities of the object Property.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

from rdflib import Graph, URIRef, RDF, Literal

from globals import URI_ONTOUML, URI_ONTOLOGY
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def set_property_relations(property_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the ontouml:aggregationKind and ontouml:propertyType object properties between an ontouml:Property and
    its related elements.

    :param property_dict: Property object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    statement_subject = URIRef(URI_ONTOLOGY + property_dict["id"])

    # Setting ontouml:aggregationKind
    statement_predicate = URIRef(URI_ONTOUML + "aggregationKind")
    statement_object = URIRef(URI_ONTOUML + property_dict["aggregationKind"].lower())
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Setting ontouml:propertyType
    if "propertyType" in property_dict:
        statement_predicate = URIRef(URI_ONTOUML + "propertyType")
        statement_object = URIRef(URI_ONTOLOGY + property_dict["propertyType"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def determine_cardinality_bounds(cardinalities: str, property_id: str) -> (str, str):
    """ Receives a string with an ontouml:Cardinality's ontoumL:cardinalityValues and decouple it into its
    ontouml:lowerBound and ontouml:upperBound. Checks if the obtained values are not valid and displays warning if so.

    :param cardinalities: String containing the value of the cardinality to be decoupled into lower and upper bounds.
    :type cardinalities: str
    :param property_id: ID of the Property that owns the cardinality being treated. Used in case of invalid cardinality.
    :type property_id: str
    :return: Tuple with lower and upper bounds, in this specific position, as strings.
    :rtype: (str, str)
    """

    lower_bound, _, upper_bound = cardinalities.partition("..")

    # If separator '..' not found, exact cardinality, meaning that lower and upper bounds have the same value
    if upper_bound == "":
        upper_bound = lower_bound
    # If lower bound is * it is converted to zero
    if lower_bound == "*":
        lower_bound = "0"

    # Validating discovered cardinality bounds
    if not (upper_bound.isnumeric() or upper_bound == "*"):
        LOGGER.warning(f"Invalid cardinality's upper bound (value '{upper_bound}') for Property individual with "
                       f"ID {property_id}. Transformation proceeded as is.")
    if not lower_bound.isnumeric():
        LOGGER.warning(f"Invalid cardinality's lower bound (value '{lower_bound}') for Property individual with "
                       f"ID {property_id}. Transformation proceeded as is.")

    return lower_bound, upper_bound


def set_cardinality_relations(property_dict: dict, ontouml_graph: Graph) -> None:
    """ Creates the ontouml:Cardinality instance and sets its properties.

    :param property_dict: Property object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    if "cardinality" in property_dict:
        ontology_property_individual = URIRef(URI_ONTOLOGY + property_dict["id"])
        ontology_cardinality_individual = URIRef(URI_ONTOLOGY + property_dict["id"] + '_cardinality')

        ontouml_cardinality_class = URIRef(URI_ONTOUML + "Cardinality")
        ontouml_cardinality_property = URIRef(URI_ONTOUML + "cardinality")
        ontouml_cardinalityvalue_property = URIRef(URI_ONTOUML + "cardinalityValue")
        ontouml_lowerbound_property = URIRef(URI_ONTOUML + "lowerBound")
        ontouml_upperbound_property = URIRef(URI_ONTOUML + "upperBound")

        # Creating ontouml:Cardinality individuals (named after its related Property's name + '_cardinality' string)
        ontouml_graph.add((ontology_cardinality_individual, RDF.type, ontouml_cardinality_class))

        # Setting the ontouml:cardinality between an ontouml:Property and its ontouml:Cardinality
        ontouml_graph.add((ontology_property_individual, ontouml_cardinality_property, ontology_cardinality_individual))

        # Setting the ontouml:cardinalityValue between an ontouml:Cardinality and its cardinality field
        ontouml_graph.add((ontology_cardinality_individual, ontouml_cardinalityvalue_property,
                           Literal(property_dict["cardinality"])))

        # Setting cardinality's lower and upper bounds
        lower_bound, upper_bound = determine_cardinality_bounds(property_dict["cardinality"], property_dict["id"])
        ontouml_graph.add((ontology_cardinality_individual, ontouml_lowerbound_property, Literal(lower_bound)))
        ontouml_graph.add((ontology_cardinality_individual, ontouml_upperbound_property, Literal(upper_bound)))

        # TODO (@pedropaulofb): Update vocabulary for all entities used in this module.


def create_property_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type Property.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created instances of class:
        - ontouml:Cardinality

    Created properties:
        - ontouml:aggregationKind (domain ontouml:Property, range ontouml:AggregationKind)
        - ontouml:propertyType (domain ontouml:Property, range ontouml:Classifier)
        - ontouml:cardinality (domain ontouml:Property, range ontouml:Cardinality)
        - ontouml:cardinalityValue (domain ontouml:Cardinality, range xsd:string)
        - ontouml:lowerBound (domain ontouml:Cardinality, range xsd:nonNegativeInteger)
        - ontouml:upperBound (domain ontouml:Cardinality)

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Getting Property dictionaries
    property_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Property")

    for property_dict in property_dicts_list:
        set_property_relations(property_dict, ontouml_graph)
        set_cardinality_relations(property_dict, ontouml_graph)
