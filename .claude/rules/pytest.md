# Pytest Rule

> Source: `rules/pytest.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Pytest testing standards for Python projects
globs:
  - "**/test_*.py"
  - "**/tests/**/*.py"
  - "**/*_test.py"
  - "**/conftest.py"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Pytest

## Philosophy

- **Write from docstrings**: derive tests from the public docstring of the function under test, not from reading its implementation
- **Test results, not mechanics**: assert what a function *returns* or *raises* — not which internal helpers it calls, which branch it takes, or what intermediate values it computes
- **No private-method tests**: do not call methods or functions prefixed with `_`; test the public API
- **No third-party testing**: do not write tests for code from external libraries
- **Mock external I/O**: patch heavy or filesystem-dependent callsites via `unittest.mock.patch`; prefer reusable fixtures from `conftest.py`

## Structure

- **File layout**: mirror `src/` — `src/foo/bar.py` → `tests/foo/test_bar.py`
- **Coverage target**: 80% line coverage (`--cov-fail-under=80`)
- Avoid duplicate test bootstrapping — apply the `pytest-setup-awareness` skill
