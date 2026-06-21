# Python Rule

> Source: `rules/python.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Python coding conventions for ML and LLM projects
globs:
  - "**/*.py"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Python

- Type hints on function signatures; Pydantic models for data schemas
- Google-style docstrings on public functions and classes
- Prefer functional, composable code; avoid classes unless the domain requires them
- f-strings over `.format()` or `%`
- Explicit `None` checks (`if x is None`) over falsy checks when `0`/`""` are valid
- Imports: stdlib → third-party → local, separated by blank lines
- No wildcard imports; no unused imports
- No historical commentary in code or docs — describe current behaviour only (no "previously…", "no longer…", "used to…")
- Notebooks are for exploration only — no production logic; reusable functions belong in `src/`

## Verification

After code changes, run pylint and fix all issues before considering the task done:

```bash
docker compose run --rm notebooks uv run --no-sync pylint --reports=no src/ tests/
```

When managing dependencies or running commands, use the `uv-package-management` skill.
When logging, use the `python-logging` skill.

For deep work on classical ML (pipelines, training, predictors), apply `python-ml-expert`.
For deep work on LLM/bot projects (assistants, graphs, prompts), apply `python-llm-expert`.
