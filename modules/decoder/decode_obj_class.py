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
from globals import URI_ONTOUML
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
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           URIRef(URI_ONTOUML + "order"),
                           Literal(0, datatype=XSD.nonNegativeInteger)))

    # Case A: remove invalid information so the field can be treated as null and then receive the default value.
    elif (type(class_dict["order"]) is int) and (class_dict["order"] <= 0):
        class_dict.pop("order")

    # Case B
    elif type(class_dict["order"]):
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
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
            ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
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
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           URIRef(URI_ONTOUML + "isExtensional"),
                           Literal(class_dict["isExtensional"])))

    if "isPowertype" in class_dict:
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           URIRef(URI_ONTOUML + "isPowertype"),
                           Literal(class_dict["isPowertype"])))


def set_class_attribute_defaults(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Verifies a class dictionary and check if their non-nullable attributes isExtensional and isPowertype were set
    or not. If not, creates default values.

    Default values checked are:

    CASE C) isPowertype default value = False when class's stereotype 'type'
    CASE D) isExtensional default value = False when class's stereotype 'collective'

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    class_stereotype = get_stereotype(class_dict)

    # CASE C: Setting IS_POWERTYPE attribute default value
    if "isPowertype" not in class_dict and class_stereotype == "type":
        print_class_log_message(class_dict, 5, attribute='isPowertype', attribute_valid_stereotype='type')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           URIRef(URI_ONTOUML + "isPowertype"), Literal(False)))

    # CASE D: Setting IS_EXTENSIONAL default value to False when it is not set in a class with stereotype collective
    if "isExtensional" not in class_dict and class_stereotype == "collective":
        print_class_log_message(class_dict, 5, attribute='isExtensional', attribute_valid_stereotype='collective')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           URIRef(URI_ONTOUML + "isExtensional"), Literal(False)))


def set_class_order_defaults(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Verifies a class dictionary and check if their non-nullable attribute order was set or not.
    If not, creates default values.

    Default values checked are:

    CASE A) order default value = 1 when class's stereotype is not 'type'
    CASE B) order default value = 2 when class's stereotype 'type'

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    class_stereotype = get_stereotype(class_dict)

    # Setting ORDER attribute default value
    if "order" not in class_dict:

        # CASE 0: Do nothing if the stereotype is unknown
        if class_stereotype == 'null':
            pass

        # CASE A: 'order' default value = 1 when stereotype is not 'type'
        elif class_stereotype != 'type':
            print_class_log_message(class_dict, 3, attribute='order')
            ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                               URIRef(URI_ONTOUML + "order"), Literal(1, datatype=XSD.nonNegativeInteger)))

        # CASE B: 'order' default value = 2 when stereotype is 'type'
        elif class_stereotype == 'type':
            print_class_log_message(class_dict, 4, attribute='order')
            ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                               URIRef(URI_ONTOUML + "order"), Literal(2, datatype=XSD.nonNegativeInteger)))

        # Unexpected value received for class_stereotype
        else:
            current_function = inspect.stack()[0][3]
            report_error_end_of_switch("class_stereotype", current_function)


def get_class_log_message(class_dict: dict, warning_code: int,
                          attribute: str, att_valid_stereotype: str = "") -> str:
    """ Mounts and returns a warning message according to the information received as parameter.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param warning_code: Code used to select the correct message to be displayed to the user if not in silent mode.
    :type warning_code: int
    :param attribute: Information about an attribute type to be displayed in a warning message. Optional.
    :type attribute: str
    :param att_valid_stereotype: Stereotype associated to an attribute to be displayed in a warning message. Optional.
    :type att_valid_stereotype: str
    :return: Warning message containing information about the modification made to be printed to user.
    :rtype: str
    """

    class_stereotype = get_stereotype(class_dict)
    message = "NOT DEFINED MESSAGE"
    att_value = class_dict[attribute] if attribute in class_dict else "null"
    class_identification = f"Class '{class_dict['name']}' <<{class_stereotype}>> (ID: {class_dict['id']}): "

    if warning_code == 0:
        message = "This class must not have values for both 'isExtensional' (allowed only for classes with " \
                  "stereotype 'collective') and 'isPowertype' (allowed only for 'type'). " \
                  "The transformation output is INVALID."

    elif warning_code == 1:
        message = f"stereotype (originally {class_stereotype}) set to '{att_valid_stereotype}' as it contains the " \
                  f"related attribute '{attribute}' (with value '{class_dict[attribute]}') that is only allowed in " \
                  f"classes with this stereotype."

    elif warning_code == 2:
        message = f"attribute '{attribute}' (originally '{att_value}') removed " \
                  f"as this attribute is only allowed in classes with stereotype '{att_valid_stereotype}'."

    elif warning_code == 3:
        message = f"attribute '{attribute}' (originally '{att_value}') set to '1', " \
                  f"the default value to classes with stereotype different than 'type'."

    elif warning_code == 4:
        message = f"attribute '{attribute}' (originally '{att_value}') set to '2', " \
                  f"the default value to classes with stereotype 'type'."

    elif warning_code == 5:
        message = f"attribute '{attribute}' (originally {att_value}) set to 'False', " \
                  f"the default value to classes with stereotype '{att_valid_stereotype}'."

    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("warning_number", current_function)

    return class_identification + message


def print_class_log_message(class_dict: dict, warning_number: int,
                            attribute: str = "", attribute_valid_stereotype: str = "",
                            message_type: str = "warning") -> None:
    """ Gets warning message and prints it to the user as a log if not in silent mode.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param warning_number: Predefined warning number to be displayed to the user if not in silent mode.
    :type warning_number: int
    :param attribute: Information about an attribute type to be displayed in a warning message. Optional.
    :type attribute: str
    :param attribute_valid_stereotype: Stereotype associated to an attribute to be displayed in a warning message. Optional.
    :type attribute_valid_stereotype: str
    :param message_type: Logger's level. Default value is 'warning'. Accepted values are: 'warning', 'error'.
    :type message_type: str
    """

    # If in silent mode, exit function and do not print anything
    if args.ARGUMENTS["silent"]:
        return

    log_message = get_class_log_message(class_dict, warning_number, attribute, attribute_valid_stereotype)

    if message_type == "warning":
        LOGGER.warning(log_message)
    elif message_type == "error":
        LOGGER.error(log_message)
    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("message_type", current_function)


def validate_class_attribute_constraints(class_dict: dict) -> None:
    """ Verifies all Class dictionaries and check if the constraints related to classes were correctly considered and
    fixes them when they are not.

    The checked constraints are:

    A) To the pair of attribute/stereotype: isExtensional/collective and isPowertype/type

    A0) If class without stereotype but with isExtensional and with isPowertype, then do nothing and report error.
    A1) If class has no stereotype, but the attribute is set, then set correct stereotype.
    A2) If class a different stereotype than the one related to the attribute and the attribute is set,
        then remove the attribute value.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    """

    if not args.ARGUMENTS["correct"]:
        return

    class_stereotype = get_stereotype(class_dict)

    att_valid = {"isExtensional": "collective",
                 "isPowertype": "type"}

    # CASE A0: Treating a bizzare case where the class has no stereotype but has both attributes
    if ("isExtensional" in class_dict) and ("isPowertype" in class_dict) and ("stereotype" not in class_dict):
        print_class_log_message(class_dict, 0, message_type="error")
    else:
        for attribute in att_valid.keys():

            att_stereotype = att_valid[attribute]

            if attribute not in class_dict:
                continue

            # CASE A1: Case class has attribute but no stereotype, set the stereotype
            elif class_stereotype == "null":
                print_class_log_message(class_dict, 1, attribute, att_stereotype)
                class_dict["stereotype"] = att_stereotype

            # CASE A2: Case the attribute was set to an invalid stereotype, remove it
            elif class_stereotype != att_stereotype:
                print_class_log_message(class_dict, 2, attribute, att_stereotype)
                class_dict.pop(attribute)


def validate_class_order_constraints(class_dict: dict) -> None:
    """ Verifies all Class dictionaries and check if the constraints related to classes were correctly considered and
    fixes them when they are not.

    The checked constraints are:

    B) 'order' property must be greater than 1 when class's stereotype is 'type'
    C) class's 'order' property must be 1 when class's stereotype is not 'type'

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    """

    if not args.ARGUMENTS["correct"]:
        return

    class_stereotype = get_stereotype(class_dict)

    # Constraints B and C depend on the existence of the order attribute
    if "order" in class_dict:

        # Constraint B: order must be greater than 1 when the class's stereotype is 'type'
        if class_stereotype == "type" and ((class_dict["order"] == 1) or (class_dict["order"] == "1")):
            # The 'order' value is removed, so it can receive a new value in the set_class_defaults function
            class_dict.pop('order')

        # Constraint C: class's order must be 1 when class's stereotype is not 'type'
        if class_stereotype != "type" and class_dict["order"] != 1:
            # The 'order' value is removed, so it can receive a new value in the set_class_defaults function
            class_dict.pop('order')


def set_class_attribute_property(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:attribute relation between an ontouml:Class and an ontouml:Property.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    list_related_properties = get_list_subdictionaries_for_specific_type(class_dict, "Property")

    for related_property in list_related_properties:
        statement_subject = URIRef(args.ARGUMENTS["base_uri"] + class_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "attribute")
        statement_object = URIRef(args.ARGUMENTS["base_uri"] + related_property["id"])

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
        statement_subject = URIRef(args.ARGUMENTS["base_uri"] + class_dict["id"])
        statement_predicate = URIRef(URI_ONTOUML + "literal")
        statement_object = URIRef(args.ARGUMENTS["base_uri"] + related_literal["id"])

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

        if "gGhuFxGFS_j2pAmkX3" in class_dict['id']:
            print(f"0: {class_dict = }")

        # Performs validation (only cases enabled by the user)
        # Priority order is: (1) stereotype, (2) isExtensional and isPowertype attributes, (3) order attribute
        validate_class_attribute_constraints(class_dict)
        validate_class_order_constraints(class_dict)

        if "gGhuFxGFS_j2pAmkX3" in class_dict['id']:
            print(f"1: {class_dict = }")

        # Setting properties
        set_class_order_nonnegativeinteger(class_dict, ontouml_graph)
        set_object_stereotype(class_dict, ontouml_graph)
        set_class_restrictedto_ontologicalnature(class_dict, ontouml_graph)

        # Setting default values when the values were not provided
        set_class_order_defaults(class_dict, ontouml_graph)
        set_class_attribute_defaults(class_dict, ontouml_graph)

        if "gGhuFxGFS_j2pAmkX3" in class_dict['id']:
            print(f"2: {class_dict = }")

        # Setting isPowertype and isExtensional
        set_class_attributes(class_dict, ontouml_graph)

        if "gGhuFxGFS_j2pAmkX3" in class_dict['id']:
            print(f"3: {class_dict = }")

        # Treats relations between instances of Class and Property only if the formers exist
        if "Property" in element_counting:
            set_class_attribute_property(class_dict, ontouml_graph)

        # Treats relations between instances of Class and Literal only if the formers exist
        if "Literal" in element_counting:
            set_class_literal_literal(class_dict, ontouml_graph)

        if "gGhuFxGFS_j2pAmkX3" in class_dict['id']:
            print(f"4: {class_dict = }")
