""" Functions to decode objects of type Class.

Function's nomenclatures:
    - Functions that set one property are named: set_<subject>_<predicate>_<object>.
    - Functions that set multiple object properties are named: set_<subject>_relations.
    - Functions that set multiple data properties are named: set_<subject>_attributes.
    - Functions that set both object and data properties are named: set_<subject>_properties.
"""

import inspect

from rdflib import Graph, URIRef, XSD, Literal

from .. import arguments as args
from ..decoder.decode_general import get_list_subdictionaries_for_specific_type, get_stereotype
from ..errors import report_error_end_of_switch
from ..messages import print_decode_log_message
from ..utils_graph import ontouml_ref


def validate_class_attribute_constraints(class_dict: dict) -> None:
    """ Verifies all Class dictionaries and check if the constraints related to classes were correctly considered and
    fixes them when they are not.

    The pair of attribute/stereotype: isExtensional/collective and isPowertype/type checked constraints are:

    VCA1) If class is not type and has isExtensional True and isPowertype True, then do nothing and report error.
    VCA2a) If class has no stereotype and isExtensional is not null, set as ontouml:collective.
    VCA2b) If class has no stereotype and isPowertype is True, set as ontouml: type.
    VCA3a) If class has stereotype different from 'collective' and isExtensional is not null, remove isExtensional.
    VCA3b) If class has stereotype different from 'type' and isPowertype is True, set isPowertype as False.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    """

    if not args.ARGUMENTS["correct"]:
        return

    class_stereotype = get_stereotype(class_dict)

    # VCA1: Reports Class different from 'type' with isExtensional value not null and isPowertype value True.
    if (class_stereotype != 'type') and ("isExtensional" in class_dict) and ("isPowertype" in class_dict):
        if class_dict["isPowertype"]:
            print_decode_log_message(class_dict, "VCA1")

    # VCA2a: Class has no stereotype, but has isExtensional not null. Set stereotype as 'collective'.
    elif (class_stereotype == "null") and ("isExtensional" in class_dict):
        print_decode_log_message(class_dict, "VCA2", "isExtensional", "collective")
        class_dict["stereotype"] = "collective"

    # VCA2b: Class has no stereotype, but has isPowertype equal True. Set stereotype as 'type'.
    elif (class_stereotype == "null") and ("isPowertype" in class_dict):
        if class_dict["isPowertype"]:
            print_decode_log_message(class_dict, "VCA2", "isPowertype", "type")
            class_dict["stereotype"] = "type"

    # VCA3a: Class has stereotype different than 'collective' and isExtensional not null. Remove isExtensional.
    elif (class_stereotype != "collective") and ("isExtensional" in class_dict):
        print_decode_log_message(class_dict, "VCA3a", "isExtensional", "collective")
        class_dict.pop("isExtensional")

    # VCA3b: Class has stereotype different than 'type' and isPowertype 'True'. Set isPowertype as 'False'.
    elif (class_stereotype != "type") and ("isPowertype" in class_dict):
        if class_dict["isPowertype"]:
            print_decode_log_message(class_dict, "VCA3b", "isPowertype", "type")
            class_dict["isPowertype"] = False


def validate_class_order_constraints(class_dict: dict) -> None:
    """ Verifies all Class dictionaries and check if the constraints related to classes were correctly considered and
    fixes them when they are not.

    The checked constraints are:

    VCO1) 'order' property must be greater than 1 when class's stereotype is 'type'
    VCO2) class's 'order' property must be 1 when class's stereotype is not 'type'

    The above codes are used to display warning/error messages when necessary.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    """

    if not args.ARGUMENTS["correct"]:
        return

    class_stereotype = get_stereotype(class_dict)

    # Constraints VCO1 and VCO2 depend on the existence of the order attribute
    if "order" in class_dict:

        # VCO1: order must be greater than 1 when the class's stereotype is 'type'. Remove order to set default.
        if class_stereotype == "type" and ((class_dict["order"] == 1) or (class_dict["order"] == "1")):
            # The 'order' value is removed, so it can receive a new value in the set_class_defaults function
            class_dict.pop('order')

        # VCO2: class's order must be 1 when class's stereotype is not 'type'. Remove order to set default.
        if class_stereotype != "type" and class_dict["order"] != 1:
            # The 'order' value is removed, so it can receive a new value in the set_class_defaults function
            class_dict.pop('order')


def set_defaults_class_attribute(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Verifies a class dictionary and check if their non-nullable attributes isExtensional and isPowertype were set
    or not. If not, creates default values. Default values checked are:

    DCA1) ontouml:isExtensional default value = False when class's stereotype 'collective'
    DCA2) ontouml:isPowertype default value = False
    DCA3) ontouml:isDerived default value = False
    DCA4) ontouml:isAbstract default value = False

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    class_stereotype = get_stereotype(class_dict)

    # DCA1: Setting ontouml:isExtensional default value to False when it's not set in a class with stereotype collective
    if "isExtensional" not in class_dict and class_stereotype == "collective":
        print_decode_log_message(class_dict, "DCA1", property_name='isExtensional', att_valid_stereotype='collective')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("isExtensional"), Literal(False, datatype=XSD.boolean)))

    # DCA2, DCA3, and DCA4 use the same message DGA1, as they are not associated to their holder's stereotype

    # DCA2: Setting ontouml:isPowertype attribute default value
    if "isPowertype" not in class_dict:
        print_decode_log_message(class_dict, "DGA1", property_name='isPowertype')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("isPowertype"), Literal(False, datatype=XSD.boolean)))

    # DCA3: Setting ontouml:isDerived attribute default value
    if "isDerived" not in class_dict:
        print_decode_log_message(class_dict, "DGA1", property_name='isDerived')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("isDerived"), Literal(False, datatype=XSD.boolean)))

    # DCA4: Setting ontouml:isAbstract attribute default value
    if "isAbstract" not in class_dict:
        print_decode_log_message(class_dict, "DGA1", property_name='isAbstract')
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("isAbstract"), Literal(False, datatype=XSD.boolean)))


def set_defaults_class_order(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Verifies a class dictionary and check if their non-nullable attribute order was set or not.
    If not, creates default values.

    Default values checked are:

    DCO1) order default value = 1 when class's stereotype is not 'type'
    DCO2) order default value = 2 when class's stereotype 'type'

    The above codes are used to display warning/error messages when necessary.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    class_stereotype = get_stereotype(class_dict)

    # Setting ORDER attribute default value. Do nothing if the stereotype is unknown.
    if ("order" not in class_dict) and (class_stereotype != 'null'):

        # DCO1: 'order' default value = 1 when stereotype is not 'type'
        if class_stereotype != 'type':
            print_decode_log_message(class_dict, "DCO1", property_name='order')
            ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                               ontouml_ref("order"), Literal(1, datatype=XSD.nonNegativeInteger)))

        # DCO2: 'order' default value = 2 when stereotype is 'type'
        elif class_stereotype == 'type':
            print_decode_log_message(class_dict, "DCO2", property_name='order')
            ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                               ontouml_ref("order"), Literal(2, datatype=XSD.nonNegativeInteger)))

        # Unexpected value received for class_stereotype
        else:
            current_function = inspect.stack()[0][3]
            report_error_end_of_switch("class_stereotype", current_function)


def set_class_stereotype(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:stereotype property between an instance of ontouml:Class and an instance representing an
    ontouml:ClassStereotype.

    Warning messages:
        - VCS1: Mandatory stereotype not assigned to a class. Result is invalid.
        - VCS2: Class has invalid stereotype associated to it. Result is invalid.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    ENUM_CLASS_STEREOTYPE = ["type", "historicalRole", "historicalRoleMixin", "event", "situation", "category", "mixin",
                             "roleMixin", "phaseMixin", "kind", "collective", "quantity", "relator", "quality", "mode",
                             "subkind", "role", "phase", "enumeration", "datatype", "abstract"]

    class_stereotype = get_stereotype(class_dict)

    # If stereotype not declared, report warning.
    if class_stereotype == "null":
        print_decode_log_message(class_dict, "VCS1", "stereotype")
    else:
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("stereotype"),
                           ontouml_ref(class_dict['stereotype'])))

        # If declared but invalid, create and report error. Uses generic message with code 'VCSG'.
        if class_stereotype not in ENUM_CLASS_STEREOTYPE:
            print_decode_log_message(class_dict, "VCSG", property_name="stereotype")


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
                           ontouml_ref("order"),
                           Literal(0, datatype=XSD.nonNegativeInteger)))

    # Case A: remove invalid information so the field can be treated as null and then receive the default value.
    elif (type(class_dict["order"]) is int) and (class_dict["order"] <= 0):
        class_dict.pop("order")

    # Case B
    elif type(class_dict["order"]):
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("order"),
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
                               ontouml_ref("restrictedTo"),
                               ontouml_ref(restriction_nature_mapping[restriction])))


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
                           ontouml_ref("isExtensional"),
                           Literal(class_dict["isExtensional"], datatype=XSD.boolean)))

    if "isPowertype" in class_dict:
        ontouml_graph.add((URIRef(args.ARGUMENTS["base_uri"] + class_dict['id']),
                           ontouml_ref("isPowertype"),
                           Literal(class_dict["isPowertype"], datatype=XSD.boolean)))


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
        statement_predicate = ontouml_ref("attribute")
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
        statement_predicate = ontouml_ref("literal")
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
        - ontouml:isDerived (range xsd:boolean)
        - ontouml:isAbstract (range xsd:boolean)
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
        # Priority order is: (1) stereotype, (2) isExtensional and isPowertype attributes, (3) order attribute
        validate_class_attribute_constraints(class_dict)
        validate_class_order_constraints(class_dict)

        # Setting properties
        set_class_order_nonnegativeinteger(class_dict, ontouml_graph)
        set_class_stereotype(class_dict, ontouml_graph)
        set_class_restrictedto_ontologicalnature(class_dict, ontouml_graph)

        # Setting default values when the values were not provided
        set_defaults_class_order(class_dict, ontouml_graph)
        set_defaults_class_attribute(class_dict, ontouml_graph)

        # Setting isPowertype and isExtensional
        set_class_attributes(class_dict, ontouml_graph)

        # Treats relations between instances of Class and Property only if the formers exist
        if "Property" in element_counting:
            set_class_attribute_property(class_dict, ontouml_graph)

        # Treats relations between instances of Class and Literal only if the formers exist
        if "Literal" in element_counting:
            set_class_literal_literal(class_dict, ontouml_graph)
