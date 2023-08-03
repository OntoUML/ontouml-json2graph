import sys

sys.path.append('./json2graph')

from json2graph.modules.errors import report_error_io_read, report_error_io_write
import yaml
import toml

metadata_file_read = "pyproject.toml"
metadata_file_write = "json2graph/resources/metadata.yaml"

# Loads pyproject.toml file into a dictionary
try:
    metadata_dictionary = toml.load(metadata_file_read)
except IOError as error:
    file_description = "pyproject.toml file could not be found"
    report_error_io_read(metadata_file_read, file_description, error)

# Removes tool.poetry.packages
metadata_dictionary["tool"]["poetry"].pop("packages")

# Writes the dictionary with the pyproject.toml file as a yaml file inside the package's resource folder
try:
    with open(metadata_file_write, mode="w", encoding="utf-8") as file:
        yaml.dump(metadata_dictionary, file)
except IOError as error:
    file_description = "metadata file could not be saved into resource folder"
    report_error_io_write(metadata_file_write, file_description, error)

print("Metadata file sucessfully created.")
