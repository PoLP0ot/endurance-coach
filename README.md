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

## Deployment

### Full stack with Docker Compose (local prod-parity)

Brings up Postgres, Redis, the API, and the ARQ worker. The API runs Alembic
migrations on start and serves on host port **8001**.

```bash
cp api/.env.example api/.env   # app secrets (OpenAI, Supabase, ENCRYPTION_KEY)
# Datastore passwords are NOT in the compose file — supply them at run time:
POSTGRES_PASSWORD=change-me REDIS_PASSWORD=change-me docker compose up --build
```

Compose builds `DATABASE_URL`/`REDIS_URL` from `POSTGRES_PASSWORD`/`REDIS_PASSWORD`
(read from a root `.env` or your shell — it **fails fast** if they're unset) and
binds Postgres/Redis to `127.0.0.1` only. `ENVIRONMENT` defaults to
`development`; set it to `production` only against real managed datastores.

### Frontend on Vercel

`web/vercel.json` pins the framework, the EU region (`cdg1`), and baseline
security headers. Set these project env vars in the Vercel dashboard:

| Var | Purpose |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | Base URL of the deployed FastAPI API |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anonymous key |

### API env vars (`api/.env`)

| Var | Purpose |
| --- | --- |
| `DATABASE_URL` | Postgres DSN (SQLite `sqlite:///./dev.db` for local dev) |
| `REDIS_URL` | Redis DSN for ARQ jobs |
| `SUPABASE_URL` / `SUPABASE_JWT_SECRET` | Auth: JWT verification |
| `OPENAI_API_KEY` | LLM narration (chat / analysis / plan) |
| `ENCRYPTION_KEY` | Fernet key encrypting Garmin tokens at rest |
| `LOG_LEVEL` | Log level (default `INFO`); JSON logs outside `development` |
| `RESEND_API_KEY` | Weekly email send (optional) |
| `PADDLE_*` | Checkout + webhook (optional) |

## Architecture notes

- **GarminProvider** isolates the unofficial `garminconnect` library so it can
  be swapped for the official API later.
- **AnalyticsEngine** is pure, deterministic Python — fully unit-tested.
- **LLMProvider** routes Sonnet for chat/analysis and Opus for plan generation;
  it receives structured facts and produces narrative only.
- Garmin credentials are encrypted at rest (Fernet) — never stored in plaintext.

See `.claude/memory/` for the full project brief and architecture.
