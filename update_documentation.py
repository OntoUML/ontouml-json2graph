"""Build the project's Sphinx documentation."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from json2graph.modules.logger import initialize_logger

LOGGER = initialize_logger()

CLI_HELP_COLUMNS = 100
CLI_REFERENCE_RELATIVE_PATH = Path("docs") / "reference" / "cli-help.txt"


def render_cli_help(base_dir: Path | None = None) -> str:
    """Return deterministic help output from the current command-line parser."""
    repository_root = base_dir or Path(__file__).resolve().parent
    environment = os.environ.copy()
    environment["COLUMNS"] = str(CLI_HELP_COLUMNS)

    completed_process = subprocess.run(
        [sys.executable, "-m", "json2graph.decode", "--help"],
        cwd=repository_root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    return completed_process.stdout


def update_cli_reference(base_dir: Path | None = None) -> Path:
    """Write the checked-in CLI reference from the current parser help."""
    repository_root = base_dir or Path(__file__).resolve().parent
    output_file = repository_root / CLI_REFERENCE_RELATIVE_PATH
    rendered_help = render_cli_help(repository_root)

    if not output_file.is_file() or output_file.read_text(encoding="utf-8") != rendered_help:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(rendered_help, encoding="utf-8")

    return output_file


def execute_documentation_commands() -> None:
    """Build the Sphinx documentation strictly and replace its local HTML output after success."""
    base_dir = Path(__file__).resolve().parent
    source_dir = base_dir / "docs"
    output_dir = source_dir / "_build" / "html"

    cli_reference = update_cli_reference(base_dir)
    LOGGER.info(f"CLI reference updated at '{cli_reference}'.")

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
