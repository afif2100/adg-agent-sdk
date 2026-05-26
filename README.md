# adg-agent-sdk

> **ADG SDK** — a CLI tool to scaffold AI Development Group (ADG) compliant projects.

```bash
pip install adg-agent-sdk
adg-sdk start
```

## Quick Start

### Interactive mode

```bash
adg-sdk start
```

Follow the prompts to configure your project — name, stack (backend / frontend / fullstack), Docker, CI, and more.

### One-liner mode

```bash
# Backend project (default)
adg-sdk init my-analytics-app

# Frontend-only (Vite + React)
adg-sdk init my-app --stack fe

# Fullstack (backend + frontend)
adg-sdk init my-app --stack fe+be

# With Docker and CI
adg-sdk init my-app --docker --ci

# Preview what would be created
adg-sdk init my-app --dry-run
```

## CLI Reference

```
adg-sdk start [options]              Interactive project creation

adg-sdk init <project-name> [options]  Non-interactive scaffolding

Options:
  --stack / -s    TEXT       Project stack: be, fe, or fe+be  [default: be]
  --dir / -d      PATH       Output directory (default: <project-name>)
  --example-code             Include example agent/tool/workflow code [default: True]
  --no-example-code          Skip example code
  --docker                   Add Dockerfile and docker-compose.yml
  --ci                       Add GitHub Actions CI workflow
  --git / --no-git           Initialize a git repository [default: True]
  --venv / --no-venv         Create a virtual environment with uv [default: True]
  --force / -f               Overwrite existing directory
  --dry-run                  Preview files without writing
  --version / -V             Show SDK version
```

## What Gets Scaffolded

### Backend (`adg-sdk init my-app` or `--stack be`)

```
my-app/
├── AGENTS.md                  # Behavioral guidelines for AI-assisted dev
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── app.py             # Entry point
│       ├── agents/            # Agent definitions
│       │   └── hello_agent.py
│       ├── tools/             # Tool implementations
│       │   └── example_tool.py
│       ├── workflows/         # Workflow definitions
│       │   └── main_workflow.py
│       └── config/
│           ├── __init__.py
│           └── settings.py    # Pydantic settings
├── tests/                     # Pytest tests
├── .adg-sdk                   # SDK version marker
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

### Frontend (`--stack fe`)

```
my-app/
├── AGENTS.md
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js               # React entry point
│   └── App.js                # App component
├── .adg-sdk
├── .env.example
├── .gitignore
└── README.md
```

### Fullstack (`--stack fe+be`)

```
my-app/
├── AGENTS.md
├── backend/                     # Python backend
│   ├── pyproject.toml
│   ├── src/my_app/...
│   └── tests/...
├── frontend/                    # Vite + React frontend
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   └── src/...
├── .adg-sdk
├── .env.example
├── .gitignore
└── README.md
```

## Interactive Start

Use `adg-sdk start` for an interactive questionnaire:

```bash
$ adg-sdk start

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ADG SDK › Let's start a new project!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Project name: my-analytics-app
Project stack [be/fe/fe+be] (be): fe+be
Include Docker? [y/N]: y
Include CI workflow? [y/N]: y
Include example agent/tool/workflow code? [Y/n]: Y
Initialize git repository? [Y/n]: Y
Create Python virtual environment? [Y/n]: Y
```

## Development

```bash
git clone https://github.com/afif2100/adg-agent-sdk
cd adg-agent-sdk
uv sync
adg-sdk --help
```

## Tests

```bash
uv run pytest
```

## ADG Standards

Projects created with `adg-sdk init` or `adg-sdk start` follow AI Development Group conventions:

- **Python >=3.11** — modern type hints, `match` statements, `tomllib`
- **src/ layout** — clean Python packaging, `pip install -e .` ready
- **Separation of concerns** — agents, tools, and workflows as first-class directories
- **Pydantic config** — type-safe settings from environment variables
- **Frontend-ready** — Vite + React out of the box
- **Agent-ready** — `AGENTS.md` with behavioral guidelines for LLM coding

## License

MIT
