# adg-agent-sdk

> **ADG SDK** — a CLI tool to scaffold AI Development Group (ADG) compliant projects.

```bash
pip install adg-agent-sdk
adg-sdk init my-project
cd my-project
source .venv/bin/activate
python -m my_project
```

## Quick Start

```bash
# Basic scaffold
adg-sdk init my-analytics-app

# With Docker and CI
adg-sdk init my-analytics-app --docker --ci

# Minimal (no example code, no git, no venv)
adg-sdk init my-analytics-app --no-example-code --no-git --no-venv

# Preview what would be created
adg-sdk init my-analytics-app --dry-run
```

## CLI Reference

```
adg-sdk init <project-name> [options]

Options:
  --dir / -d PATH         Output directory (default: <project-name>)
  --example-code          Include example agent/tool/workflow code [default: True]
  --no-example-code       Skip example code, scaffold only core structure
  --docker                Add Dockerfile and docker-compose.yml
  --ci                    Add GitHub Actions CI workflow
  --git / --no-git        Initialize a git repository [default: True]
  --venv / --no-venv      Create a virtual environment with uv [default: True]
  --force / -f            Overwrite existing directory
  --dry-run               Preview files without writing
  --version / -V          Show SDK version
```

## What Gets Scaffolded

```
my-project/
├── src/
│   └── my_project/
│       ├── __init__.py       # Package metadata
│       ├── app.py            # Entry point
│       ├── agents/           # (with --example-code)
│       │   └── hello_agent.py
│       ├── tools/            # (with --example-code)
│       │   └── example_tool.py
│       ├── workflows/        # (with --example-code)
│       │   └── main_workflow.py
│       └── config/
│           ├── __init__.py
│           └── settings.py   # Pydantic settings
├── tests/                    # Pytest tests
├── .adg-sdk                  # SDK version marker
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Development

```bash
git clone https://github.com/afif2100/adg-agent-sdk
cd adg-agent-sdk
uv sync
adg-sdk init --help
```

## ADG Standards

Projects created with `adg-sdk init` follow AI Development Group conventions:

- **Python >=3.11** — modern type hints, `match` statements, `tomllib`
- **src/ layout** — clean Python packaging, `pip install -e .` ready
- **Separation of concerns** — agents, tools, and workflows as first-class directories
- **Pydantic config** — type-safe settings from environment variables
- **Agent-ready** — structured for AI-assisted development workflows

## License

MIT
