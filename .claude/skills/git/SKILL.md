---
name: git
description: Git workflow for commits, branches, and PR creation. Use when creating commits, opening pull requests, choosing a branch, or following team git conventions.
---

> Claude Code adaptation: migrated from `skills/git/SKILL.md`. Use as a project skill under `.claude/skills/git/SKILL.md`.

# Git Workflow

## Branching

- If work is linked to a Linear card, use the card's branch.
- Otherwise, use `{username}/{type}-{description}`:
  - **username**: your git username (e.g. `olivier`)
  - **type**: `feat`, `fix`, `chore`, or `docs`
  - **description**: short **kebab-case** summary (lowercase words separated by hyphens)
  - Examples: `olivier/feat-add-user-auth`, `olivier/fix-login-timeout`

## Commits

- Always generate commit messages compliant with commitlint if present.
- Fallback: conventional commits (`type(scope?): subject`).
- Keep commit messages complete but concise.
- One logical change per commit when possible.

## Pull requests

- Create PRs in **draft** mode by default.
- PR title follows conventional commit format (same as commits) — it becomes the squash commit message on merge.
- PR description should explain **what** changed and **why** — complete but concise.
- When linked to a Linear issue, include a **magic word + issue ID** in the PR description to auto-link (and close on merge).
  - Magic words: `Close`, `Fixes`, `Resolves` (and variants)
  - Example: `Close ADB-123`

## PR reviews

- For reviewing someone else's PR on GitHub, use the `github-pr-review` skill — not this one.
