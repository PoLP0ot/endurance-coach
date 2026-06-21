# Memory Maintenance Rule

> Source: `rules/memory-maintenance.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
alwaysApply: true
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Project memory maintenance

If this project has no `.claude/memory/` directory, skip this rule entirely.

## When to update

After making impactful changes, you MUST update the relevant `.claude/memory/` file(s) before considering the work complete. This includes follow-up changes in the same session — do not defer to "later".

Skip trivial edits (typos, single renames, comment-only changes).

## What to update

| Change type | Update |
|-------------|--------|
| Domain rules, workflows, state machines | business-logic.md |
| Structure, modules, data flow | architecture.md |
| Patterns, test setup, error handling | conventions.md |
| Dependencies, infra, config | stack-and-deps.md |
| Focus, decisions, open questions | active-context.md |
| Goals, scope, users | project-brief.md |

Also update AGENTS.md if commands, env, verification, or architecture summary changed.
When updating AGENTS.md, also check if README.md needs the same factual update (see `project-docs` rule for format guidance).

## How to enforce

- For multi-step tasks using a todo list, add a "Update memory files" todo as the last item before verification.
- For single-step changes, update memory inline right after the code change.
- Patch incrementally — do not rewrite entire files for small changes.
