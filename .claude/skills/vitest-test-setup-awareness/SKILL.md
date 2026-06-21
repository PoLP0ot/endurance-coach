---
name: vitest-test-setup-awareness
description: Prevent duplicate test bootstrapping when using Vitest.
---

> Claude Code adaptation: migrated from `skills/vitest-test-setup-awareness/SKILL.md`. Use as a project skill under `.claude/skills/vitest-test-setup-awareness/SKILL.md`.

# Vitest test setup awareness

## Rule

When writing Vitest tests, **do not** perform test bootstrapping inside the test suite:

- **No vitest reset mocks**
- **No DB initialization** (creating connections/containers/clients for bootstrapping).
- **No migrations**.
- **No DB seeding**.

Assume **Vitest global setup** already handles environment + database readiness.

## What to do instead

- Assume each mutation db operation is rollbacked at the end of each test automatically.
- Use the existing test models already provided by the project.
- If a test needs a special state, set up *only the minimal records needed* via the models.

## Quick checks (before adding setup code)

- Search the repo for existing `globalSetup`, `setupFiles`, or `setupFilesAfterEnv` usage.
- If you’re about to add `beforeAll` that “prepares the DB”, stop: prefer existing global setup or per-test minimal fixtures.

