""" This Python module provides a simple script to remove all files with the ".ttl" extension from the
tests/results directory and then remove the directory itself.
"""

import os

dir_name = "results"

# Check if the specified directory exists
if os.path.exists(dir_name):

    # Retrieve a list of items (files and directories) in the specified directory
    test = os.listdir(dir_name)

    # Iterate through each item in the directory
    for item in test:
        if item.endswith(".ttl"):
            # If the item ends with ".ttl" extension, remove the file
            os.remove(os.path.join(dir_name, item))

    # Remove the directory itself after all .ttl files have been deleted
    os.rmdir(dir_name)
