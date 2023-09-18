"""This module provides functionality for various tasks related to a software project. \
It includes functions for running tests, checking package versions, and running Poetry commands. \
The module also uses a logging system for better error and information handling.

Usage:
    This module can be executed as a script to perform a series of tasks related to a software project, including
    testing, version checking, and command execution.
"""

import os
import subprocess

import requests
import tomli

from json2graph.modules.logger import initialize_logger

LOGGER = initialize_logger()


def run_tests() -> None:
    """
    Run custom tests using pytest.

    This function runs custom-defined tests using the pytest framework.
    It executes the pytest command on a specified test file and logs the results.
    """
    LOGGER.info(
        "Running own-defined tests using pytest.\nExecuting command: 'pytest .\\json2graph\\tests\\test_main.py'"
    )

    # Path to the test file
    test_file_path = os.path.join("json2graph", "tests", "test_main.py")

    # Construct the command
    command = ["pytest", test_file_path]

    try:
        # Run the command
        subprocess.run(command, check=True)
        LOGGER.info("Tests concluded with success. Proceeding to the next step.\n")
    except subprocess.CalledProcessError as e:
        LOGGER.error(f"Test failed with return code {e.returncode}: {e.cmd}")
        exit(1)
    except FileNotFoundError:
        LOGGER.error("pytest command not found. Please make sure pytest is installed.")
        exit(1)


def get_latest_package_version() -> str:
    """
    Get the latest version of a package from PyPI.

    This function fetches the latest version of a specified package from PyPI
    by making an HTTP GET request to the PyPI JSON API.

    :return: The latest version of a package from PyPI
    :rtype: str
    """
    package_name = "ontouml-json2graph"

    # Create the URL for the PyPI JSON API
    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        # Send an HTTP GET request to the PyPI API
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()
            # Extract the latest version from the response
            latest_version = data["info"]["version"]
            LOGGER.info(f"The latest version of {package_name} is {latest_version}")
            return latest_version
        else:
            LOGGER.error(f"Failed to fetch data. Status code: {response.status_code}")
            exit(1)
    except requests.exceptions.RequestException as e:
        LOGGER.error(f"An error occurred: {e}")
        exit(1)


def get_current_package_version() -> str:
    """
    Get the current version of a package from 'pyproject.toml'.

    This function reads the 'pyproject.toml' file and extracts the version
    information from the 'tool.poetry.version' section.

    :return: The current version of a package from PyPI
    :rtype: str
    """
    pyproject_path = "pyproject.toml"

    if not os.path.isfile(pyproject_path):
        LOGGER.error(f"pyproject.toml not found at {pyproject_path}.")
        exit(1)

    try:
        with open(pyproject_path, "rb") as toml_file:  # Open the file in binary mode
            toml_data = tomli.load(toml_file)
            # Extract the version from the pyproject.toml file
            version = toml_data.get("tool", {}).get("poetry", {}).get("version")
            LOGGER.info(f"The version in pyproject.toml is: {version}")
            return version
    except (FileNotFoundError, tomli.TOMLDecodeError) as e:
        LOGGER.error(f"An error occurred while reading the pyproject.toml file: {e}")
        exit(1)


def check_versions(published_version: str, current_version: str) -> None:
    """Check if published and current versions of a package are equal.

    This function compares two versions and logs whether they are the same or different.
    If the versions are the same, it indicates a problem and exits the program.


    :param published_version: The published version of the package.
    :type published_version: str
    :param current_version: The current version of the package.
    :type current_version: str
    """
    if published_version == current_version:
        LOGGER.error("The published version and current version are the same.")
        LOGGER.error("There's a problem. The software cannot proceed.")
        exit(1)
    else:
        LOGGER.info("The published version and current version are different.")
        LOGGER.info("It's okay. The software can proceed.")


def run_poetry_commands() -> None:
    """
    Run a series of Poetry commands.

    This function runs a series of Poetry commands, including 'export', 'check', and 'build'.
    It logs the execution of each command and exits the program if any command fails.
    """
    # Commands to run
    commands = [
        ["poetry", "export", "-f", "requirements.txt", "--output", "requirements.txt", "--dev"],
        ["poetry", "check"],
        ["poetry", "build"],
    ]

    for command in commands:
        try:
            # Run the command
            subprocess.run(command, check=True)
            LOGGER.info(f"Command '{' '.join(command)}' successfully executed!")
        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Command '{' '.join(command)}' failed with return code {e.returncode}")
            exit(1)
        except FileNotFoundError:
            LOGGER.error(f"'{' '.join(command)}' command not found. Please make sure Poetry is installed.")
            exit(1)


def execute_documentation_commands():
    """
    Execute a sequence of documentation-related commands.

    This function executes the following commands sequentially:
    1. Clean the Sphinx documentation build.
    2. Build the Sphinx HTML documentation.
    3. Remove the 'docs' directory and its contents.
    4. Create a new 'docs' directory.
    5. Copy the HTML documentation to the 'docs' directory.
    6. Clean the Sphinx documentation build again.

    If any command fails, the function raises an exception and stops the execution.
    """
    # Define the base directory
    base_dir = os.getcwd()  # Use the current working directory

    # Define paths to directories and commands
    sphinx_dir = os.path.join(base_dir, "sphinx")
    docs_dir = os.path.join(base_dir, "docs")

    # Command list
    commands = [
        ["make", "clean"],
        ["make", "html"],
        ["rmdir", docs_dir, "/s", "/q"],
        ["mkdir", docs_dir],
        ["xcopy", os.path.join(sphinx_dir, "_build", "html"), docs_dir, "/E", "/H"],
        ["make", "clean"],
    ]

    # Execute commands sequentially
    for command in commands:
        try:
            subprocess.run(command, cwd=sphinx_dir, shell=True, check=True)
            LOGGER.info(f"Command successfully executed: {' '.join(command)}")
        except subprocess.CalledProcessError as e:
            LOGGER.error(f"Command failed with return code {e.returncode}: {e.cmd}")
            exit(1)
        except Exception as e:
            LOGGER.error(f"An error occurred: {e}")
            exit(1)

    LOGGER.info("Documentation commands executed successfully.")


if __name__ == "__main__":
    """This block serves as the main entry point when the script is executed directly.
    It orchestrates the execution of various tasks related to a software project, including testing, version checking,
    and running Poetry commands.
    """
    LOGGER.info("Building a new package")
    run_tests()
    version_before = get_latest_package_version()
    version_after = get_current_package_version()
    check_versions(version_before, version_after)
    run_poetry_commands()
    execute_documentation_commands()
