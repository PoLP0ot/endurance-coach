---
name: uv-package-management
description: UV dependency management for container-first Python projects. Use when adding, removing, upgrading packages, running scripts, syncing environments, or setting up local IDE venv in Docker-based Python projects.
---

> Claude Code adaptation: migrated from `skills/uv-package-management/SKILL.md`. Use as a project skill under `.claude/skills/uv-package-management/SKILL.md`.

# UV Package Management

All dependency operations run inside Docker. Never install packages locally.

## Commands

| Task | Command |
|------|---------|
| Add dependency | `docker compose run --rm notebooks uv add <pkg>` |
| Add dev dependency | `docker compose run --rm notebooks uv add --dev <pkg>` |
| Remove dependency | `docker compose run --rm notebooks uv remove <pkg>` |
| Sync (install all) | `docker compose run --rm notebooks uv sync` |
| Lock only | `docker compose run --rm notebooks uv lock` |
| Upgrade one package | `docker compose run --rm notebooks uv lock --upgrade-package <pkg>` |
| Run a script | `docker compose run --rm notebooks uv run --no-sync <cmd>` |
| Pin Python version | `uv python pin X.X.X` |

## Critical: `--no-sync`

**Always** use `uv run --no-sync` inside Docker containers. Without it, UV attempts to resolve dependencies against the public PyPI + private index, which fails because container runtime lacks `SAGACIFY_PYPI_USERNAME`/`SAGACIFY_PYPI_PASSWORD` credentials at that stage.

## Version constraints

- PEP 440 syntax: `>=1.0,<2` — not Poetry caret (`^1.0`)
- Never edit `pyproject.toml` constraints manually — use `uv add`/`uv remove`
- Lock file: `uv.lock` (committed to Git)

## Private index

Configured in `pyproject.toml`:

```toml
[[tool.uv.index]]
name = "sagacify"
url = "https://pypiserver.sagacify.com/"
```

Credentials via env vars: `SAGACIFY_PYPI_USERNAME`, `SAGACIFY_PYPI_PASSWORD` (in `~/.zshrc` and Docker build secrets).

## Local `.venv` for IDE

The `.venv/lib` directory is volume-mounted from the container to the host so your IDE gets autocomplete, linting, and type checking.

- **Setup after clone:** `docker compose run --rm notebooks uv sync`
- **IDE interpreter:** point to `.venv/bin/python`
- **Never execute code via local `.venv`** — all execution inside Docker
- After `uv add`/`uv remove`, the volume mount updates `.venv/lib` automatically

## Python version

UV manages Python versions (not pyenv):

- `uv python pin X.X.X` — sets `.python-version` for the project
- `uv python install X.X.X` — installs a version locally
- `uv python list` — shows available versions
