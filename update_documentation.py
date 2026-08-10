"""Build the project's Sphinx documentation."""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from json2graph.modules.logger import initialize_logger

LOGGER = initialize_logger()


def execute_documentation_commands() -> None:
    """Build the Sphinx documentation strictly and replace its local HTML output after success."""
    base_dir = Path(__file__).resolve().parent
    source_dir = base_dir / "docs"
    output_dir = source_dir / "_build" / "html"

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
                str(source_dir),
                str(build_dir),
                "-W",
                "--keep-going",
                "-n",
            ],
            cwd=base_dir,
            check=True,
        )

        built_html_dir = build_dir / "html"
        if not built_html_dir.is_dir():
            raise FileNotFoundError(f"Sphinx did not create the expected HTML directory: {built_html_dir}")

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(built_html_dir, output_dir)

    LOGGER.info(f"Documentation successfully generated at '{output_dir}'.")


if __name__ == "__main__":
    execute_documentation_commands()
