""" Functions to decode objects of type Class.
Functions to set object properties are named according to the nomenclature: set_<subject>_<predicate>_<object>.
"""

import inspect

from rdflib import Graph, URIRef, XSD, Literal, RDF

from globals import URI_ONTOLOGY, URI_ONTOUML
from modules.decoder.decode_general import get_list_subdictionaries_for_specific_type
from modules.errors import report_error_end_of_switch
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def get_stereotype(class_dict: dict) -> str:
    """ For coding reasons (dictionary index error), it is necessary to check if a class has its stereotype not set.
    Returns the evaluated class's stereotype or 'null' when the stereotype is absent.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :return: Evaluated class's stereotype or 'null' when the stereotype is absent.
    :rtype: str
    """

    if "stereotype" not in class_dict:
        result_stereotype = "null"
    else:
        result_stereotype = class_dict["stereotype"]

    return result_stereotype


def set_class_order(class_dict: dict, ontouml_graph: Graph) -> None:
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


def set_class_stereotypes(class_dict: dict, ontouml_graph: Graph) -> None:
    """ Sets ontouml:stereotype relation between a class and an instance representing an ontouml stereotype.

    :param class_dict: Class object loaded as a dictionary.
    :type class_dict: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    ENUM_CLASS_STEREOTYPE = ["type", "historicalRole", "historicalRoleMixin", "event", "situation", "category", "mixin",
                             "roleMixin", "phaseMixin", "kind", "collective", "quantity", "relator", "quality", "mode",
                             "subkind", "role", "phase", "enumeration", "datatype", "abstract"]

    class_stereotype = get_stereotype(class_dict)

    # Verifying for non declared stereotypes. If not declared, point to ClassStereotype and report warning.
    if class_stereotype == "null":

        LOGGER.warning(f"Stereotype not defined for class {class_dict['name']}.")

        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "stereotype"),
                           URIRef(URI_ONTOUML + "ClassStereotype")))

    else:
        ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                           URIRef(URI_ONTOUML + "stereotype"),
                           URIRef(URI_ONTOUML + class_dict['stereotype'])))

        # Adding information that an ontouml:Class is an ontouml:CollectiveClass
        if class_stereotype == "collective":
            ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                               URIRef(RDF.type),
                               URIRef(URI_ONTOUML + "CollectiveClass")))

        # If declared but invalid, create and report error
        elif class_stereotype not in ENUM_CLASS_STEREOTYPE:
            LOGGER.error(f"Invalid stereotype {class_dict['stereotype']} defined for class {class_dict['name']}. "
                         f"The transformation output is not syntactically valid.")


def set_class_restricted_to(class_dict: dict, ontouml_graph: Graph) -> None:
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
    """ Creates the isPowertype and isExtensional attribute of a class in the resulting graph.

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

    warning_not_type = f"The class '{class_dict['name']}' had its order attribute (originally 'null') set to 1 " \
                       f"(default to classes with stereotype different than 'type')."

    # DEFAULT: ORDER VALUE
    if "order" not in class_dict:

        # Default: order default value = 1 when stereotype is not 'type'
        if (class_stereotype == "null") or (class_stereotype != 'type'):
            LOGGER.warning(warning_not_type)
            ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                               URIRef(URI_ONTOUML + "order"),
                               Literal(1, datatype=XSD.nonNegativeInteger)))

        # Default: order default value = 2 when stereotype is 'type'
        elif class_stereotype == 'type':
            LOGGER.warning(
                f"The class {class_dict['name']} had its 'order' attribute (originally null) set to 2 "
                f"(default to classes with stereotype 'type').")
            ontouml_graph.add((URIRef(URI_ONTOLOGY + class_dict['id']),
                               URIRef(URI_ONTOUML + "order"),
                               Literal(2, datatype=XSD.nonNegativeInteger)))

        # Unexpected value received for class_stereotype
        else:
            current_function = inspect.stack()[0][3]
            report_error_end_of_switch("class_stereotype", current_function)

    # DEFAULT: ISPOWERTYPE DEFAULT VALUE = FALSE
    if "isPowertype" not in class_dict:
        LOGGER.warning(
            f"The class {class_dict['name']} had its 'isPowertype' attribute (originally null) set to False (default).")
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

    # Constraint A: isExtensional must be null when the class's stereotype is not 'collective'
    if ("isExtensional" in class_dict) and class_stereotype != "collective":
        LOGGER.warning(
            f"Class '{class_dict['name']}' of stereotype '{class_stereotype}' had its isExtensional "
            f"attribute (originally '{class_dict['isExtensional']}') removed as it is not of stereotype collective.")
        class_dict.pop('isExtensional')

    # Constraints B and C depend on the existence of the order attribute
    if "order" in class_dict:

        # Constraint B: order must be greater than 1 when the class's stereotype is 'type'
        if class_stereotype == "type" and ((class_dict["order"] == 1) or (class_dict["order"] == "1")):
            LOGGER.warning(f"Class '{class_dict['name']}' of stereotype '{class_stereotype}' had its order attribute "
                           f"(originally '{class_dict['order']}') set to '2' (default for 'type').")
            class_dict.pop('order')

        # Constraint C: class's order must be 1 when class's stereotype is not 'type'
        if class_stereotype != "type" and class_dict["order"] != 1:
            LOGGER.warning(
                f"Class '{class_dict['name']}' of stereotype '{class_stereotype}' had its order attribute "
                f"(originally '{class_dict['order']}') set to '1' as it is not a 'type').")
            class_dict.pop('order')

    # Constraint D: class must have stereotype 'type' when no stereotype and when its isPowertype attribute is true
    if "isPowertype" in class_dict:
        if class_dict["isPowertype"] and class_stereotype == "null":
            LOGGER.warning(
                f"Class '{class_dict['name']}' had its stereotype (originally unknown) set 'type' as its isPowertype "
                f"attribute is 'True'.")
            class_dict['stereotype'] = "type"

    # Constraint E: class's isPowertype must be false when class's stereotype is not ('type' or undefined)
    if "isPowertype" in class_dict:
        if class_dict["isPowertype"] and not (class_stereotype == "type" or class_stereotype == "null"):
            LOGGER.warning(
                f"Class '{class_dict['name']}' of stereotype '{class_stereotype}' had its isPowertype "
                f"attribute (originally '{class_dict['isPowertype']}') set to 1 as it is not of stereotype type.")
            class_dict['isPowertype'] = False


def create_class_properties(json_data: dict, ontouml_graph: Graph) -> None:
    """ Main function for decoding an object of type 'Class'.

    Receives the whole JSON loaded data as a dictionary and manipulates it to create all properties in which the
    object's type is domain of.

    Created properties:
        - ontouml:order (range xsd:nonNegativeInteger)
        - ontouml:stereotype (range ontouml:Stereotype)
        - ontouml:restrictedTo (range ontouml:OntologicalNature)
        - ontouml:isPowertype (range xsd:boolean)
        - ontouml:isExtensional (range xsd:boolean)

    Dictionaries containing classes IDs are used for reference. One of its characteristics is that they do not have the
    field 'name'. These are not Classes dictionaries and, hence, are not treated here.

    :param json_data: JSON's data to have its fields decoded loaded into a dictionary.
    :type json_data: dict
    :param ontouml_graph: Knowledge graph that complies with the OntoUML Vocabulary.
    :type ontouml_graph: Graph
    """

    # Get all class' dictionaries
    list_all_class_dicts = get_list_subdictionaries_for_specific_type(json_data, "Class")

    # Treat each Rectangle
    for class_dict in list_all_class_dicts:

        # Skipping dictionaries that refer to classes
        if "name" not in class_dict:
            continue

        # Validating default values
        validate_class_constraints(class_dict)
        set_class_order(class_dict, ontouml_graph)
        set_class_stereotypes(class_dict, ontouml_graph)
        set_class_restricted_to(class_dict, ontouml_graph)
        set_class_defaults(class_dict, ontouml_graph)
        set_class_attributes(class_dict, ontouml_graph)
