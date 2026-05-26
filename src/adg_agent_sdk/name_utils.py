"""Project name normalization utilities."""

import re
from pathlib import Path


def normalize_project_name(name: str) -> str:
    """Normalize a user-provided name to a valid Python-safe project name.

    Rules:
    - Strip whitespace
    - Convert spaces/special chars to hyphens
    - Lowercase
    - Collapse multiple hyphens
    - Strip leading/trailing hyphens
    """
    name = name.strip()
    name = re.sub(r"[^a-zA-Z0-9_-]", "-", name)
    name = re.sub(r"[-_]+", "-", name)
    name = name.lower().strip("-")
    return name if name else "my-project"


def project_name_to_dir(name: str) -> str:
    """Return the directory name for a project (kebab-case)."""
    return normalize_project_name(name)


def project_name_to_package(name: str) -> str:
    """Return the Python package name (snake_case) for a project.

    Converts kebab-case to snake_case and strips non-Python-valid characters.
    """
    normalized = normalize_project_name(name)
    package = normalized.replace("-", "_")
    # Ensure it's a valid Python identifier
    package = re.sub(r"[^a-zA-Z0-9_]", "", package)
    if not package or not re.match(r"[a-zA-Z_]", package):
        package = "my_app"
    return package


def validate_package_name(package: str) -> str | None:
    """Validate a Python package name. Returns None if valid, error string if invalid."""
    if not package:
        return "Package name is empty."
    if not re.match(r"^[a-zA-Z_]", package):
        return f"Package name must start with a letter or underscore: '{package}'"
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", package):
        return (
            f"Package name contains invalid characters: '{package}' — "
            f"use only letters, digits, and underscores."
        )
    return None
