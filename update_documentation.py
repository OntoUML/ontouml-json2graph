"""Build and publish the project's Sphinx documentation."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from json2graph.modules.logger import initialize_logger

LOGGER = initialize_logger()


def execute_documentation_commands() -> None:
    """Build the Sphinx documentation and replace ``docs`` only after success."""
    base_dir = Path(__file__).resolve().parent
    sphinx_dir = base_dir / "sphinx"
    docs_dir = base_dir / "docs"

    with tempfile.TemporaryDirectory(prefix="ontouml-json2graph-docs-") as temporary_directory:
        build_dir = Path(temporary_directory) / "build"

        LOGGER.info(f"Building documentation with Python interpreter '{sys.executable}'.")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-M",
                "html",
                ".",
                str(build_dir),
            ],
            cwd=sphinx_dir,
            check=True,
        )

        built_html_dir = build_dir / "html"
        if not built_html_dir.is_dir():
            raise FileNotFoundError(f"Sphinx did not create the expected HTML directory: {built_html_dir}")

        if docs_dir.exists():
            shutil.rmtree(docs_dir)
        shutil.copytree(built_html_dir, docs_dir)

    LOGGER.info(f"Documentation successfully generated at '{docs_dir}'.")


if __name__ == "__main__":
    execute_documentation_commands()
