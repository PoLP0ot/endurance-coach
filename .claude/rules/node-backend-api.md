# Node Backend Api Rule

> Source: `rules/node-backend-api.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Backend API standards - apply path structure and logging conventions
globs:
  - "**/server.{ts,js}"
  - "**/api/**/*.{ts,js}"
  - "**/routes/**/*.{ts,js}"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Backend API Context

This file appears to be part of backend API code.

When working on API routes and backend services:
- Use **one folder per path segment**.
  - Example: `/api/v1/users/:id` → `api/v1/users/_id/`
- When you need to log, use the `node-backend-logging` skill for structured logging
- For config, env vars, and external resources, use the `node-backend-config` skill
