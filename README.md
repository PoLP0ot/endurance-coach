# Endurance Coach

AI coaching platform for endurance athletes. Connect your Garmin, get personalized coaching, adaptive training plans, and a clear answer to "what does this run mean for my goal?"

> **Core principle:** the AI _never_ computes numbers. A deterministic
> `AnalyticsEngine` computes every metric (TSS, CTL/ATL/TSB, recovery). The LLM
> only narrates the facts it is given.

## Monorepo layout

```
web/    Next.js 15 (App Router, TS, Tailwind, shadcn/ui)   → Vercel
api/    FastAPI (Python 3.12+, SQLAlchemy, Alembic, ARQ)   → Railway/Fly.io (EU)
        supabase/schema.sql   Postgres schema + RLS policies
.github/workflows/ci.yml      pytest + ruff + vitest + lint + build
```

## Prerequisites

- Node 20+ and `pnpm`
- Python 3.12+
- A Supabase project (Postgres + Auth)
- Redis (for ARQ background jobs)

## Setup

### Backend (`api/`)

```bash
cd api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in secrets
alembic upgrade head          # or run supabase/schema.sql in Supabase
uvicorn app.main:app --reload # http://localhost:8000
```

Apply the database schema either via Alembic (`alembic upgrade head`) or by
running `supabase/schema.sql` in the Supabase SQL editor (the SQL version also
sets up Row Level Security policies).

### Frontend (`web/`)

```bash
cd web
pnpm install
cp .env.example .env.local     # fill in Supabase + API URLs
pnpm dev                       # http://localhost:3000
```

## Testing & quality

```bash
# Backend
cd api && pytest -q && ruff check .

# Frontend
cd web && pnpm vitest run && pnpm lint && pnpm build
```

## Architecture notes

- **GarminProvider** isolates the unofficial `garminconnect` library so it can
  be swapped for the official API later.
- **AnalyticsEngine** is pure, deterministic Python — fully unit-tested.
- **LLMProvider** routes Sonnet for chat/analysis and Opus for plan generation;
  it receives structured facts and produces narrative only.
- Garmin credentials are encrypted at rest (Fernet) — never stored in plaintext.

See `.claude/memory/` for the full project brief and architecture.
