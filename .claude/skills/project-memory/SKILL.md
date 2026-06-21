---
name: project-memory
description: Initialize, refresh, and maintain self-enriching project memory (AGENTS.md + .claude/memory/). Use when running /refresh-memory, initializing memory, or updating memory files after impactful changes.
---

> Claude Code adaptation: migrated from `skills/project-memory/SKILL.md`. Use as a project skill under `.claude/skills/project-memory/SKILL.md`.

# Project Memory

Token-efficient persistent project knowledge: **AGENTS.md** (always loaded, managed front page) + **`.claude/memory/*.md`** (on-demand depth).

## Principles

- AGENTS.md is fully managed by this system — operational facts inline, deep knowledge in memory files.
- Never delete facts when relocating content from an existing AGENTS.md.
- No duplication between AGENTS.md and memory files; one source of truth per concern.
- Agent-dense markdown: bullets, tables, paths — no onboarding prose.

## File layout (per project)

```
AGENTS.md
.claude/
  memory/
    project-brief.md
    architecture.md
    conventions.md
    business-logic.md
    ux-direction.md
    stack-and-deps.md
    active-context.md
```

Templates (after `./install.sh`): `~/.claude/templates/project-memory/` — copy into the project on init; do not symlink memory into projects.

## AGENTS.md format

Keep under ~150 lines. Sections:

1. `# Project Name` + one-line description
2. `## Commands` — exact install/run/test/lint/build/deploy
3. `## Environment` — required env vars, ports, services
4. `## Architecture (summary)` — 5–10 lines, key paths only
5. `## Verification` — post-change checks
6. `## Memory` — table indexing `.claude/memory/` files

Memory table columns: **File | Contains | Read when**

Standard rows (omit file row if N/A for project):

| File | Contains | Read when |
|------|----------|-----------|
| project-brief.md | Mission, goals, users | New features, scope questions |
| architecture.md | Design, boundaries, data flow | Structural changes, new modules |
| conventions.md | Patterns, naming, testing | Writing/reviewing code |
| business-logic.md | Domain rules, entities, workflows | Features, validation |
| ux-direction.md | Design tokens, UX principles, flows | UI work, new screens |
| stack-and-deps.md | Frameworks, versions, infra | Deps, config, deploy |
| active-context.md | Current focus, decisions, issues | Session start, continuity |

## Memory file formats

Each file ~50–200 lines. Use headings and bullets.

### project-brief.md

- Purpose, target users, core problems solved
- Success criteria / non-goals
- High-level product constraints

### architecture.md

- Stack and runtime boundaries (monolith, services, packages)
- Key directories and what lives where
- Data flow, auth, external integrations
- Important design decisions (with rationale if non-obvious)

### conventions.md

- Project-specific patterns (not generic style — team rules cover that)
- Testing approach, folder conventions, API patterns
- Things agents must not do in this repo

### business-logic.md

- Domain entities and relationships
- Workflows, state machines, validation rules
- Edge cases and business invariants

### ux-direction.md

- Design system (ShadCN, tokens, typography component, etc.)
- Layout/navigation patterns
- Accessibility or i18n expectations

### stack-and-deps.md

- Languages, frameworks, major libraries with versions when known
- Infrastructure (Docker, DB, queues, cloud)
- Config files and how env maps to runtime

### active-context.md

- Current sprint / focus area
- Recent decisions and open questions
- Known issues or tech debt worth remembering

## Enrichment during work

Update the relevant memory file when you make **impactful** changes:

| Change type | Update |
|-------------|--------|
| Structure, modules, APIs | architecture.md |
| New patterns, test setup | conventions.md |
| Domain rules, entities | business-logic.md |
| UI system, flows | ux-direction.md |
| Dependencies, infra | stack-and-deps.md |
| Focus, decisions | active-context.md |
| Goals, scope | project-brief.md |

Also update AGENTS.md if commands, env, verification, or architecture summary changed.

**Skip:** typo fixes, single-variable renames, button colors, comment-only edits.

Patch incrementally — do not rewrite entire files unless refresh mode requires it.

## Full init or refresh

Run `/refresh-memory` (command owns the procedure). This skill covers formats, templates, and incremental updates.

