"""Project scaffolding logic — renders templates and creates files."""

import json
import os
import shutil
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader

from . import __version__

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

STACK_CHOICES = ("be", "fe", "fe+be")
DEFAULT_STACK = ""


def _confirm_overwrite(path: Path) -> bool:
    """Prompt the user to overwrite an existing directory."""
    answer = typer.prompt(
        f"Directory '{path}' already exists. Overwrite?",
        default="n",
        type=str,
    )
    return answer.lower() in ("y", "yes")


def _run(cmd: list[str], cwd: Path | None = None, dry_run: bool = False) -> None:
    """Run a shell command, printing it first."""
    cwd_str = f" in {cwd}" if cwd else ""
    typer.echo(f"  ⚙️  {'[dry-run] would run:' if dry_run else 'running:'} {' '.join(cmd)}{cwd_str}")
    if not dry_run:
        try:
            subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            typer.echo(f"  ⚠️  Command failed (continuing): {e.stderr.strip()}", err=True)


class Scaffolder:
    """Orchestrates scaffolding a new ADG-compliant project."""

    def __init__(
        self,
        project_name: str,
        package_name: str,
        output_dir: Path,
        stack: str = DEFAULT_STACK,
        include_example_code: bool = True,
        include_docker: bool = False,
        include_ci: bool = False,
        init_git: bool = True,
        init_venv: bool = True,
        force: bool = False,
        dry_run: bool = False,
    ) -> None:
        self.project_name = project_name
        self.package_name = package_name
        self.output_dir = output_dir.resolve()
        self.stack = stack if stack in STACK_CHOICES else DEFAULT_STACK
        self.include_example_code = include_example_code
        self.include_docker = include_docker
        self.include_ci = include_ci
        self.init_git = init_git
        self.init_venv = init_venv
        self.force = force
        self.dry_run = dry_run

    # ── context ──────────────────────────────────────────────────────

    def _template_context(self) -> dict:
        """Return the Jinja2 template variables."""
        return {
            "project_name": self.project_name,
            "package_name": self.package_name,
            "project_dir": self.output_dir.name,
            "sdk_version": __version__,
            "python_version": ">=3.11",
            "year": date.today().year,
            "today": date.today().isoformat(),
            "stack": self.stack,
            "include_example_code": self.include_example_code,
            "include_docker": self.include_docker,
            "include_ci": self.include_ci,
        }

    # ── helpers ──────────────────────────────────────────────────────

    def _resolve_dest_path(self, rel_root: Path, fname: str, dest: Path) -> Path:
        """Resolve the destination path, substituting {{{package_name}}} where it appears."""
        parts = list(rel_root.parts)
        substituted = [
            p.replace("{{package_name}}", self.package_name)
            for p in parts
        ]
        out_name = fname
        if out_name.endswith(".jinja"):
            out_name = out_name[: -len(".jinja")]
        substituted.append(out_name)
        return dest / Path(*substituted)

    def _render_tree(self, template_dir: str, dest: Path, prefix: Path | None = None) -> None:
        """Render all Jinja2 templates and copy plain files from a template subtree.

        Directory names containing {{{package_name}}} are substituted with the
        actual package name at runtime.

        When *prefix* is set, files are placed under that subdirectory within *dest*.
        """
        src_dir = TEMPLATES_DIR / template_dir
        if not src_dir.is_dir():
            return

        local_env = Environment(
            loader=FileSystemLoader(str(src_dir)),
            autoescape=False,
        )

        for root, _dirs, files in os.walk(src_dir):
            rel_root = Path(root).relative_to(src_dir)
            for fname in files:
                output_root = dest / prefix if prefix else dest
                dest_path = self._resolve_dest_path(rel_root, fname, output_root)

                if self.dry_run:
                    typer.echo(f"  📄  {dest_path.relative_to(self.output_dir)}")
                    continue

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                src_file = Path(root) / fname

                if fname.endswith(".jinja"):
                    tmpl_rel = (rel_root / fname).as_posix()
                    content = local_env.get_template(tmpl_rel).render(**self._template_context())
                    dest_path.write_text(content, encoding="utf-8")
                else:
                    shutil.copy2(src_file, dest_path)
                typer.echo(f"  📄  {dest_path.relative_to(self.output_dir)}")

    # ── post-generation hooks ───────────────────────────────────────

    def _init_git_repo(self) -> None:
        """Initialize a git repository."""
        typer.echo("  ── git init ──")
        _run(["git", "init", "-b", "main"], cwd=self.output_dir, dry_run=self.dry_run)
        _run(["git", "add", "."], cwd=self.output_dir, dry_run=self.dry_run)

    def _create_venv(self) -> None:
        """Create a virtual environment using uv."""
        typer.echo("  ── uv venv ──")
        _run(["uv", "venv"], cwd=self.output_dir, dry_run=self.dry_run)

    # ── main entry point ─────────────────────────────────────────────

    def run(self) -> None:
        """Execute the full scaffold."""
        # ── preamble ─────────────────────────────────────────────
        stack_label = {"": "Minimal", "be": "Backend", "fe": "Frontend", "fe+be": "Fullstack (FE + BE)"}.get(self.stack, "Minimal")
        typer.echo(
            f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            f"\n ADG SDK › Creating project: {self.project_name}"
            f"\n           Stack: {stack_label}"
            f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )

        # When scaffolding into current directory, skip overwrite/rmtree
        is_cwd = self.output_dir == Path.cwd()
        if not is_cwd and self.output_dir.exists() and not self.force:
            if not _confirm_overwrite(self.output_dir):
                typer.echo("Aborted.")
                raise typer.Exit(0)
            if not self.dry_run:
                shutil.rmtree(self.output_dir)
        elif not is_cwd and self.output_dir.exists() and self.force and not self.dry_run:
            shutil.rmtree(self.output_dir)

        # ── render project templates ────────────────────────────
        label = "current directory" if is_cwd else str(self.output_dir)
        typer.echo(f"  Creating project files in {label}")

        # Root-level files always at project root
        self._render_tree("minimal/root", self.output_dir)

        # Backend stack: be or fe+be
        if self.stack in ("be", "fe+be"):
            be_prefix = Path("backend") if self.stack == "fe+be" else None
            self._render_tree("minimal/core", self.output_dir, prefix=be_prefix)
            if self.include_example_code:
                self._render_tree("minimal/example", self.output_dir, prefix=be_prefix)

        # Frontend stack: fe or fe+be
        if self.stack in ("fe", "fe+be"):
            fe_prefix = Path("frontend") if self.stack == "fe+be" else None
            self._render_tree("minimal/frontend", self.output_dir, prefix=fe_prefix)

        # Optional extras (always at project root unless stack is fe+be)
        if self.include_docker:
            self._render_tree("with-docker", self.output_dir)

        if self.include_ci:
            self._render_tree("with-ci", self.output_dir)

        # ── write .adg-sdk marker ───────────────────────────────
        marker = {
            "adg_sdk_version": __version__,
            "template_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "project_name": self.project_name,
            "package_name": self.package_name,
            "stack": self.stack,
        }
        if self.dry_run:
            typer.echo(f"  📄  .adg-sdk")
        else:
            (self.output_dir / ".adg-sdk").write_text(
                json.dumps(marker, indent=2) + "\n",
                encoding="utf-8",
            )
            typer.echo("  📄  .adg-sdk")

        # ── .claude directory ───────────────────────────────────
        claude_dirs = [
            self.output_dir / ".claude" / "rules",
            self.output_dir / ".claude" / "skills",
        ]
        for d in claude_dirs:
            if self.dry_run:
                typer.echo(f"  📄  {d.relative_to(self.output_dir)}/")
            else:
                d.mkdir(parents=True, exist_ok=True)
                gitkeep = d / ".gitkeep"
                gitkeep.write_text("")
                typer.echo(f"  📄  {gitkeep.relative_to(self.output_dir)}")

        # ── summary ─────────────────────────────────────────────
        if self.dry_run:
            typer.echo("\n  ✓ Dry-run complete.")
            return

        label = "current directory" if self.output_dir == Path.cwd() else str(self.output_dir)
        typer.echo(f"\n  ✓ Project scaffolded at: {label}")

        # ── post-gen hooks ──────────────────────────────────────
        if self.stack in ("be", "fe+be"):
            # Only init venv for Python-based stacks
            if self.init_venv:
                venv_dir = self.output_dir / "backend" if self.stack == "fe+be" else self.output_dir
                _run(["uv", "venv"], cwd=venv_dir, dry_run=self.dry_run)

        if self.init_git:
            self._init_git_repo()

        # ── next steps ──────────────────────────────────────────
        typer.echo(f"\n  Next steps:")
        if self.stack == "":
            typer.echo(f"    Start building your project!")
        elif self.stack == "fe":
            typer.echo(f"    npm install && npm run dev")
        elif self.stack == "fe+be":
            typer.echo(f"    # Backend:")
            typer.echo(f"    cd backend && source .venv/bin/activate")
            typer.echo(f"    # Frontend:")
            typer.echo(f"    cd frontend && npm install && npm run dev")
        elif self.stack == "be":
            if self.output_dir == Path.cwd():
                typer.echo(f"    source .venv/bin/activate")
            else:
                cd_dir = self.output_dir.name
                typer.echo(f"    cd {cd_dir}")
                typer.echo(f"    source .venv/bin/activate")
        typer.echo(f"    # Start building!\n")
