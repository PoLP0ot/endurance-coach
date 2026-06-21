# Typescript Rule

> Source: `rules/typescript.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: TypeScript coding conventions
globs:
  - "**/*.ts"
  - "**/*.tsx"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# TypeScript Conventions

- Prefer async/await over promise chains
- Use arrow functions only
- Avoid classes unless required
- Avoid `any` in production code; acceptable in test files
