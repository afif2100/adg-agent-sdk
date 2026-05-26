"""Tests for scaffold logic."""

import json
import tempfile
from pathlib import Path

from adg_agent_sdk.scaffold import Scaffolder


class TestScaffolder:
    """Integration tests for the Scaffolder."""

    def _run_scaffold(
        self,
        project_name: str = "test-project",
        package_name: str | None = None,
        **kwargs,
    ) -> Path:
        """Run the scaffolder in a temp directory and return the output path."""
        tmpdir = Path(tempfile.mkdtemp())
        output = tmpdir / project_name

        if package_name is None:
            from adg_agent_sdk.name_utils import project_name_to_package
            package_name = project_name_to_package(project_name)

        s = Scaffolder(
            project_name=project_name,
            package_name=package_name,
            output_dir=output,
            init_git=False,
            init_venv=False,
            force=True,
            dry_run=False,
            **kwargs,
        )
        s.run()
        return output

    def test_core_files_created(self) -> None:
        """The core scaffold should create essential project files."""
        output = self._run_scaffold()
        files = {f.relative_to(output).as_posix() for f in output.rglob("*") if f.is_file()}

        assert "pyproject.toml" in files, f"Missing pyproject.toml. Files: {files}"
        assert "README.md" in files
        assert ".gitignore" in files
        assert ".env.example" in files
        assert ".adg-sdk" in files
        assert "src/test_project/__init__.py" in files
        assert "src/test_project/app.py" in files
        assert "src/test_project/config/__init__.py" in files
        assert "src/test_project/config/settings.py" in files
        assert "tests/__init__.py" in files

    def test_pyproject_toml_content(self) -> None:
        """pyproject.toml should reference the project name."""
        output = self._run_scaffold()
        content = (output / "pyproject.toml").read_text()
        assert "test-project" in content

    def test_adg_sdk_marker(self) -> None:
        """.adg-sdk marker should contain version info."""
        output = self._run_scaffold()
        marker = json.loads((output / ".adg-sdk").read_text())
        assert marker["project_name"] == "test-project"
        assert marker["package_name"] == "test_project"
        assert "adg_sdk_version" in marker
        assert "created_at" in marker

    def test_example_code_included_by_default(self) -> None:
        """With --example-code (default), agent/tool/workflow dirs should exist."""
        output = self._run_scaffold()
        assert (output / "src/test_project/agents/__init__.py").exists()
        assert (output / "src/test_project/tools/__init__.py").exists()
        assert (output / "src/test_project/workflows/__init__.py").exists()
        assert (output / "src/test_project/agents/hello_agent.py").exists()
        assert (output / "src/test_project/tools/example_tool.py").exists()
        assert (output / "src/test_project/workflows/main_workflow.py").exists()

    def test_no_example_code(self) -> None:
        """Without --example-code, agent/tool/workflow dirs should NOT exist."""
        output = self._run_scaffold(include_example_code=False)
        assert not (output / "src/test_project/agents/__init__.py").exists()
        assert not (output / "src/test_project/tools/__init__.py").exists()
        assert not (output / "src/test_project/workflows/__init__.py").exists()

    def test_docker_flag(self) -> None:
        """--docker should create Dockerfile and docker-compose.yml."""
        output = self._run_scaffold(include_docker=True)
        assert (output / "Dockerfile").exists()
        assert (output / "docker-compose.yml").exists()

    def test_ci_flag(self) -> None:
        """--ci should create GitHub Actions CI workflow."""
        output = self._run_scaffold(include_ci=True)
        ci_path = output / ".github/workflows/ci.yml"
        assert ci_path.exists(), f"Missing CI workflow. Contents: {list(output.rglob('*'))}"

    def test_docker_and_ci(self) -> None:
        """--docker and --ci should work together."""
        output = self._run_scaffold(include_docker=True, include_ci=True)
        assert (output / "Dockerfile").exists()
        assert (output / "docker-compose.yml").exists()
        assert (output / ".github/workflows/ci.yml").exists()

    def test_package_name_substitution_in_code(self) -> None:
        """Python files should reference the correct package name."""
        output = self._run_scaffold(project_name="custom-app", package_name="custom_app")
        init_content = (output / "src/custom_app/__init__.py").read_text()
        assert "custom_app" in init_content

        # Example workflow imports (when --example-code is default)
        workflow = (output / "src/custom_app/workflows/main_workflow.py").read_text()
        assert "custom_app" in workflow
        assert "custom_app.agents.hello_agent" in workflow

    def test_dry_run_does_not_write(self) -> None:
        """Dry-run should not create any files or directories."""
        tmpdir = Path(tempfile.mkdtemp())
        output = tmpdir / "dry-test"

        s = Scaffolder(
            project_name="dry-test",
            package_name="dry_test",
            output_dir=output,
            force=True,
            dry_run=True,
            init_git=False,
            init_venv=False,
        )
        s.run()

        # The output directory itself should not exist after dry-run
        assert not output.exists(), f"Expected {output} not to exist"
        # The parent should still exist
        assert tmpdir.exists()
