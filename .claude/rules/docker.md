# Docker Rule

> Source: `rules/docker.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Prefer Docker-based execution when Docker configuration is present
globs:
  - "**/docker-compose*.yml"
  - "**/Dockerfile*"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Docker Context Detected

This project contains Docker configuration.

When executing commands, starting services, or running scripts:
- Prefer Docker-based execution
- Apply the `docker-first-execution` skill
