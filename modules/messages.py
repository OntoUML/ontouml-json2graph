""" Decoding messages to be displayed to users must be concentrated in this module whenever possibile. """
import inspect

import modules.arguments as args
from modules.decoder.decode_general import get_stereotype
from modules.errors import report_error_end_of_switch
from modules.logger import initialize_logger

LOGGER = initialize_logger()


def get_decode_log_message(object_dict: dict, warning_code: str, attribute: str, att_valid_stereotype: str = "") -> str:
    """ Mounts and returns a warning message according to the information received as parameter.

    :param object_dict: Object's JSON data loaded as a dictionary.
    :type object_dict: dict
    :param warning_code: Code used to select the correct message to be displayed to the user if not in silent mode.
    :type warning_code: str
    :param attribute: Information about an attribute type to be displayed in a warning message. Optional.
    :type attribute: str
    :param att_valid_stereotype: Stereotype associated to an attribute to be displayed in a warning message. Optional.
    :type att_valid_stereotype: str
    :return: Warning message containing information about the modification made to be printed to user.
    :rtype: str
    """

    if "stereotype" in object_dict:
        object_stereotype = get_stereotype(object_dict)
        msg_stereotype = f"<<{object_stereotype}>> "
    else:
        msg_stereotype = ""

    object_identification = f"{object_dict['type']} '{object_dict['name']}' " + msg_stereotype + f"(ID: {object_dict['id']}): "

    message = "NOT DEFINED MESSAGE"
    att_value = object_dict[attribute] if attribute in object_dict else "null"

    if warning_code == "VCA1":
        message = "This class must not have values for both 'isExtensional' (allowed only for classes with " \
                  "stereotype 'collective') and 'isPowertype' (allowed only for 'type'). " \
                  "The transformation output is semantically INVALID."

    elif warning_code == "VCA2":
        message = f"stereotype (originally {object_stereotype}) set to '{att_valid_stereotype}' as it contains the " \
                  f"related attribute '{attribute}' (with value '{object_dict[attribute]}') that is only allowed in " \
                  f"classes with this stereotype."

    elif warning_code == "VCA3":
        message = f"attribute '{attribute}' (originally '{att_value}') removed " \
                  f"as this attribute is only allowed in classes with stereotype '{att_valid_stereotype}'."

    elif warning_code == "DCO1":
        message = f"attribute '{attribute}' (originally '{att_value}') set to '1', " \
                  f"the default value to classes with stereotype different than 'type'."

    elif warning_code == "DCO2":
        message = f"attribute '{attribute}' (originally '{att_value}') set to '2', " \
                  f"the default value to classes with stereotype 'type'."

    elif warning_code == "DCA1":
        message = f"attribute '{attribute}' (originally {att_value}) set to 'False', " \
                  f"the default value to classes with stereotype '{att_valid_stereotype}'."

    elif warning_code == "DGA1":
        message = f"attribute '{attribute}' (originally {att_value}) set to its default value: 'False'."

    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("warning_number", current_function)

    return object_identification + message


def print_decode_log_message(class_dict: dict, warning_code: str, attribute: str = "",
                             attribute_valid_stereotype: str = "", message_type: str = "warning") -> None:
    """ Gets warning message and prints it to the user as a log if not in silent mode.

    :param class_dict: Object's JSON data loaded as a dictionary.
    :type class_dict: dict
    :param warning_code: Predefined warning number to be displayed to the user if not in silent mode.
    :type warning_code: str
    :param attribute: Information about an attribute type to be displayed in a warning message. Optional.
    :type attribute: str
    :param attribute_valid_stereotype: Optional attribute's stereotype to be displayed in a warning message.
    :type attribute_valid_stereotype: str
    :param message_type: Logger's level. Default value is 'warning'. Accepted values are: 'warning', 'error'.
    :type message_type: str
    """

    # If in silent mode, exit function and do not print anything
    if args.ARGUMENTS["silent"]:
        return

    log_message = get_decode_log_message(class_dict, warning_code, attribute, attribute_valid_stereotype)

    if message_type == "warning":
        LOGGER.warning(log_message)
    elif message_type == "error":
        LOGGER.error(log_message)
    else:
        current_function = inspect.stack()[0][3]
        report_error_end_of_switch("message_type", current_function)
