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
