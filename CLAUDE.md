# Endurance Coach

AI coaching platform for endurance athletes. Import Garmin data, get personalized coaching, adaptive training plans.

## Stack

- **Frontend:** Next.js 15 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend:** FastAPI (Python 3.12+) + SQLAlchemy + Alembic
- **Database:** PostgreSQL (Supabase)
- **Auth:** Supabase Auth (JWT)
- **Payments:** Paddle (Merchant of Record)
- **Queue:** ARQ + Redis (async jobs: Garmin import, AI analysis, emails)
- **Email:** Resend
- **AI:** Anthropic Claude (Sonnet for chat/analysis, Opus for plan generation)
- **Garmin:** python-garminconnect (unofficial, isolated behind GarminProvider interface)

## Architecture

Monorepo: `web/` (Next.js → Vercel) + `api/` (FastAPI → Railway/Fly.io, EU region)

The Next.js frontend talks to FastAPI over `fetch` with Supabase JWT as Bearer token.
FastAPI is the only place Python runs — Garmin import, AI coaching, analytics engine.
The AI NEVER computes numbers. A deterministic AnalyticsEngine computes all metrics (TSS, CTL/ATL/TSB, recovery). The LLM only narrates provided facts.

## Code Standards

- TypeScript strict mode. Python type hints on all public functions.
- TDD: RED (failing test) → GREEN (minimal code) → REFACTOR → BUILD → LINT → COMMIT
- Backend tests: `cd api && pytest -q`. Frontend: `cd web && pnpm vitest run`.
- Lint: `pnpm lint` (ESLint), `ruff check api/`
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- No demo data in production code. Real data or nothing.

## Key Commands

```bash
# Dev
cd api && uvicorn app.main:app --reload     # Backend on :8000
cd web && pnpm dev                           # Frontend on :3000

# Tests
cd api && pytest -q                          # Backend tests
cd web && pnpm vitest run                     # Frontend tests

# Quality
cd web && pnpm lint && pnpm build
cd api && ruff check .
```

## Project Context

All project context lives in `.claude/memory/`:
- `project-brief.md` — What we're building and why
- `architecture.md` — System design and data flow
- `business-logic.md` — Domain rules (TSS calculation, training zones, etc.)
- `stack-and-deps.md` — Exact versions and dependencies
- `conventions.md` — Code style, naming, patterns
- `active-context.md` — Current phase, open decisions
- `ux-direction.md` — Design system and UX patterns

## AT STARTUP, BEFORE ANY CODE CHANGE:
Read ALL `.claude/memory/*.md` files. This is MANDATORY. Never skip this step.

## Hermes PM Rules
- Hermes is PM/QA. Claude Code does ALL coding.
- Every story must pass QA gate (tests + build + lint + manual) before next story.
- NEVER proceed to story N+1 with open bugs.
- Source code only when fixing bugs — never touch memory/docs/design.
