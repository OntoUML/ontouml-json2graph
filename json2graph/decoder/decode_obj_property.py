"""Functions to decode specificities of the object Property.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
    - Functions that set default values: set_<subject>_defaults.
"""

from rdflib import Graph, URIRef, RDF, Literal, XSD

from ..decoder.decode_general import get_list_subdictionaries_for_specific_type
from ..modules import arguments as args
from ..modules.logger import initialize_logger
from ..modules.messages import print_decode_log_message
from ..modules.sparql_queries import GET_CLASS_STEREOTYPE_ATTRIBUTE_STEREOTYPE
from ..modules.utils_graph import load_ontouml_vocabulary, ontouml_ref

LOGGER = initialize_logger()


def validate_property_stereotype(ontouml_graph: Graph) -> None:
    """Perform syntactical and semantic validations on an ontouml:Property's stereotype.

    Differently from what is used in the validation of other JSON objects, this function manipulates the graph itself,
    not the JSON object. This is because it is much straightforward to access all the necessary property elements.

    Validations performed:
    VPS1) Reports invalid property stereotypes (i.e., stereotypes different from ontouml:begin or ontouml:end).
    VPS2) Reports if a property stereotype is used in association with an invalid class stereotype.
    I.e., a class stereotype that is known and different from 'event'.
    VPS3) Sets class stereotype as 'event' when it is associated to a property that has an assigned valid stereotype.

    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    if not args.ARGUMENTS["correct"]:
        return

    ontouml_meta_graph = load_ontouml_vocabulary()
    aggregated_graph = ontouml_meta_graph + ontouml_graph
    query_answer = aggregated_graph.query(GET_CLASS_STEREOTYPE_ATTRIBUTE_STEREOTYPE)

    for row in query_answer:
        class_id = (row.class_id).fragment
        class_stereotype = (row.class_stereotype).fragment
        class_name = row.class_name.toPython()
        property_id = (row.property_id).fragment
        property_stereotype = (row.property_stereotype).fragment

        # VPS1: If the asserted stereotype is invalid, create the statement and report error.
        if property_stereotype not in ["begin", "end"]:
            dict_argument = {"type": "Property", "id": property_id}
            print_decode_log_message(dict_argument, "VPS1")

        # VPS2: If class has known stereotype and is not event, report sematic error.
        elif class_stereotype not in ["event", "null"]:
            dict_argument = {
                "type": "Class",
                "name": class_name,
                "id": class_id,
                "stereotype": class_stereotype,
                "propID": property_id,
                "propST": property_stereotype,
            }
            print_decode_log_message(dict_argument, "VPS2")

        # VPS3: If class has unknown stereotype and stereotyped property, set its stereotype as 'event'.
        elif class_stereotype == "null":
            dict_argument = {
                "type": "Class",
                "name": class_name,
                "id": class_id,
                "stereotype": class_stereotype,
                "propID": property_id,
                "propST": property_stereotype,
            }
            print_decode_log_message(dict_argument, "VPS3")

            ontouml_graph.add(
                (
                    URIRef(args.ARGUMENTS["base_uri"] + class_id),
                    ontouml_ref("stereotype"),
                    ontouml_ref("event"),
                )
            )


def set_property_defaults(property_dict: dict, ontouml_graph: Graph) -> None:
    """Set default values for ontouml:Property elements that do not present them.

    The defaults are:
        DPA1) ontouml:isDerived default value = False
        DPA2) ontouml:isOrdered default value = False
        DPA3) ontouml:isReadOnly default value = False

    :param property_dict: Property object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    # DPA1, DPA2, and DPA3 use the same message DGA1, as they are not associated to their holder's stereotype.

    # DPA1: Setting ontouml:isDerived attribute default value
    if "isDerived" not in property_dict:
        print_decode_log_message(property_dict, "DGA1", property_name="isDerived")
        ontouml_graph.add(
            (
                URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"]),
                ontouml_ref("isDerived"),
                Literal(False, datatype=XSD.boolean),
            )
        )

    # DPA2: Setting ontouml:isOrdered attribute default value
    if "isOrdered" not in property_dict:
        print_decode_log_message(property_dict, "DGA1", property_name="isOrdered")
        ontouml_graph.add(
            (
                URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"]),
                ontouml_ref("isOrdered"),
                Literal(False, datatype=XSD.boolean),
            )
        )

    # DPA3: Setting ontouml:isReadOnly attribute default value
    if "isReadOnly" not in property_dict:
        print_decode_log_message(property_dict, "DGA1", property_name="isReadOnly")
        ontouml_graph.add(
            (
                URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"]),
                ontouml_ref("isReadOnly"),
                Literal(False, datatype=XSD.boolean),
            )
        )


def set_property_relations(property_dict: dict, ontouml_graph: Graph) -> None:
    """Set the ontouml:aggregationKind and ontouml:propertyType object properties between an ontouml:Property and \
    its related elements.

    :param property_dict: Property object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    statement_subject = URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"])

    # Setting ontouml:aggregationKind
    if "aggregationKind" not in property_dict:
        statement_object = ontouml_ref("none")
    else:
        statement_object = ontouml_ref(property_dict["aggregationKind"].lower())

    statement_predicate = ontouml_ref("aggregationKind")
    ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Setting ontouml:propertyType
    if "propertyType" in property_dict:
        statement_predicate = ontouml_ref("propertyType")
        statement_object = URIRef(args.ARGUMENTS["base_uri"] + property_dict["propertyType"]["id"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Setting ontouml:stereotype. Its validation is performed later in function validate_property_stereotype
    if "stereotype" in property_dict:
        statement_predicate = ontouml_ref("stereotype")
        statement_object = ontouml_ref(property_dict["stereotype"])
        ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Setting ontouml:subsetsProperty
    if "subsettedProperties" in property_dict:
        statement_predicate = ontouml_ref("subsetsProperty")

        for subsetted_prop_dict in property_dict["subsettedProperties"]:
            statement_object = URIRef(args.ARGUMENTS["base_uri"] + subsetted_prop_dict["id"])
            ontouml_graph.add((statement_subject, statement_predicate, statement_object))

    # Setting ontouml:redefinesProperty
    if "redefinedProperties" in property_dict:
        statement_predicate = ontouml_ref("redefinesProperty")

        for redefined_prop_dict in property_dict["redefinedProperties"]:
            statement_object = URIRef(args.ARGUMENTS["base_uri"] + redefined_prop_dict["id"])
            ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def determine_cardinality_bounds(cardinalities: str, property_id: str) -> (str, str, str):
    """Receive a string with an ontouml:Cardinality's ontouml:cardinalityValue, fix its format and decouple it into \
    its ontouml:lowerBound and ontouml:upperBound. Checks and displays warning if the obtained values are not valid.

    :param cardinalities: String containing the value of the cardinality to be decoupled into lower and upper bounds.
    :type cardinalities: str
    :param property_id: ID of the Property that owns the cardinality being treated. Used in case of invalid cardinality.
    :type property_id: str
    :return: Tuple of three elements: full cardinality, cardinality's lower bound, and cardinality's upper bound.
    :rtype: (str, str, str)
    """
    lower_bound, _, upper_bound = cardinalities.partition("..")

    # If separator '..' not found, exact cardinality, meaning that lower and upper bounds have the same value
    if upper_bound == "":
        upper_bound = lower_bound
    # If lower bound is * it is converted to zero
    if lower_bound == "*":
        lower_bound = "0"

    full_cardinality = lower_bound + ".." + upper_bound

    # Validating discovered cardinality bounds
    if not (upper_bound.isnumeric() or upper_bound == "*") and not args.ARGUMENTS["silent"]:
        LOGGER.warning(
            f"Invalid cardinality's upper bound (value '{upper_bound}') for Property individual with "
            f"ID '{property_id}'. Transformation proceeded as is."
        )
    if not lower_bound.isnumeric() and not args.ARGUMENTS["silent"]:
        LOGGER.warning(
            f"Invalid cardinality's lower bound (value '{lower_bound}') for Property individual with "
            f"ID '{property_id}'. Transformation proceeded as is."
        )

    return full_cardinality, lower_bound, upper_bound


def set_cardinality_relations(property_dict: dict, ontouml_graph: Graph) -> None:
    """Create the ontouml:Cardinality instance and sets its properties.

    :param property_dict: Property object loaded as a dictionary.
    :type property_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    if "cardinality" in property_dict:
        ontology_property_individual = URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"])
        ontology_cardinality_individual = URIRef(args.ARGUMENTS["base_uri"] + property_dict["id"] + "_cardinality")

        ontouml_cardinality_class = ontouml_ref("Cardinality")
        ontouml_cardinality_property = ontouml_ref("cardinality")

        ontouml_cardinalityvalue_property = ontouml_ref("cardinalityValue")
        ontouml_lowerbound_property = ontouml_ref("lowerBound")
        ontouml_upperbound_property = ontouml_ref("upperBound")

        # Creating ontouml:Cardinality individuals (named after its related Property's name + '_cardinality' string)
        ontouml_graph.add((ontology_cardinality_individual, RDF.type, ontouml_cardinality_class))

        # Setting the ontouml:cardinality between an ontouml:Property and its ontouml:Cardinality
        ontouml_graph.add(
            (
                ontology_property_individual,
                ontouml_cardinality_property,
                ontology_cardinality_individual,
            )
        )

        # Setting the full cardinality value and the lower and upper bounds
        full_cardinality, lower_bound, upper_bound = determine_cardinality_bounds(
            property_dict["cardinality"], property_dict["id"]
        )
        ontouml_graph.add(
            (
                ontology_cardinality_individual,
                ontouml_cardinalityvalue_property,
                Literal(full_cardinality),
            )
        )
        ontouml_graph.add(
            (
                ontology_cardinality_individual,
                ontouml_lowerbound_property,
                Literal(lower_bound),
            )
        )
        ontouml_graph.add(
            (
                ontology_cardinality_individual,
                ontouml_upperbound_property,
                Literal(upper_bound),
            )
        )


def create_property_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """Decode object of type Property.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created instances of class:
        - ontouml:Cardinality

    Created properties:
        - ontouml:aggregationKind (domain ontouml:Property, range ontouml:AggregationKind)
        - ontouml:propertyType (domain ontouml:Property, range ontouml:Classifier)
        - ontouml:stereotype (domain ontouml:Property, range ontouml:PropertyStereotype)
        - ontouml:cardinality (domain ontouml:Property, range ontouml:Cardinality)
        - ontouml:cardinalityValue (domain ontouml:Cardinality, range xsd:string)
        - ontouml:lowerBound (domain ontouml:Cardinality, range xsd:nonNegativeInteger)
        - ontouml:upperBound (domain ontouml:Cardinality)
        - ontouml:subsetsProperty (range ontouml:Property)
        - ontouml:redefinesProperty (range ontouml:Property)
        - ontouml:isDerived (range xsd:boolean)
        - ontouml:isOrdered (range xsd:boolean)
        - ontouml:isReadOnly (range xsd:boolean)

    Performs validation for ontouml:stereotype.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """
    # Getting Property dictionaries
    property_dicts_list = get_list_subdictionaries_for_specific_type(json_data, "Property")

    for property_dict in property_dicts_list:
        # Removing possible dictionaries that are only references
        if len(property_dict) < 3:
            continue

        set_property_defaults(property_dict, ontouml_graph)
        set_property_relations(property_dict, ontouml_graph)
        set_cardinality_relations(property_dict, ontouml_graph)

    validate_property_stereotype(ontouml_graph)
