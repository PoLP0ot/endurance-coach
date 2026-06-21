# Vitest Rule

> Source: `rules/vitest.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Testing standards for Vitest - prevent duplicate bootstrapping
globs:
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
  - "**/tests/**/*.ts"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Vitest Testing Context

This file appears to be a test file using Vitest.

When writing or modifying tests:
- Avoid duplicate test bootstrapping
- Apply the `vitest-test-setup-awareness` skill
