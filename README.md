# adg-agent-sdk

> **ADG SDK** — a CLI tool to scaffold AI Development Group (ADG) compliant projects.

```bash
pip install adg-agent-sdk
adg-sdk init my-project
cd my-project
uv sync
uv run python -m my_project
```

## Quick Start

```bash
# Interactive start — answers questions, scaffolds the project
adg-sdk start

# Basic scaffold — creates <project-name>/ directory
adg-sdk init my-analytics-app

# Fullstack project (backend + frontend)
adg-sdk init my-analytics-app --stack fullstack

# With Docker and CI
adg-sdk init my-analytics-app --docker --ci

# Backend-only, minimal (no example code)
adg-sdk init my-api --stack be --no-example-code

# Preview what would be created
adg-sdk init my-analytics-app --dry-run
```

## CLI Reference

```
Usage: adg-sdk [OPTIONS] COMMAND [ARGS]...

  Scaffold ADG (AI Development Group) compliant projects.

Commands:
  start     Interactive project creation (guided prompts)
  init      Create a new ADG project from CLI options

Options:
  --version / -V    Show SDK version
  --help            Show this message
```

### `adg-sdk start`

Guided interactive mode — asks you questions and scaffolds based on your answers:

```
? Project name: my-app
? Project stack:  [Backend / Fullstack / Frontend]
? Include example code?  [Yes / No]
? Add Docker support?  [Yes / No]
? Add CI workflow?  [Yes / No]
? Initialize git repository?  [Yes / No]
? Create virtual environment?  [Yes / No]
```

### `adg-sdk init`

```
adg-sdk init <project-name> [options]

Options:
  --stack / -s TEXT       Project stack: be, fullstack, fe  [default: be]
  --dir / -d PATH         Output directory (default: <project-name>)
  --example-code          Include example agent/tool/workflow code  [default: True]
  --no-example-code       Skip example code, scaffold only core structure
  --docker                Add Dockerfile and docker-compose.yml
  --ci                    Add GitHub Actions CI workflow
  --git / --no-git        Initialize a git repository  [default: True]
  --venv / --no-venv      Create a virtual environment with uv  [default: True]
  --force / -f            Overwrite existing directory
  --dry-run               Preview files without writing
  --version / -V          Show SDK version
```

## What Gets Scaffolded

### Backend (default)

```
my-project/
├── AGENTS.md                   # Behavioral guidelines for AI-assisted dev
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── __main__.py         # python -m entry
│       ├── app.py              # Application entry point
│       ├── agents/             # (with --example-code)
│       │   ├── __init__.py
│       │   └── hello_agent.py
│       ├── tools/              # (with --example-code)
│       │   ├── __init__.py
│       │   └── example_tool.py
│       ├── workflows/          # (with --example-code)
│       │   ├── __init__.py
│       │   └── main_workflow.py
│       └── config/
│           ├── __init__.py
│           └── settings.py     # Pydantic settings
├── tests/
├── .adg-sdk                    # SDK version marker
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### Frontend (Vite + vanilla JS)

```
my-project/
├── AGENTS.md
├── package.json
├── index.html
├── vite.config.js
├── src/
│   ├── main.js
│   └── App.js
├── .adg-sdk
├── .env.example
├── .gitignore
├── README.md
└── agents.md
```

### Fullstack (backend + frontend)

Combines both structures above under a single `src/` layout with `src/backend/` and `src/frontend/`.

## Interactive Prompt

### `adg-sdk start`

Walks you through project creation with clear prompts — ideal for first-time users or when you want to see all options before committing.

```
$ adg-sdk start

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ADG SDK › Interactive Project Creation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

? Project name: my-awesome-app
? Project stack (be / fullstack / fe): fullstack
? Include example code? [Y/n]: Y
? Add Docker support? [Y/n]: Y
? Add CI workflow? [Y/n]: Y
? Initialize git repository? [Y/n]: Y
? Create virtual environment? [Y/n]: Y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ADG SDK › Creating project: my-awesome-app
           Stack: Fullstack
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## ADG Standards

Projects created with `adg-sdk` follow AI Development Group conventions:

- **Python >=3.11** — modern type hints, `match` statements, `tomllib`
- **src/ layout** — clean Python packaging, `pip install -e .` ready
- **Separation of concerns** — agents, tools, and workflows as first-class directories
- **Pydantic config** — type-safe settings from environment variables
- **AGENTS.md** — behavioral guidelines for AI-assisted development
- **Agent-ready** — structured for AI-assisted development workflows

## Development

```bash
git clone https://github.com/afif2100/adg-agent-sdk
cd adg-agent-sdk
uv sync

# Run tests
uv run pytest

# Test the CLI locally
uv run adg-sdk --help
uv run adg-sdk init test-project
```

## License

MIT
