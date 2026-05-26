"""CLI entry point for adg-sdk — scaffold ADG-compliant projects."""

from pathlib import Path

import typer

from . import __version__
from .name_utils import normalize_project_name, project_name_to_package
from .scaffold import STACK_CHOICES, Scaffolder

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
    pass


@app.command()
def init(
    project_name: str = typer.Argument(
        ...,
        help="Name of the project (e.g. 'my-analytics-app')",
    ),
    stack: str = typer.Option(
        "be",
        "--stack",
        "-s",
        help="Project stack: be (backend), fe (frontend), or fe+be (fullstack)",
        show_choices=True,
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
        help="Include example agent, tool, and workflow code (backend only)",
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
    Group (ADG) standards. Use --stack to choose the project type.
    """
    if stack not in STACK_CHOICES:
        typer.echo(f"Invalid stack '{stack}'. Choose from: {', '.join(STACK_CHOICES)}", err=True)
        raise typer.Exit(1)

    normalized = normalize_project_name(project_name)
    package = project_name_to_package(project_name)
    output_dir = directory or Path.cwd() / normalized

    scaffolder = Scaffolder(
        project_name=normalized,
        package_name=package,
        output_dir=output_dir,
        stack=stack,
        include_example_code=example_code,
        include_docker=docker,
        include_ci=ci,
        init_git=git,
        init_venv=venv,
        force=force,
        dry_run=dry_run,
    )

    scaffolder.run()


@app.command()
def start(
    directory: Path = typer.Option(
        None,
        "--dir",
        "-d",
        help="Output directory (default: <project-name> in current directory)",
        file_okay=False,
        dir_okay=True,
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
    """Start a new project interactively.

    \b
    Prompts you for project details and scaffolds an ADG-compliant
    project based on your answers.
    """
    typer.echo(
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        "\n ADG SDK › Let's start a new project!"
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    # ── Ask questions ──────────────────────────────────────────
    project_name = typer.prompt("Project name")
    if not project_name:
        typer.echo("Project name is required.", err=True)
        raise typer.Exit(1)

    stack = typer.prompt(
        "Project stack",
        type=typer.Choice(list(STACK_CHOICES)),
        default="be",
        show_choices=True,
    )

    docker = typer.confirm("Include Docker?", default=False)
    ci = typer.confirm("Include CI workflow?", default=False)

    if stack in ("be", "fe+be"):
        example_code = typer.confirm("Include example agent/tool/workflow code?", default=True)
    else:
        example_code = False

    git = typer.confirm("Initialize git repository?", default=True)
    venv = typer.confirm("Create Python virtual environment?", default=True)

    # ── Scaffold ───────────────────────────────────────────────
    normalized = normalize_project_name(project_name)
    package = project_name_to_package(project_name)
    output_dir = directory or Path.cwd() / normalized

    scaffolder = Scaffolder(
        project_name=normalized,
        package_name=package,
        output_dir=output_dir,
        stack=stack,
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
