---
name: pytest-setup-awareness
description: Prevent duplicate test bootstrapping when using pytest in Python projects.
---

> Claude Code adaptation: migrated from `skills/pytest-setup-awareness/SKILL.md`. Use as a project skill under `.claude/skills/pytest-setup-awareness/SKILL.md`.

# Pytest setup awareness

## Rule

When writing pytest tests, **do not** perform test bootstrapping inside the test suite:

- **No DB initialization** (creating connections, running migrations, seeding)
- **No env var setup** (clearing/injecting environment)
- **No mock server startup** (moto, mock APIs)
- **No fixture duplication** from `conftest.py`

Assume **`conftest.py`** already handles environment isolation, service mocks, and DB readiness.

## What to do instead

- Use existing fixtures from `conftest.py` and sub-package `conftest.py` files
- If a test needs specific state, add a minimal fixture or parametrize — don't rebuild the world
- Mock at service boundaries (`unittest.mock.patch`); don't re-implement mock infrastructure
- For LLM projects: use `MemorySaver` (not real Postgres) and canned LLM responses from `tests/mocks/`

## Quick checks (before adding setup code)

- Search for existing `conftest.py` at repo root and in `tests/` subdirectories
- Check if a fixture already provides what you need (DB client, test app, mock responses)
- If you're about to write `@pytest.fixture(autouse=True)` at module level, stop: it likely belongs in `conftest.py`

## Execution

```bash
docker compose run --rm notebooks uv run --no-sync pytest --cov=src --cov-fail-under=80
docker compose run --rm notebooks uv run --no-sync pylint --reports=no src/ tests/
docker compose run --rm notebooks uv run --no-sync black src/ tests/
```
