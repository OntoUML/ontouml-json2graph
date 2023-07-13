""" Functions to decode objects of type Class.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

import inspect

from rdflib import Graph, URIRef, XSD, Literal

import modules.arguments as args
from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type, get_stereotype, \
    set_object_stereotype
from modules.errors import report_error_end_of_switch
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def set_class_order_nonnegativeinteger(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets an ontouml:Class's ontouml:order property based on the received value of the object's field 'order'.

    The treated possibilities are:
    A) invalid value (null, non integers, integers <= 0) ---> is converted to the default value of the class
    B) positive integers ---> directly converted
    C) * (representing an orderless type) ---> converted to 0 (representation of orderless in the OntoUML Vocabulary).

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Case A: if 'order' field is null, it will receive the default value (see function set_class_defaults)
    if "order" not in class_dict:
        return

    # Case C: receives 0, representing an orderless class.
    elif class_dict["order"] == "*":
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "order"),
                           Literal(0, datatype=XSD.nonNegativeInteger)))

    # Case A: remove invalid information so the field can be treated as null and then receive the default value.
    elif (type(class_dict["order"]) is int) and (class_dict["order"] <= 0):
        class_dict.pop("order")

    # Case B
    elif type(class_dict["order"]):
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "order"),
                           Literal(class_dict['order'], datatype=XSD.nonNegativeInteger)))

    # Case A: remove invalid information so the field can be treated as null and then receive the default value.
    else:
        class_dict.pop("order")


def set_class_restrictedto_ontologicalnature(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets the ontouml:restrictedTo relation between a class and its related ontouml:OntologicalNature instance.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    restriction_nature_mapping = {
        "abstract": "abstractNature",
        "collective": "collectiveNature",
        "event": "eventNature",
        "extrinsic-mode": "extrinsicModeNature",
        "functional-complex": "functionalComplexNature",
        "intrinsic-mode": "intrinsicModeNature",
        "quality": "qualityNature",
        "quantity": "quantityNature",
        "relator": "relatorNature",
        "situation": "situationNature",
        "type": "typeNature"
    }

    if "restrictedTo" in class_dict:

        for restriction in class_dict["restrictedTo"]:
            ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                               URIRef(URI_ONTOUML + "restrictedTo"),
                               URIRef(URI_ONTOUML + restriction_nature_mapping[restriction])))


def set_class_attributes(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Defines the ontouml:isPowertype and ontouml:isExtensional data properties of an ontouml:Class in the graph.

    This function must be called after the function set_class_defaults, as the received value may change because of
    identified problems.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    if "isExtensional" in class_dict:
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "isExtensional"),
                           Literal(class_dict["isExtensional"])))

    if "isPowertype" in class_dict:
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "isPowertype"),
                           Literal(class_dict["isPowertype"])))


def set_class_defaults(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Verifies a class dictionary and check if their non-nullable attributes were set or not.
    If not, creates default values.

    Default values checked are:
    - order default value = 1 when class's stereotype is not 'type'
    - order default value = 2 when class's stereotype 'type'
    - isPowertype default value = False

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    class_stereotype = get_stereotype(class_dict)

    # Warning messages
    warning_msg1 = f"The class '{class_dict['name']}' had its order attribute (originally 'null') set to 1 " \
                   f"(default to classes with stereotype different than 'type')."
    warning_msg2 = f"The class {class_dict['name']} had its 'order' attribute (originally null) set to 2 " \
                   f"(default to classes with stereotype 'type')."
    warning_msg3 = f"The class {class_dict['name']} had its 'isPowertype' attribute (originally null) " \
                   f"set to False (default)."

    # DEFAULT: ORDER VALUE
    if "order" not in class_dict:

        # Default: order default value = 1 when stereotype is not 'type'
        if (class_stereotype == "null") or (class_stereotype != 'type'):
            if not args.ARGUMENTS["silent"]:
                LOGGER.warning(warning_msg1)
            ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                               URIRef(URI_ONTOUML + "order"),
                               Literal(1, datatype=XSD.nonNegativeInteger)))

        # Default: order default value = 2 when stereotype is 'type'
        elif class_stereotype == 'type':
            if not args.ARGUMENTS["silent"]:
                LOGGER.warning(warning_msg2)
            ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                               URIRef(URI_ONTOUML + "order"),
                               Literal(2, datatype=XSD.nonNegativeInteger)))

        # Unexpected value received for class_stereotype
        else:
            current_function = inspect.stack()[0][3]
            report_error_end_of_switch("class_stereotype", current_function)

    # DEFAULT: ISPOWERTYPE DEFAULT VALUE = FALSE
    if "isPowertype" not in class_dict:
        if not args.ARGUMENTS["silent"]:
            LOGGER.warning(warning_msg3)
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "isPowertype"),
                           Literal(False)))


def validate_class_constraints(class_dict: dict) -> None:
    """ Verifies all Class dictionaries and check if the constraints related to classes were correctly considered and
    fixes them when they are not.

    The checked constraints are:
    A) isExtensional must be null when the class's stereotype is not 'collective'
    B) order must be greater than 1 when class's stereotype is 'type'
    C) class's order must be 1 when class's stereotype is not 'type'
    D) class must have stereotype 'type' when no stereotype is informed and when its isPowertype attribute is true
    E) class's isPowertype must be false when class's stereotype is not 'type'

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    """

    class_stereotype = get_stereotype(class_dict)

    class_dict_order = ""
    class_dict_is_pt = ""
    class_dict_is_ext = ""

    # Warning messages
    warning_msg1 = f"The class '{class_dict['name']}' of stereotype '{class_stereotype}' had its isExtensional " \
                   f"attribute (originally '{class_dict_is_ext}') removed as it is not of stereotype collective."
    warning_msg2 = f"The class '{class_dict['name']}' of stereotype '{class_stereotype}' had its order attribute " \
                   f"(originally '{class_dict_order}') set to '2' (default for 'type')."
    warning_msg3 = f"The class '{class_dict['name']}' of stereotype '{class_stereotype}' had its order attribute " \
                   f"(originally '{class_dict_order}') set to '1' as it is not a 'type')."
    warning_msg4 = f"The class '{class_dict['name']}' had its stereotype (originally unknown) set 'type' as its " \
                   f"isPowertype attribute is 'True'."
    warning_msg5 = f"The class '{class_dict['name']}' of stereotype '{class_stereotype}' had its isPowertype " \
                   f"attribute (originally '{class_dict_is_pt}') set to 1 as it is not of stereotype type."

    # Constraint A: isExtensional must be null when the class's stereotype is not 'collective'
    if ("isExtensional" in class_dict) and class_stereotype != "collective":
        if not args.ARGUMENTS["silent"]:
            class_dict_is_ext = class_dict['isExtensional']
            LOGGER.warning(warning_msg1)
        class_dict.pop('isExtensional')

    # Constraints B and C depend on the existence of the order attribute
    if "order" in class_dict and args.ARGUMENTS["correct"]:

        # Constraint B: order must be greater than 1 when the class's stereotype is 'type'
        if class_stereotype == "type" and ((class_dict["order"] == 1) or (class_dict["order"] == "1")):
            if not args.ARGUMENTS["silent"]:
                class_dict_order = class_dict['order']
                LOGGER.warning(warning_msg2)
            class_dict.pop('order')

        # Constraint C: class's order must be 1 when class's stereotype is not 'type'
        if class_stereotype != "type" and class_dict["order"] != 1:
            if not args.ARGUMENTS["silent"]:
                class_dict_order = class_dict['order']
                LOGGER.warning(warning_msg3)
            class_dict.pop('order')

    # Constraint D: class must have stereotype 'type' when no stereotype and when its isPowertype attribute is true
    if "isPowertype" in class_dict and args.ARGUMENTS["correct"]:
        if class_dict["isPowertype"] and class_stereotype == "null":
            if not args.ARGUMENTS["silent"]:
                LOGGER.warning(warning_msg4)
            class_dict['stereotype'] = "type"

    # Constraint E: class's isPowertype must be false when class's stereotype is not ('type' or undefined)
    if "isPowertype" in class_dict and args.ARGUMENTS["correct"]:
        if class_dict["isPowertype"] and not (class_stereotype == "type" or class_stereotype == "null"):
            if not args.ARGUMENTS["silent"]:
                class_dict_is_pt = class_dict['isPowertype']
                LOGGER.warning(warning_msg5)
            class_dict['isPowertype'] = False


def set_class_attribute_property(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:attribute relation between an ontouml:Class and an ontouml:Property.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_related_properties = get_list_subdictionaries_for_specific_type(class_dict, "Property")

    for related_property in list_related_properties:
        statement_subject = URIRef(URI_ONTOLOGY + class_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "attribute")
        statement_object = URIRef(URI_ONTOLOGY + related_property["id"])

        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def set_class_literal_literal(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:literal relation between an ontouml:Class and its related ontouml:Literal individuals.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_related_literals = get_list_subdictionaries_for_specific_type(class_dict, "Literal")

    for related_literal in list_related_literals:
        statement_subject = URIRef(URI_ONTOLOGY + class_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "literal")
        statement_object = URIRef(URI_ONTOLOGY + related_literal["id"])

        ontouml_graph.add((statement_subject, statement_predicate, statement_object))


def create_class_properties(json_data: dict, ontouml_graph: Graph, element_counting: dict) -> None:
    """ Main function for decoding an object of type 'Class'.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:order (range xsd:nonNegativeInteger)
        - ontouml:stereotype (range ontouml:ClassStereotype)
        - ontouml:restrictedTo (range ontouml:OntologicalNature)
        - ontouml:isPowertype (range xsd:boolean)
        - ontouml:isExtensional (range xsd:boolean)
        - ontouml:attribute (range ontouml:Property)
        - ontouml:literal (range ontouml:Literal)

    Dictionaries containing classes IDs are used for reference. One of its characteristics is that they do not have the
    field 'name'. These are not Classes dictionaries and, hence, are not treated here.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    :param element_counting: Dictionary with types and respective quantities present on graph.
    :type element_counting: dict
    """

    # Get all class' dictionaries
    list_all_class_dicts = get_list_subdictionaries_for_specific_type(json_data, "Class")

    # Treat each object dictionary
    for class_dict in list_all_class_dicts:

        # Skipping dictionaries that only make reference to classes (and not class dictionaries)
        if "name" not in class_dict:
            continue

        # Performs validation (only cases enabled by the user)
        validate_class_constraints(class_dict)

        # Setting properties
        set_class_order_nonnegativeinteger(class_dict, ontouml_graph)
        set_object_stereotype(class_dict, ontouml_graph)
        set_class_restrictedto_ontologicalnature(class_dict, ontouml_graph)

        # Setting default values when the values were not provided
        set_class_defaults(class_dict, ontouml_graph)

        # Setting isPowertype and isExtensional
        set_class_attributes(class_dict, ontouml_graph)

        # Treats relations between instances of Class and Property only if the formers exist
        if "Property" in element_counting:
            set_class_attribute_property(class_dict, ontouml_graph)

        # Treats relations between instances of Class and Literal only if the formers exist
        if "Literal" in element_counting:
            set_class_literal_literal(class_dict, ontouml_graph)
