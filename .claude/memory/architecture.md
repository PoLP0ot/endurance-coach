# Architecture

## System Diagram

```
Browser (Next.js 15) → FastAPI → Supabase PostgreSQL
                           ↓
                    ARQ Workers (Redis)
                    ├── GarminProvider (python-garminconnect)
                    ├── AnalyticsEngine (TSS/CTL/ATL/TSB — deterministic)
                    ├── LLMProvider (Anthropic Claude — narration only)
                    └── EmailWorker (Resend)
```

## Core Principle
The AI NEVER computes numbers. AnalyticsEngine is pure Python, deterministic, fully testable. The LLM only narrates provided facts — it receives structured metrics and produces natural language analysis. This kills the hallucination risk on metrics.

## Key Interfaces
- `GarminProvider` — isolates unofficial python-garminconnect. Swap to official API via new implementation.
- `AnalyticsEngine` — pure functions: TSS, CTL/ATL/TSB recurrence, recovery score, intensity distribution
- `LLMProvider` — Anthropic Claude, with model router (Sonnet for chat, Opus for plan generation)

## Data Flow
Garmin import → credentials encrypted at rest → ARQ job → Activity + Health APIs → store in PostgreSQL → AnalyticsEngine computes metrics → LLM generates narrative → cache in ai_analyses → serve to frontend

## Garmin Import Pipeline (US1)
`POST /garmin/connect` → provider.login (typed errors: auth/MFA/locked) → encrypt token (Fernet) → upsert GarminConnection → create ImportJob (queued) → enqueue ARQ job → 202 {job_id}. Worker decrypts token and runs `garmin_import.run_import`: upsert activities (idempotent on user_id+garmin_activity_id) → upsert daily_health (idempotent on user_id+day) → store downsampled streams (cap 1000) into activity_metrics, updating ImportJob.progress_label at each step. Poll via `GET /garmin/import-status/{job_id}` (ownership-checked). `/garmin/sync` is incremental from last_sync_at; `/garmin/disconnect` keeps data. Tables: daily_health, import_jobs (migration 0002).

## API Surface (current)
- `GET /health`, `GET /me` (identity probe)
- `GET/PATCH /profile` — user profile (US11a)
- Garmin: `POST /garmin/connect`, `GET /garmin/status`, `GET /garmin/import-status/{job}`, `POST /garmin/sync`, `POST /garmin/disconnect`
- `GET /dashboard` — coach-first fitness/form/recovery + load series
- `GET /activities`, `GET /activities/{id}`, `GET /activities/{id}/analysis` (premium)
- Chat: `GET /chat/messages`, `POST /chat` (premium)
- Plans: `POST /plans`, `GET /plans/current` (premium)
- Subscription: `GET /subscription/status`, `POST /subscription/checkout`, `POST /subscription/webhook` (Paddle, signature-verified)
- `GET /email/weekly/preview` (premium)
- GDPR: `GET /gdpr/export`, `DELETE /gdpr/account`

## Deterministic vs LLM split
AnalyticsEngine + service layer compute ALL numbers (dashboard, activity facts, plan periodization, weekly-email facts). The LLM (`LLMProvider`, injected via `deps.get_llm_provider`, stubbed in tests) only narrates: activity analysis, chat replies, plan rationale, weekly-email prose. Services take a `_Narrator` protocol so the Anthropic SDK is import-lazy and never loaded in tests.

## Models / migrations
users, garmin_connections, activities, activity_metrics, ai_analyses, daily_health, import_jobs (0001–0002); chat_messages (0003, int PK for stable ordering); training_plans (0004); subscriptions (0005); user units/weekly_email_opt_in (0006); gdpr_audit_log (0007, FK-free so it survives erasure).

## Monorepo Structure
```
web/    — Next.js 15 App Router, Tailwind, shadcn/ui
api/    — FastAPI, SQLAlchemy, Alembic, ARQ workers
  app/
    routers/    — auth, garmin, activities, analytics, chat, plans, subscriptions, gdpr
    services/   — GarminProvider, AnalyticsEngine, LLMProvider, SubscriptionService
    models/     — SQLAlchemy models
    jobs/       — ARQ background tasks
    core/       — config, deps, security
```
