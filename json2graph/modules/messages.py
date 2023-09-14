""" Decoding messages to be displayed to users must be concentrated in this module whenever possibile. """
import inspect

from . import arguments as args
from .errors import report_error_end_of_switch
from .logger import initialize_logger
from ..decoder.decode_general import get_stereotype

LOGGER = initialize_logger()


def get_decode_log_message(
    object_dict: dict,
    warning_code: str,
    property_name: str,
    att_valid_stereotype: str = "",
) -> str:
    """Mounts and returns a warning message according to the information received as parameter.

    :param object_dict: Object's JSON data loaded as a dictionary.
    :type object_dict: dict
    :param warning_code: Code used to select the correct message to be displayed to the user if not in silent mode.
    :type warning_code: str
    :param property_name: Information about a property or attribute type to be displayed in a warning message. Optional.
    :type property_name: str
    :param att_valid_stereotype: Stereotype associated to an attribute to be displayed in a warning message. Optional.
    :type att_valid_stereotype: str
    :return: Warning message containing information about the modification made to be printed to user.
    :rtype: str
    """

    message = "NOT DEFINED MESSAGE"

    # All cases require
    object_type = object_dict["type"]
    object_id = object_dict["id"]

    # Not for VPS1
    if warning_code != "VPS1":
        object_stereotype = get_stereotype(object_dict)
        object_name = object_dict["name"] if "name" in object_dict else "null"
        object_identification = f"{object_type} '{object_name}' (stereotype: {object_stereotype}, ID: {object_id}): "

    # Not for VPS1, VPS2, and VPS3
    if "VPS" not in warning_code:
        att_value = object_dict[property_name] if property_name in object_dict else "null"

    # Warnings generated in function decode_obj_class.validate_class_attribute_constraints

    if warning_code == "VCA1":
        message = (
            "a class cannot have at the same time value 'True' for 'isPowertype' (allowed only for 'type' "
            "stereotype) and value different than 'null' for 'isExtensional' (allowed only for 'collective'). "
            "The transformation output is semantically INVALID."
        )

    elif warning_code == "VCA2":
        message = (
            f"stereotype (originally 'null') set to '{att_valid_stereotype}' as it contains the "
            f"related attribute '{property_name}' (with value '{object_dict[property_name]}') "
            f"that is only allowed in classes with this stereotype."
        )

    elif warning_code == "VCA3a":
        message = (
            f"attribute '{property_name}' (originally '{att_value}') removed as 'isExtensional' is only "
            f"allowed to be not 'null' in classes with stereotype '{att_valid_stereotype}'."
        )

    elif warning_code == "VCA3b":
        message = (
            f"attribute '{property_name}' (originally '{att_value}') set to 'False' "
            f"as 'isPowertype' can only have value 'True' in classes with stereotype '{att_valid_stereotype}'."
        )

    # Warnings generated in function decode_obj_class.set_defaults_class_order

    elif warning_code == "DCO1":
        message = (
            f"attribute '{property_name}' (originally '{att_value}') set to '1', "
            f"the default value to classes with stereotype different than 'type'."
        )

    elif warning_code == "DCO2":
        message = (
            f"attribute '{property_name}' (originally '{att_value}') set to '2', "
            f"the default value to classes with stereotype 'type'."
        )

    # Warnings generated in function decode_obj_class.set_defaults_class_attribute

    elif warning_code == "DCA1":
        message = (
            f"attribute '{property_name}' (originally '{att_value}') set to 'False', "
            f"the default value to classes with stereotype '{att_valid_stereotype}'."
        )

    # Warnings for  CLASS.set_defaults_class_attribute, RELATION.set_relation_defaults,
    #               PROPERTY.set_property_defaults, and GENERALIZATION_SET.set_generalizationset_defaults

    elif warning_code == "DGA1":
        message = f"attribute '{property_name}' (originally '{att_value}') set to its default value: 'False'."

    # Warnings generated in function decode_obj_class.set_class_stereotype

    elif warning_code == "VCS1":
        message = (
            f"mandatory '{property_name}' is missing. To be syntactically valid, every Class in an "
            f"ontology must have an stereotype relation with a ClassStereotype."
        )

    # Warnings for CLASS.set_class_stereotype, and RELATION.set_relation_stereotype

    elif warning_code == "VCSG":
        message = (
            f"invalid stereotype assigned. A valid {object_type} stereotype must be an instance of the "
            f"enumeration class {object_type}Stereotype. The transformation output is syntactically INVALID."
        )

    # Warnings for PROPERTY.validate_property_stereotype
    # This is a specific case, as the validation of properties are performed using the Graph's information

    elif warning_code == "VPS1":
        object_identification = f"{object_type} (ID: {object_id}): "
        message = (
            "invalid stereotype assigned. A valid Property stereotype must be an instance of the "
            "enumeration class PropertyStereotype. The transformation output is syntactically INVALID."
        )

    elif warning_code == "VPS2":
        message = (
            f"contains a property (ID: '{object_dict['propID']}') with stereotype '{object_dict['propID']}'. "
            f"Only classes of type 'event' can be associated to stereotyped properties."
        )

    elif warning_code == "VPS3":
        message = (
            f"stereotype (originally 'null') set to 'event', as this class contains a property "
            f"(ID: '{object_dict['propID']}') with stereotype (value '{object_dict['propID']}') that can only "
            f"happen associated to 'event' classes."
        )

    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("warning_number", current_function)

    return object_identification + message


def print_decode_log_message(
    object_dict: dict,
    warning_code: str,
    property_name: str = "",
    att_valid_stereotype: str = "",
) -> None:
    """Gets warning message and prints it to the user as a log if not in silent mode.

    :param object_dict: Object's JSON data loaded as a dictionary.
    :type object_dict: dict
    :param warning_code: Predefined warning number to be displayed to the user if not in silent mode.
    :type warning_code: str
    :param property_name: Information about a property or attribute type to be displayed in a warning message. Optional.
    :type property_name: str
    :param att_valid_stereotype: Optional attribute's stereotype to be displayed in a warning message.
    :type att_valid_stereotype: str
    """

    # If in silent mode, exit function and do not print anything
    if args.ARGUMENTS["silent"]:
        return

    log_message = get_decode_log_message(object_dict, warning_code, property_name, att_valid_stereotype)
    LOGGER.warning(log_message)
