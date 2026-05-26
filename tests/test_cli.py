"""Tests for the CLI entry point — uses Typer's CliRunner."""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from adg_agent_sdk.cli import app

runner = CliRunner()


class TestCliVersion:
    """adg-sdk --version and -V."""

    def test_version_long(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "adg-sdk version" in result.stdout

    def test_version_short(self) -> None:
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert "adg-sdk version" in result.stdout

    def test_no_args_shows_help(self) -> None:
        """No args should show help."""
        result = runner.invoke(app, [])
        # CliRunner may return 0 or 2 for help display
        assert result.exit_code in (0, 2), f"exit: {result.exit_code}"
        assert "Usage:" in result.stdout
        assert "Commands" in result.stdout


class TestCliInit:
    """adg-sdk init <project>."""

    def test_init_basic(self) -> None:
        """Basic init creates core files."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "my-app"
            result = runner.invoke(app, ["init", "my-app", "--dir", str(target)])
            assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.stdout}"
            assert target.exists()
            assert (target / "pyproject.toml").exists()
            assert (target / "AGENTS.md").exists()
            assert (target / ".adg-sdk").exists()
            marker = json.loads((target / ".adg-sdk").read_text())
            assert marker["project_name"] == "my-app"

    def test_init_with_docker_ci(self) -> None:
        """Init with --docker and --ci flags."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "docker-ci-app"
            result = runner.invoke(
                app,
                ["init", "docker-ci-app", "--dir", str(target), "--docker", "--ci", "--no-git"],
            )
            assert result.exit_code == 0, result.stdout
            assert (target / "Dockerfile").exists()
            assert (target / "docker-compose.yml").exists()
            assert (target / ".github/workflows/ci.yml").exists()

    def test_init_no_example_code(self) -> None:
        """Init with --no-example-code skips example dirs."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "minimal"
            result = runner.invoke(
                app,
                ["init", "minimal", "--dir", str(target), "--no-example-code", "--no-git"],
            )
            assert result.exit_code == 0, result.stdout
            # Core files still present
            assert (target / "pyproject.toml").exists()
            # No example code
            assert not (target / "src/minimal/agents").exists()

    def test_init_dry_run(self) -> None:
        """Dry-run does not create files."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "dry"
            result = runner.invoke(
                app,
                ["init", "dry", "--dir", str(target), "--dry-run"],
            )
            assert result.exit_code == 0, result.stdout
            assert "Dry-run complete" in result.stdout
            # Should have no files or dirs created
            assert not target.exists()

    def test_init_stack_fe(self) -> None:
        """Init with --stack fe creates frontend project."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fe-app"
            result = runner.invoke(
                app,
                ["init", "fe-app", "--dir", str(target), "--stack", "fe", "--no-git"],
            )
            assert result.exit_code == 0, result.stdout
            assert (target / "package.json").exists()
            assert (target / "index.html").exists()
            assert not (target / "pyproject.toml").exists()

    def test_init_stack_fe_plus_be(self) -> None:
        """Init with --stack fe+be creates backend/ and frontend/."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fullstack"
            result = runner.invoke(
                app,
                ["init", "fullstack", "--dir", str(target), "--stack", "fe+be", "--no-git"],
            )
            assert result.exit_code == 0, result.stdout
            assert (target / "backend/pyproject.toml").exists()
            assert (target / "frontend/package.json").exists()
            assert (target / "README.md").exists()

    def test_init_invalid_stack(self) -> None:
        """Invalid stack should exit with error."""
        result = runner.invoke(app, ["init", "bad-stack", "--stack", "invalid"])
        assert result.exit_code == 1
        assert "Invalid stack" in result.stderr

    def test_init_force_overwrite(self) -> None:
        """--force should overwrite existing directory."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "overwrite-me"
            target.mkdir()
            (target / "old-file.txt").touch()

            result = runner.invoke(
                app,
                ["init", "overwrite-me", "--dir", str(target), "--force", "--no-git"],
            )
            assert result.exit_code == 0, result.stdout
            # Old file should be gone, new files present
            assert not (target / "old-file.txt").exists()
            assert (target / "pyproject.toml").exists()


class TestCliStart:
    """adg-sdk start — interactive prompt command."""

    def test_start_basic(self) -> None:
        """Start with basic answers scaffolds a project."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "interactive-app"
            # 7 inputs: name, stack, docker, ci, example, git, venv
            result = runner.invoke(
                app,
                ["start", "--dir", str(target)],
                input="interactive-app\nbe\nn\nn\ny\nn\nn\n",
            )
            assert result.exit_code == 0, f"Exit {result.exit_code}: {result.stdout}"
            assert target.exists()
            assert (target / "AGENTS.md").exists()
            assert (target / "pyproject.toml").exists()

    def test_start_empty_name_aborts(self) -> None:
        """Empty project name on the first prompt should abort."""
        result = runner.invoke(app, ["start"], input="\n")
        assert result.exit_code == 1
        assert "Aborted" in result.stderr

    def test_start_dry_run(self) -> None:
        """Start with dry-run should not create files."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "dry-start"
            # 7 inputs: name, stack, docker, ci, example, git, venv
            result = runner.invoke(
                app,
                ["start", "--dir", str(target), "--dry-run"],
                input="dry-start\nbe\nn\nn\ny\nn\nn\n",
            )
            assert result.exit_code == 0, f"Exit {result.exit_code}: {result.stdout}"
            assert "Dry-run complete" in result.stdout
            assert not target.exists()

    def test_start_fe_stack(self) -> None:
        """Start with fe stack skips example code prompt and venv."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "fe-start"
            # 6 inputs: name, stack, docker, ci, git, venv (no example prompt for fe)
            result = runner.invoke(
                app,
                ["start", "--dir", str(target), "--dry-run"],
                input="fe-start\nfe\nn\nn\nn\nn\n",
            )
            assert result.exit_code == 0, f"Exit {result.exit_code}: {result.stdout}"
            assert "Dry-run complete" in result.stdout

    def test_start_fullstack(self) -> None:
        """Start with fe+be creates backend/ and frontend/."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "full-start"
            # 7 inputs: name, stack, docker, ci, example, git, venv
            result = runner.invoke(
                app,
                ["start", "--dir", str(target), "--dry-run"],
                input="full-start\nfe+be\nn\nn\ny\nn\nn\n",
            )
            assert result.exit_code == 0, f"Exit {result.exit_code}: {result.stdout}"
            assert "backend" in result.stdout
            assert "frontend" in result.stdout
