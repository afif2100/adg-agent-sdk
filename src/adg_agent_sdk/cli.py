"""CLI entry point for adg-sdk — scaffold ADG-compliant projects."""

from pathlib import Path

import typer

from . import __version__
from .name_utils import normalize_project_name, project_name_to_package
from .scaffold import Scaffolder

app = typer.Typer(
    name="adg-sdk",
    help="Scaffold ADG (AI Development Group) compliant projects.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    """Callback that fires eagerly for --version / -V."""
    if value:
        typer.echo(f"adg-sdk version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show the SDK version and exit.",
        callback=_version_callback,
        is_eager=True,
        expose_value=False,
    ),
) -> None:
    """Scaffold ADG (AI Development Group) compliant projects."""
    pass  # All work is in subcommands


@app.command()
def init(
    project_name: str = typer.Argument(
        ...,
        help="Name of the project (e.g. 'my-analytics-app')",
    ),
    directory: Path = typer.Option(
        None,
        "--dir",
        "-d",
        help="Output directory (default: <project-name> in current directory)",
        file_okay=False,
        dir_okay=True,
    ),
    example_code: bool = typer.Option(
        True,
        "--example-code/--no-example-code",
        help="Include example agent, tool, and workflow code in the scaffold",
    ),
    docker: bool = typer.Option(
        False,
        "--docker",
        help="Add Dockerfile and docker-compose.yml",
    ),
    ci: bool = typer.Option(
        False,
        "--ci",
        help="Add GitHub Actions CI workflow",
    ),
    git: bool = typer.Option(
        True,
        "--git/--no-git",
        help="Initialize a git repository in the new project",
    ),
    venv: bool = typer.Option(
        True,
        "--venv/--no-venv",
        help="Create a virtual environment with uv",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing directory without prompting",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would be created without writing anything",
    ),
) -> None:
    """Create a new ADG-compliant project.

    \b
    This command scaffolds a directory tree with Python packaging,
    configuration, and optional example code following AI Development
    Group (ADG) standards.
    """
    normalized = normalize_project_name(project_name)
    package = project_name_to_package(project_name)
    output_dir = directory or Path.cwd() / normalized

    scaffolder = Scaffolder(
        project_name=normalized,
        package_name=package,
        output_dir=output_dir,
        include_example_code=example_code,
        include_docker=docker,
        include_ci=ci,
        init_git=git,
        init_venv=venv,
        force=force,
        dry_run=dry_run,
    )

    scaffolder.run()


def main_entry() -> None:
    app()
