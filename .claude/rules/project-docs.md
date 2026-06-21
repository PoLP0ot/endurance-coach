# Project Docs Rule

> Source: `rules/project-docs.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Format and sync guidance for AGENTS.md, CLAUDE.md, and README.md
globs:
  - '**/AGENTS.md'
  - '**/CLAUDE.md'
  - '**/README.md'
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Project documentation format

This rule governs **format and tone** of project docs. For triggering updates after code changes, see `memory-maintenance`.

## AGENTS.md / CLAUDE.md (model-oriented)

Write for AI agents — dense, operational, no fluff:

- Architecture overview and key directories
- How to install, run, test, lint, and build (exact commands)
- Required env vars and config
- Verification steps after changes
- Project-specific conventions agents must follow
- Memory table pointing to `.claude/memory/` (if project memory is initialized)

Use `AGENTS.md` by default. Use `CLAUDE.md` only when the project explicitly targets Claude — same content, same rules.

## README.md (human-oriented)

Write for developers onboarding or browsing the repo:

- What the project is and who it's for
- Prerequisites and quick start
- Common workflows in plain language
- Links to deeper docs, deployment, contributing

## Keep in sync

When you change one file, check whether the other needs the same factual update:

- New or removed commands (test, lint, build, migrate, seed)
- Env vars, ports, or service URLs
- Architecture, folder layout, or stack changes
- Setup or verification steps

Same facts, different tone — do not copy-paste blocks verbatim between files.

| Topic        | AGENTS.md / CLAUDE.md      | README.md                  |
| ------------ | -------------------------- | -------------------------- |
| Commands     | Exact, copy-pasteable      | Explained in context       |
| Architecture | Structural, path-oriented  | High-level overview        |
| Env vars     | Complete list with purpose | Setup-focused subset       |
| Verification | Step-by-step checks        | "How to run tests" section |

If only one file exists, create the missing one when the project has enough substance to warrant it.
