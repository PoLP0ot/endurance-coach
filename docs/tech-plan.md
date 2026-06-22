# Endurance Coach — Technical Architecture & Implementation Plan

> Author: Hermes (planning) · Implementation: Claude
> Date: 2026-06-21
> Source of truth: `research.md`, `go-to-market.md`, `screen-spec.md`, `qa-checklist.md`
> Scope: MVP (2 weeks). Garmin-only. Multi-brand vision deferred to V2.
> **Hermes plans. Hermes never writes code. This document is the contract Claude implements against.**

---

## 0. Assumptions & Decisions Log

These are decisions made to avoid blocking. Each is reversible but documented.

| # | Decision | Rationale |
|---|----------|-----------|
| A1 | **Payments = Paddle** (Merchant of Record), NOT Stripe. | Task constraint overrides screen-spec/QA mentions of Stripe. Paddle handles EU VAT/sales tax as MoR — big win for a solo EU founder. Every "Stripe" in screen-spec.md/qa-checklist.md is read as "Paddle". |
| A2 | **python-garminconnect (unofficial)** is the import mechanism for MVP. | Task constraint. The research doc flags this as ToS-violating and fragile; we design defensively (§7). We do NOT block MVP on official Garmin Developer Program approval (2-week lead time). A migration path to the official API is kept open behind a provider interface. |
| A3 | **Data residency = EU.** Supabase project in `eu-central-1` (Frankfurt). | GDPR Art. 9 — Garmin health data is a special category. Keeping storage in the EU minimizes transfer risk. |
| A4 | **AI provider = Anthropic Claude**, with a model router. Sonnet for chat/analysis, Opus for plan generation. | Cost model in research.md §B6. EU inference endpoint / zero-retention + DPA required (§7, §1.4). A `LLMProvider` interface allows swapping. |
| A5 | **Garmin credentials stored encrypted** (session tokens, not raw password where possible). python-garminconnect logs in with email+password and caches a token (GarminTokenStore). We encrypt the token blob at rest with app-level envelope encryption. | Defensive — minimize blast radius of a breach (QA SEC4). |
| A6 | **Background jobs** run in FastAPI via a task queue (ARQ + Redis). Garmin import, AI analysis generation, weekly emails are async. | Imports + AI are too slow for request/response. Onboarding shows simulated progress while the job runs (screen-spec §3). |
| A7 | **Auth = Supabase Auth.** FastAPI validates the Supabase JWT (JWKS/asymmetric or shared secret HS256). | Task constraint. Detail in §3.2. |
| A8 | **Monorepo**, two deployables: `web/` (Next.js → Vercel) and `api/` (FastAPI → Fly.io or Railway, EU region). | Next.js cannot run python-garminconnect; FastAPI is the only place Python lives. |
| A9 | **Free vs Premium gate**: Free = dashboard + analytics + last 30 days. Premium = full history, AI chat (unlimited), AI activity analysis, training plans, weekly email. | go-to-market §5.3. Enforced server-side (§3.3). |
| A10 | **Email = Resend** (EU region) with React Email templates. | Good DX, EU data region, simple transactional + scheduled. |
| A11 | Migrations: **Alembic** owns the schema (FastAPI is the writer of domain tables). Supabase migrations own only the `auth` schema + RLS policies. | Avoids two tools fighting over the same tables. Detail §2.6. |
| A12 | RLS (Row Level Security) is **belt-and-suspenders**: FastAPI uses the service role and enforces ownership in code; RLS is still enabled so a leaked anon key can't read other users' rows (QA SEC2). | Defense in depth. |
| A13 | **Modular Goal Architecture.** Users settle on a primary goal during onboarding (conversationally, see A15). The dashboard, coaching, and training plans adapt to the goal type. Each goal is a "lens" that changes: which metrics are primary, what the coach focuses on, and what "success" looks like. | Prevents a one-size-fits-all dashboard. Marathon runner needs pace/TSS/projected finish; weight loss user needs calorie balance/steps/weight trend; Hyrox needs hybrid metrics; triathlon needs 3-sport balance; general health needs sleep/HRV/movement. MVP fully renders Running/Marathon, Weight Loss and General Health lenses; the architecture (goal field + per-goal dashboard config) is ready for Triathlon and Hyrox, which onboarding already supports and which reuse the health/hybrid lens until their dedicated dashboard ships. |
| A14 | **Push to Watch.** A training-plan week can send its structured workouts to the user's Garmin watch (they land in the watch's Training Calendar). Implemented via the same `GarminProvider` interface as import (A2). python-garminconnect exposes workout upload/schedule; kept behind the provider so the official API can replace it later. State (which weeks are pushed) is persisted per plan-week. | Real differentiator and stickiness — closes the loop from "AI builds the plan" to "watch runs the plan". Send is async (provider call can be slow / fail), surfaced via a modal with sending/success/error+retry states (screen-spec §7.4). Only current + future weeks are pushable. |
| A15 | **Conversational Onboarding.** After Garmin import, goal selection happens through a chat with the AI coach (no static menu). A guided state machine (welcome → goal kind → goal-specific follow-ups → hand-off) walks the athlete to a goal type, then routes them to the matching dashboard variant (A13). Suggestion chips + free-text both feed the same engine; free text is classified to a goal kind by keyword rules with a graceful catch-all. | The first "coach-first" touch: the coach references the just-imported Garmin data naturally instead of dumping it, and the conversation — not a form — determines the goal. MVP runs the conversation over the chat UI; the resulting goal is persisted via `PATCH /me/goal` (§3). The same chat engine powers the persistent Coach screen (A4). |

---

## 1. Architecture

### 1.1 System diagram

```
                          ┌──────────────────────────────────────────┐
                          │                BROWSER                      │
                          │  Next.js 15 (App Router, RSC) + Tailwind    │
                          │  shadcn/ui · Recharts · Mapbox GL           │
                          └───────────────┬─────────────┬──────────────┘
                                          │             │
                  Supabase JS (auth)      │             │  fetch (Bearer JWT)
                                          │             │
                          ┌───────────────▼───┐     ┌───▼───────────────────────────┐
                          │   SUPABASE (EU)    │     │      FASTAPI (EU region)       │
                          │  ┌──────────────┐  │     │  ┌──────────────────────────┐ │
                          │  │ Auth (GoTrue)│◄─┼─────┼──┤ JWT verify (JWKS/secret) │ │
                          │  │ JWT issuer   │  │     │  └──────────────────────────┘ │
                          │  └──────────────┘  │     │  Routers: auth, garmin,        │
                          │  ┌──────────────┐  │     │  activities, analytics, chat,  │
                          │  │ PostgreSQL    │◄─┼─────┼─ plans, subscriptions, gdpr   │
                          │  │ (domain data) │  │ SQL │  ┌──────────────────────────┐ │
                          │  │ + RLS         │  │     │  │ Service layer             │ │
                          │  └──────────────┘  │     │  │  - GarminProvider (iface) │ │
                          └────────────────────┘     │  │  - AnalyticsEngine (TSS…) │ │
                                                      │  │  - LLMProvider (iface)    │ │
                                                      │  │  - SubscriptionService    │ │
                                                      │  └─────────┬────────────────┘ │
                                                      │            │                   │
                                                      │   ┌────────▼──────┐            │
                                                      │   │ ARQ workers   │            │
                                                      │   │ (Redis queue) │            │
                                                      │   └──┬────┬───┬───┘            │
                                                      └──────┼────┼───┼────────────────┘
                                                             │    │   │
                          ┌──────────────────────┐          │    │   │
                          │ python-garminconnect  │◄─────────┘    │   │
                          │ (UNOFFICIAL, fragile) │  scrape/login  │   │
                          │  → Garmin Connect      │               │   │
                          └──────────────────────┘                │   │
                          ┌──────────────────────┐                │   │
                          │ Anthropic Claude API  │◄───────────────┘   │
                          │ (Sonnet / Opus)       │                    │
                          └──────────────────────┘                    │
                          ┌──────────────────────┐                    │
                          │ Resend (email)        │◄───────────────────┘
                          └──────────────────────┘
                          ┌──────────────────────┐
                          │ Paddle (payments,MoR) │──webhook──► FastAPI /webhooks/paddle
                          └──────────────────────┘
```

### 1.2 Component breakdown

**Next.js 15 frontend (`web/`)**
- App Router. Server Components for data-heavy pages (dashboard, activity detail) fetching from FastAPI server-side; Client Components for interactive bits (chat, charts, forms, accordions).
- `@supabase/ssr` for auth session (cookies). The Supabase access token is forwarded as `Authorization: Bearer <jwt>` on every call to FastAPI.
- Deployed to Vercel. Marketing pages (`/`, `/pricing`) are static/ISR; app pages are dynamic + auth-gated by middleware.
- **Does NOT talk to Garmin, Claude, or Paddle's API directly** (except Paddle.js client-side checkout overlay). All domain logic is behind FastAPI.

**FastAPI backend (`api/`)**
- The **only** place python-garminconnect, the LLM calls, and the analytics math live.
- Synchronous REST for reads; enqueues ARQ jobs for slow work (import, analysis, plan gen, email).
- Validates Supabase JWT on every protected route.
- Deployed to Fly.io/Railway in an EU region. One web process + one worker process + Redis.

**Supabase**
- **Auth (GoTrue)**: email/password + Google OAuth. Issues JWTs.
- **PostgreSQL**: all domain tables (§2). RLS enabled.
- We use Supabase purely as managed Postgres + Auth; we do NOT use Supabase Edge Functions (logic lives in FastAPI).

**Third-party**
- Anthropic Claude (AI), Resend (email), Paddle (payments), Mapbox (activity maps), Upstash/Fly Redis (queue + cache).

### 1.3 Data flow: Garmin import → storage → analytics → AI → frontend

```
1. User clicks "Connect Garmin" (onboarding).
2. Frontend POST /garmin/connect  { email, password }  (over HTTPS; never stored raw, see A5)
3. FastAPI: python-garminconnect login → obtains token → encrypt → store in garmin_connections.
4. FastAPI enqueues ARQ job `import_garmin_history(user_id)`; returns 202 + job_id.
5. Frontend polls GET /garmin/import-status/{job_id} → drives the progress UI
   ("Fetching activities..." → "Analyzing metrics..." → "Building dashboard...").
6. Worker:
   a. Pull activities (paginated) + daily health metrics via python-garminconnect.
   b. Upsert into activities + activity_metrics + daily_health (idempotent on garmin_activity_id).
   c. Run AnalyticsEngine → compute per-activity TSS, rolling CTL/ATL/TSB → write training_load_daily.
   d. Enqueue per-activity AI analysis (Premium only) + dashboard "Coach's Note".
7. AnalyticsEngine is pure Python (deterministic, unit-tested). NO AI in the numbers.
8. AI layer (LLMProvider) consumes computed metrics (never raw streams) → narrative analysis,
   chat answers, plan generation. Output cached in ai_analyses / chat_messages / training_plans.
9. Frontend reads computed + AI results via REST and renders dashboard/charts/chat.
```

Key principle: **the AI never computes numbers.** All metrics (distance sums, TSS, CTL/ATL/TSB, pace, trends) are computed deterministically by `AnalyticsEngine` and passed to the LLM as structured facts. This kills the #1 hallucination class (invented metrics — QA A4.3, C3.2) and makes analytics unit-testable.

### 1.4 Where python-garminconnect lives & how Next.js talks to FastAPI

- python-garminconnect lives **only** in `api/app/integrations/garmin/`, wrapped behind a `GarminProvider` Protocol. Nothing else imports it. Swapping to the official Garmin API later = one new implementation of the interface.
- Next.js → FastAPI: plain `fetch` with `Authorization: Bearer <supabase_jwt>`. Server Components call FastAPI server-side (token read from cookies); Client Components call through a thin typed API client that injects the token. CORS on FastAPI allows only the Vercel origin(s).

---

## 2. Data Model (PostgreSQL / Supabase)

All tables in schema `public`, owned by Alembic (A11). `auth.users` is Supabase's. Domain `users` row is 1:1 with `auth.users.id`.

### 2.1 Tables

**`users`** — app profile (mirrors `auth.users`)
| col | type | notes |
|-----|------|-------|
| id | uuid PK | = `auth.users.id` (FK, on delete cascade) |
| email | text not null | mirror, read-only in UI |
| first_name | text | |
| last_name | text | |
| units | text not null default `'metric'` | `'metric'` \| `'imperial'` |
| created_at | timestamptz default now() | |
| updated_at | timestamptz | |

**`garmin_connections`** — one per user (A5)
| col | type | notes |
|-----|------|-------|
| user_id | uuid PK FK→users | |
| garmin_username | text | display only |
| token_ciphertext | bytea not null | encrypted token blob (envelope enc, AES-GCM) |
| token_nonce | bytea not null | |
| status | text not null | `'connected'` \| `'expired'` \| `'error'` \| `'disconnected'` |
| last_sync_at | timestamptz | |
| last_error | text | for diagnostics, never returned to client |
| created_at | timestamptz default now() | |

**`activities`**
| col | type | notes |
|-----|------|-------|
| id | uuid PK default gen_random_uuid() | |
| user_id | uuid FK→users not null | |
| garmin_activity_id | bigint not null | dedupe key |
| sport | text not null | `'run'` \| `'ride'` \| `'swim'` \| `'other'` |
| sub_sport | text | trail, treadmill, track… |
| start_time | timestamptz not null | |
| timezone | text | |
| name | text | "Morning Run" |
| distance_m | numeric | |
| duration_s | integer | |
| moving_duration_s | integer | |
| elevation_gain_m | numeric | |
| avg_hr | integer | |
| max_hr | integer | |
| avg_pace_s_per_km | numeric | derived, stored for sort/filter |
| avg_power_w | integer | |
| avg_cadence | integer | |
| calories | integer | |
| training_effect_aerobic | numeric | |
| training_effect_anaerobic | numeric | |
| has_gps | boolean default false | |
| tss | numeric | computed by AnalyticsEngine (§ below) |
| created_at | timestamptz default now() | |
| **UNIQUE (user_id, garmin_activity_id)** | | idempotent imports (DI1) |

**`activity_metrics`** — heavy per-activity time series & laps (kept out of `activities` for row size)
| col | type | notes |
|-----|------|-------|
| activity_id | uuid PK FK→activities | |
| streams | jsonb | downsampled arrays: time, hr, pace, elevation, power, cadence (for the chart, screen-spec §5.4) |
| laps | jsonb | array of {lap_no, distance_m, duration_s, avg_hr, elevation_m} |
| gps_polyline | text | encoded polyline for the map (§5.2) |
| raw | jsonb | trimmed raw payload for re-processing |

**`daily_health`** — sleep / HRV / stress / body battery per day
| col | type | notes |
|-----|------|-------|
| id | uuid PK | |
| user_id | uuid FK not null | |
| date | date not null | |
| sleep_score | integer | |
| sleep_duration_s | integer | |
| hrv_ms | integer | |
| resting_hr | integer | |
| stress_avg | integer | |
| body_battery_high | integer | |
| body_battery_low | integer | |
| recovery_score | integer | derived (§ recovery) |
| **UNIQUE (user_id, date)** | | |

**`training_load_daily`** — computed PMC series
| col | type | notes |
|-----|------|-------|
| user_id + date | composite PK | |
| daily_tss | numeric | sum of activity TSS that day |
| ctl | numeric | 42-day exp-weighted (fitness) |
| atl | numeric | 7-day exp-weighted (fatigue) |
| tsb | numeric | ctl − atl (form) |

**`ai_analyses`** — cached LLM outputs for activities & dashboard note
| col | type | notes |
|-----|------|-------|
| id | uuid PK | |
| user_id | uuid FK not null | |
| kind | text not null | `'activity'` \| `'dashboard_note'` \| `'weekly_email'` |
| activity_id | uuid FK nullable | set for kind='activity' |
| model | text not null | provenance |
| prompt_version | text not null | for reproducibility/audit |
| content | jsonb not null | structured {good, concern, recommendation} + rendered markdown |
| created_at | timestamptz default now() | |
| UNIQUE (activity_id) WHERE kind='activity' | | one analysis per activity, regen replaces |

**`chat_sessions`**
| col | type | notes |
|-----|------|-------|
| id | uuid PK | |
| user_id | uuid FK not null | |
| title | text | first user message, truncated |
| created_at, updated_at | timestamptz | |

**`chat_messages`**
| col | type | notes |
|-----|------|-------|
| id | uuid PK | |
| session_id | uuid FK→chat_sessions not null | |
| role | text not null | `'user'` \| `'assistant'` \| `'system'` |
| content | text not null | |
| context_ref | jsonb | e.g. {activity_id} when launched from an activity (§6.4) |
| tokens_in / tokens_out | integer | cost tracking + free-quota enforcement |
| created_at | timestamptz default now() | |

**`training_plans`**
| col | type | notes |
|-----|------|-------|
| id | uuid PK | |
| user_id | uuid FK not null | |
| goal_race | text | `'5k'`\|`'10k'`\|`'half'`\|`'marathon'` |
| race_date | date | |
| target_time_s | integer nullable | |
| days_per_week | integer | 3–6 |
| level | text | beginner/intermediate/advanced |
| status | text | `'active'` \| `'archived'` |
| model, prompt_version | text | provenance |
| created_at | timestamptz | |

**`plan_workouts`** — one row per planned day
| col | type | notes |
|-----|------|-------|
| id | uuid PK | |
| plan_id | uuid FK→training_plans not null | |
| date | date not null | |
| week_index | integer | 1..N |
| phase | text | base/build/peak/taper |
| workout_type | text | easy/tempo/interval/long/rest/cross |
| description | text | "Easy Run: 8km @ 5:15-5:30/km, Z2" |
| planned_distance_m | numeric | |
| planned_duration_s | integer | |
| status | text default `'planned'` | planned/completed/missed/adapted |
| completed_activity_id | uuid FK nullable | matched on adapt |
| coach_note | text | per-day IA note (§7.3) |

**`subscriptions`** (Paddle)
| col | type | notes |
|-----|------|-------|
| user_id | uuid PK FK→users | |
| paddle_customer_id | text | |
| paddle_subscription_id | text | |
| plan | text not null default `'free'` | `'free'` \| `'premium'` |
| billing_period | text | `'monthly'` \| `'annual'` |
| status | text | `'active'`\|`'past_due'`\|`'cancelled'`\|`'paused'` |
| current_period_end | timestamptz | |
| updated_at | timestamptz | |

**`usage_counters`** — free-tier quota (chat, analyses)
| col | type | notes |
|-----|------|-------|
| user_id + period_month | composite PK | |
| chat_messages_count | integer default 0 | |
| ai_analyses_count | integer default 0 | |

**`jobs`** — track ARQ jobs surfaced to UI (import status)
| col | type | notes |
|-----|------|-------|
| id | uuid PK (= ARQ job id) | |
| user_id | uuid FK | |
| kind | text | `'import'`\|`'analysis'`\|`'plan'` |
| status | text | queued/running/step:* /done/failed |
| progress_label | text | drives onboarding progress text |
| error | text | |
| created_at, updated_at | timestamptz | |

**`audit_log`** (GDPR / security)
| col | type | notes |
|-----|------|-------|
| id, user_id, action, meta jsonb, created_at | | export/delete/disconnect events |

### 2.2 Relationships (summary)
- `auth.users (1) ─ (1) users (1) ─ (0..1) garmin_connections`
- `users (1) ─ (N) activities (1) ─ (1) activity_metrics`
- `users (1) ─ (N) daily_health`, `(N) training_load_daily`
- `users (1) ─ (N) chat_sessions (1) ─ (N) chat_messages`
- `users (1) ─ (N) training_plans (1) ─ (N) plan_workouts`
- `users (1) ─ (1) subscriptions`, `(N) ai_analyses`, `(N) jobs`

### 2.3 Indexes
- `activities (user_id, start_time DESC)` — dashboard recent list & range queries.
- `activities (user_id, sport, start_time DESC)` — type filter (D5.5).
- partial unique `ai_analyses (activity_id) WHERE kind='activity'`.
- `daily_health (user_id, date)`, `training_load_daily (user_id, date)` — PK covers it.
- `chat_messages (session_id, created_at)`.
- `plan_workouts (plan_id, date)`.

### 2.4 Constraints
- All `user_id` FKs `ON DELETE CASCADE` → account deletion purges everything (DI2, ST5.5).
- CHECK constraints on enums (`sport`, `plan`, `status`, `units`).
- `activities.distance_m >= 0`, `duration_s >= 0`.

### 2.5 AnalyticsEngine formulas (deterministic, unit-tested)
- **TSS (run, HR-based fallback)**: hrTSS = (duration_s × avg_hr_fraction² ) / 3600 × 100, where `avg_hr_fraction = (avg_hr − resting_hr)/(threshold_hr − resting_hr)`. Power-based TSS used for rides when power present. Documented thresholds; conservative defaults when HR zones unknown.
- **CTL** = yesterday_CTL + (daily_TSS − yesterday_CTL)/42.
- **ATL** = yesterday_ATL + (daily_TSS − yesterday_ATL)/7.
- **TSB** = yesterday_CTL − yesterday_ATL.
- **Recovery score (0–100)**: weighted blend of sleep_score, HRV vs personal baseline, resting HR vs baseline, body battery. Documented weights; defaults conservative.
- Trend % = (this_week − last_week)/last_week, with null-safe handling when last_week is empty (D3.5).

### 2.6 Migration strategy
- **Alembic** in `api/`. `alembic revision --autogenerate` from SQLAlchemy models; reviewed by hand. `alembic upgrade head` in CI/deploy.
- **Supabase migrations** (in `supabase/migrations/`) own ONLY: enabling RLS, RLS policies, and any `auth` triggers (e.g. a trigger that inserts a `public.users` row when `auth.users` is created).
- One source of truth per object → no drift. Document the boundary in `api/README`.
- Seed/fixtures for tests via factory_boy + a disposable test Postgres (or Supabase branch DB).

---

## 3. API Contract

Base URL: `https://api.endurancecoach.app`. All protected routes require `Authorization: Bearer <supabase_jwt>`. JSON everywhere. Errors use a uniform envelope.

### 3.1 Error envelope & conventions
```json
{ "error": { "code": "string", "message": "human readable", "details": {} } }
```
- 401 → frontend redirects to `/login` ("Session expired", QA U6.3).
- 403 → premium-gated resource for free user (`code: "premium_required"`).
- 429 → rate-limited or free quota exhausted (`code: "quota_exceeded"`, U6.4, C5.4).
- 202 → async job accepted, returns `{ job_id }`.

### 3.2 Auth model (Supabase JWT validated by FastAPI)
- Supabase issues a JWT on login. Frontend stores session via `@supabase/ssr` (httpOnly cookies).
- FastAPI dependency `get_current_user`:
  1. Extract Bearer token.
  2. Verify signature. **Preferred**: fetch Supabase JWKS (`/.well-known/jwks.json`) and verify the asymmetric (ES256/RS256) signature, caching keys. Fallback for projects using the legacy shared secret: HS256 with `SUPABASE_JWT_SECRET`.
  3. Validate `aud`, `exp`, `iss`.
  4. `sub` = user id → load/`get_or_create` `public.users` row.
- No session state in FastAPI; pure token verification. Service-role DB key used by FastAPI; **never** exposed to the browser.
- Webhooks (Paddle) are unauthenticated by JWT but verified by **Paddle signature** (`Paddle-Signature` HMAC).

### 3.3 Endpoints

**Auth / profile**
| Method | Path | Body / Query | Returns | Notes |
|--------|------|------|---------|-------|
| GET | `/me` | — | user profile + subscription + garmin status | bootstrap call for app shell |
| PATCH | `/me` | `{first_name?, last_name?, units?}` | updated profile | ST1 |
| GET | `/me/goal` | — | `{goal_type, goal_target, config_version}` | A13/A15; drives the dashboard variant the app shell renders |
| PATCH | `/me/goal` | `{goal_type, goal_target?}` | updated goal | A13/A15; set by conversational onboarding (Screen 3.5). `goal_type ∈ {marathon, weightloss, health, hyrox, triathlon}`. May trigger plan refresh + dashboard re-lens. |
| POST | `/me/goal-race` | `{goal_race, race_date, target_time_s?}` | goal-race | ST2; race-specific detail for the marathon/running lens; may trigger plan refresh |

> Signup/login/forgot-password are handled **client-side by Supabase Auth SDK**, not FastAPI. FastAPI only consumes the resulting JWT. (Screen-spec §2 maps to Supabase flows.)

**Garmin**
| Method | Path | Body | Returns | Notes |
|--------|------|------|---------|-------|
| POST | `/garmin/connect` | `{email, password}` | `202 {job_id}` | login + enqueue full import (US1). Password used once, never stored (A5). Handles MFA error → `code: garmin_mfa_required`. |
| GET | `/garmin/status` | — | `{status, last_sync_at}` | ST3.1/3.2 |
| GET | `/garmin/import-status/{job_id}` | — | `{status, progress_label, error?}` | drives onboarding progress (O2.2/2.3) |
| POST | `/garmin/sync` | — | `202 {job_id}` | incremental sync (ST3.3) |
| POST | `/garmin/disconnect` | — | `{status:'disconnected'}` | keeps data (ST3.6) |

**Activities**
| Method | Path | Query | Returns |
|--------|------|-------|---------|
| GET | `/activities` | `?q=&sport=&date_from=&date_to=&has_analysis=&sort=&order=&limit=&cursor=` | paginated/filterable/searchable list (D5; full browse = US9). `sort∈{date,distance,duration}` (whitelisted), keyset cursor. |
| GET | `/activities/{id}` | — | full detail incl. streams, laps, polyline, metrics + comparisons (A2/A3/A5) |
| GET | `/activities/{id}/analysis` | — | cached AI analysis or `202` if generating (A4) |
| POST | `/activities/{id}/analysis:regenerate` | — | `202 {job_id}` | premium |

**Analytics / dashboard**
| Method | Path | Query | Returns |
|--------|------|-------|---------|
| GET | `/dashboard` | `?week=current` | `{week_summary{distance,duration,load,recovery + trends}, ai_note, recent_activities[]}` (D2–D6) |
| GET | `/analytics/training-load` | `?weeks=4` | PMC series (CTL/ATL/TSB) for chart (D4) |

**Chat**
| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/chat/sessions` | — | sessions list |
| POST | `/chat/sessions` | `{context_ref?}` | new session (welcome message generated, C5.2) |
| GET | `/chat/sessions/{id}/messages` | `?cursor=` | paginated history (C4) |
| POST | `/chat/sessions/{id}/messages` | `{content}` | streamed assistant reply (SSE) | quota-checked (C5.4); premium for unlimited |
| GET | `/chat/suggestions` | — | dynamic suggested questions (C2) |

**Training plans**
| Method | Path | Body | Returns |
|--------|------|------|---------|
| GET | `/plans/active` | — | active plan + workouts, or 404 |
| POST | `/plans` | `{goal_race,race_date,target_time_s?,days_per_week,level}` | `202 {job_id}` (P1) |
| POST | `/plans/{id}:adapt` | — | `202 {job_id}` (P4) |
| GET | `/plans/{id}/week/{week_index}` | — | week detail (P3) |

**Subscriptions (Paddle)**
| Method | Path | Body | Returns | Notes |
|--------|------|------|---------|-------|
| GET | `/subscription` | — | current plan/status | ST4 |
| POST | `/subscription/checkout` | `{price_id}` | `{checkout_txn_id}` | opens Paddle.js overlay (PR2) |
| GET | `/subscription/portal` | — | `{portal_url}` | manage/cancel |
| POST | `/webhooks/paddle` | Paddle event | `200` | **signature-verified**; updates `subscriptions` on `subscription.created/updated/cancelled`, `transaction.completed` |

**GDPR**
| Method | Path | Returns | Notes |
|--------|------|---------|-------|
| POST | `/gdpr/export` | `202 {job_id}` then downloadable JSON+CSV bundle | ST5.1/DI3 |
| DELETE | `/gdpr/account` | `200` | hard-delete cascade; revoke Garmin token; audit log (ST5.5/DI2) |

### 3.4 Representative response shapes
`GET /dashboard`:
```json
{
  "week": { "start": "2026-06-16", "end": "2026-06-22" },
  "summary": {
    "distance_m": 42300, "distance_trend_pct": 12,
    "duration_s": 13320, "duration_trend_pct": 8,
    "training_load_tss": 487, "load_trend": "stable", "load_zone": "optimal",
    "recovery": 82, "recovery_trend_pct": 5
  },
  "ai_note": { "text": "Your training load is well balanced...", "generated_at": "..." },
  "recent_activities": [
    { "id": "uuid", "sport": "run", "start_time": "...", "name": "Morning Run",
      "distance_m": 12400, "duration_s": 3272, "avg_pace_s_per_km": 264,
      "avg_hr": 152, "has_analysis": true }
  ]
}
```

---

## 4. User Stories → Dev Tasks (TDD)

Conventions for every task:
- Cycle = **RED** (write failing test) → **GREEN** (minimal code to pass) → **REFACTOR** → **COMMIT**.
- Each task ≈ 2–5 min of focused work.
- Backend tests: `cd api && pytest <path> -q`. Frontend tests: `cd web && pnpm vitest run <path>`.
- Lint/build gates per QA: `pnpm lint`, `pnpm build`, `pytest`, `vitest` all green before story sign-off (qa-checklist §QA Process).
- After each story: run the **QA-manual checks** for the relevant screen + **regression** (RG1–RG8).

> **Story list (17 stories, build order):** S0 → US10 → US12 → US7a → US7b → US1 → **US1b** → **US13** → US2 → US9 → US3 → US4 → US5 → **US5b** → US8 → US6 → US11a → US11b.
> Foundational stories — **S0** (scaffold/CI/auth), **US10** (app shell/nav/redirects) and **US12** (global states/toasts/errors) — must precede all feature screens, since every app page renders inside the US10 shell and consumes US12 states.
> New for the interactive prototype: **US1b** (conversational onboarding coach), **US13** (modular goal architecture — backend goal field + per-lens dashboard config), **US5b** (Push to Watch). US10's app shell now builds the **bottom nav (mobile, 4 tabs: Progress/Coach/Plan/More)** and the **desktop sidebar (240px)**.

> **New stories detail:**
> - **US1b — Conversational onboarding coach (P0, after US1).** *Screen 3.5 (`/coachonboard`). Depends on US1 (import done → counts to reference) + US4 chat UI primitives. A15.* After import, the coach opens a chat referencing the imported Garmin data and walks the athlete to a goal via a state machine (welcome → goal kind → goal-specific follow-ups → hand-off CTA). Suggestion chips (Race/Weight Loss/Hyrox/Triathlon/Health/Not sure) + free text → `classifyGoal()` keyword routing with graceful catch-all. On hand-off, `PATCH /me/goal` then route to the matching dashboard variant. Tests: each branch reaches a goal; free text classified; catch-all path; chip == free-text engine; goal persisted. QA: new "Onboarding Coach Chat" section.
> - **US13 — Modular goal architecture (P0, backend support, before US2).** *A13. Backend goal field + per-goal dashboard config so the dashboard, coach focus and "success" definition adapt by `goal_type`.* `GET/PATCH /me/goal` (§3); `/dashboard` returns a goal-typed payload; dashboard variant selected by `goal_type` (marathon/weightloss/health fully; hyrox/triathlon reuse health/hybrid lens). Tests: goal CRUD; dashboard payload differs by goal; default goal; unknown goal falls back. QA: "Goal-specific dashboards" per variant.
> - **US5b — Push to Watch (P1, after US5).** *Screen §7.4. A14. Extends `GarminProvider` with workout upload/schedule (mocked in tests).* Endpoint `POST /plans/{id}/week/{week_index}:push-to-watch` → async job → marks the week pushed; `GarminProvider.push_workouts()` behind the interface; only current+future weeks. Frontend: "Send This Week to Watch" CTA → confirm modal → sending/success(banner + per-day watch icons)/error+retry. Tests: provider called with structured workouts; idempotent re-send; error→retry; past weeks reject. QA: "Push to Watch" section.

### Story 0 — Project scaffold & CI (prereq)
- **0.1** RED: add `api/tests/test_health.py::test_health_returns_200`. GREEN: FastAPI `GET /health`. Verify `pytest -q`. COMMIT.
- **0.2** Configure Alembic + SQLAlchemy base; test `test_migrations_run` spins up test DB and runs `upgrade head`. COMMIT.
- **0.3** `web/`: Next.js 15 App Router + Tailwind + shadcn/ui init; vitest config; test `home.test.tsx` renders a placeholder. COMMIT.
- **0.4** Supabase client (`@supabase/ssr`) + middleware redirecting unauthenticated app routes to `/login` (test middleware logic). COMMIT.
- **0.5** FastAPI `get_current_user` dependency. RED: `test_jwt_invalid_returns_401`, `test_jwt_valid_returns_user` (mint a test JWT with the test secret/JWKS). GREEN. COMMIT.
- **0.6** CORS config (Vercel origin only) + error-envelope exception handler; tests. COMMIT.
- **0.7** CI workflow (GitHub Actions): pytest + vitest + build + lint matrix. COMMIT.

### US10 — App shell, navigation & auth-aware redirects (P0, foundational)
*Transverse — every app page renders inside this shell. Screen-spec "Architecture de navigation" + §4.1 (Top Bar) + §3 skip-banner (O4) + Global States "Auth expired". QA D1, O4, U2.4/U2.5, U5.1–U5.3, RG4. Absorbs old tasks 0.4 (middleware) and 2.11 (top bar) so nav is built once.*
- **10.1** Route groups: `web/app/(app)/layout.tsx` (auth-gated app shell) vs `web/app/(marketing)/layout.tsx` (public). RED `layout-routing.test.tsx`: app routes render the shell chrome, marketing routes do not. GREEN. COMMIT.
- **10.2** Shell bootstrap: server-side `GET /me` (profile + subscription + garmin status) feeds the layout. RED `test_shell_fetches_me`; GREEN typed fetch in app layout. COMMIT. (§3.3 `/me`)
- **10.3** `TopBar` (logo→`/dashboard`, nav `Dashboard`/`Coach`/`Plan` with labels, avatar dropdown). Test renders links + correct hrefs. COMMIT. (D1.1)
- **10.4** Free/Premium badge (gold premium, gray "Free"→`/pricing`); test badge variant by subscription plan. COMMIT. (D1.4)
- **10.5** Mobile bottom-nav (icons only, ≥44×44px) + desktop top-nav; test breakpoint visibility (`Sheet` for mobile menu). COMMIT. (D1.2, U2.4/U2.5)
- **10.6** Auth-aware middleware (extends old 0.4): unauthenticated app route→`/login`; valid session but `garmin.status='disconnected'`→ render onboarding banner (not redirect). RED `middleware.test.ts` both branches. GREEN. COMMIT. (U6.3, O4.2)
- **10.7** No-Garmin yellow banner in shell ("Connect your Garmin to unlock full analytics →"→`/onboarding`); test shows only when disconnected + clickable. COMMIT. (O4.2/O4.3)
- **10.8** Avatar dropdown actions: `Settings`→`/settings`, `Upgrade`→`/pricing` (free only), `Logout`→ Supabase `signOut`→`/login`; tests each. COMMIT. (D1.3, ST6.1)
- **10.9** Active-nav state (`aria-current`) + keyboard a11y (Tab order, Enter/Space activate, Esc closes dropdown); tests. COMMIT. (U5.1–U5.3)
- **10.10** QA manual D1, O4, U2.5, RG4 (every nav link resolves). COMMIT.

### US12 — Global states & error handling (P0, foundational)
*Transverse — used by every screen. Screen-spec "États Globaux" (Loading/Empty/Error) + Error States (404/500/auth-expired/API-down) + Toast micro-interaction. QA U3.1–U3.3, U6.3–U6.5. Absorbs old task G.5. Build before any data screen so they can consume it.*
- **12.1** Toast system (shadcn Sonner) provider in root layout + `toast.{success,error,info}` helper; test render + 4s auto-dismiss + slide-in. COMMIT. (micro-interactions)
- **12.2** Typed API client wrapper: injects `Bearer` token, parses the error envelope (§3.1), maps `code`→typed errors (401/403/429/5xx). RED `api-client.test.ts` per code; GREEN. COMMIT.
- **12.3** Auth-expired: client intercepts 401 → redirect `/login` + "Session expired. Please log in again." toast. Test interceptor. COMMIT. (U6.3, Error States §)
- **12.4** Rate-limit/quota: 429 (`quota_exceeded`) → toast + (where relevant) Upgrade CTA. Test mapping. COMMIT. (U6.4)
- **12.5** API-down banner: fetch failure/timeout → red `Alert` "We're having trouble connecting. Retrying in 10s…" + live countdown + auto-retry. Test countdown + retry fires. COMMIT. (U6.5)
- **12.6** `web/app/not-found.tsx` (404): "Page not found" + link→`/dashboard`; test renders + link. COMMIT.
- **12.7** `web/app/error.tsx` (500 boundary): "Something went wrong" + `Try Again` + `Contact Support`; test renders + retry resets boundary. COMMIT.
- **12.8** Shared `EmptyState`/`ErrorState`/`LoadingSkeleton` primitives (§5.3) consumed by all screens; render tests. COMMIT. (U3.1–U3.3)
- **12.9** QA manual U3.1–U3.3, U6.3–U6.5. COMMIT.

### US7a — Landing page (P0, build early; no backend dependency)
*Screen 1. QA L1–L7 + U1–U5. Fully parallel to backend (US1).*
- **7a.1** RED `landing-hero.test.tsx`: H1 "Your Garmin data, finally decoded." + subheadline + primary CTA→`/signup` + secondary "See how it works ↓" anchor. GREEN `app/(marketing)/page.tsx` hero (dynamic social-proof count if >0). COMMIT. (L1)
- **7a.2** How-It-Works (3 steps + icons); test 3 steps render + 3-col→1-col order. COMMIT. (L2)
- **7a.3** Features 3-col + per-feature bullet list; test columns + bullets. COMMIT. (L3)
- **7a.4** Comparison table (4 competitors), our column highlighted; test highlight class + horizontal-scroll wrapper + a11y. COMMIT. (L4)
- **7a.5** Pricing section with Monthly/Annual toggle + "Save 18%" badge; test toggle updates price + CTAs→`/signup`. COMMIT. (L5)
- **7a.6** Testimonials (3 cards; pre-launch founder + "Be one of the first" fallback variant); test cards + fallback. COMMIT. (screen-spec §1.7 — was missing from the original plan)
- **7a.7** FAQ accordion (shadcn `Accordion`, single-open); test expand/collapse + one-open. COMMIT. (L6)
- **7a.8** Footer (anchor links + Privacy/Terms/Contact page links + dynamic ©2026); test links present. COMMIT. (L7)
- **7a.9** Responsive (375/768/1440) + a11y pass (labels, tab order, contrast ≥4.5:1); component tests + manual U1–U5, L1–L7. COMMIT.

### US7b — Signup / Login / Forgot password (P0, build early; no backend data dependency)
*Screen 2. QA S1–S3. Auth handled client-side by Supabase Auth SDK (§3.2); FastAPI only consumes the JWT.*
- **7b.1** Signup form (Supabase `signUp`): email + password(min8) + visibility toggle + "or Continue with Google" + "Already have an account?"→`/login`. RED validation-state tests. GREEN. COMMIT. (S1.1–S1.4/S1.8)
- **7b.2** Signup error/success: email-exists→message + login link; loading spinner; success→redirect `/onboarding`. Tests. COMMIT. (S1.5/S1.6/S1.7)
- **7b.3** Login form + invalid-creds error + redirect logic (`/dashboard`, or `/onboarding` if no Garmin); "Don't have an account?"→`/signup`. Tests. COMMIT. (S2)
- **7b.4** Forgot-password (Supabase reset) with no-info-leak message ("If this email exists, we sent a link") + "Back to login". Test. COMMIT. (S3)
- **7b.5** Responsive + a11y pass (375/768/1440; labels, `aria-describedby` on field errors, tab order); component tests + manual U1–U5, S1–S3. COMMIT.

### US1 — Garmin OAuth/credential import (P0)
*Screen 3. QA O*, plus DI1, SEC4.*
- **1.1** RED `test_garmin_provider_login_caches_token` against a **mocked** garminconnect client. GREEN: `GarminProvider.login()` wrapper. COMMIT.
- **1.2** Envelope encryption util: `test_encrypt_decrypt_roundtrip`, `test_ciphertext_differs`. GREEN AES-GCM helper. COMMIT. (A5)
- **1.3** `POST /garmin/connect`: RED `test_connect_stores_encrypted_token_and_enqueues_job` (mock provider + fake queue). GREEN. COMMIT.
- **1.4** MFA/locked-account handling: `test_connect_mfa_returns_garmin_mfa_required`. GREEN map exceptions → typed errors. COMMIT. (defensive, §7)
- **1.5** Import job — activities: RED `test_import_upserts_activities_idempotent` (run twice → no dupes, UNIQUE works). GREEN worker step. COMMIT. (DI1)
- **1.6** Import job — daily health upsert; test idempotent. COMMIT.
- **1.7** Import job — streams/laps/polyline into `activity_metrics` (downsample test: long stream → capped length). COMMIT.
- **1.8** Job status writes (`progress_label` transitions): test sequence "Fetching…"→"Analyzing…"→"Building…". GREEN. COMMIT. (O2.3)
- **1.9** `GET /garmin/import-status/{job_id}` + `/garmin/status`; tests. COMMIT.
- **1.10** `/garmin/sync` incremental (only activities after last_sync); test boundary. COMMIT. (ST3.3)
- **1.11** `/garmin/disconnect` sets status, keeps data; test. COMMIT. (ST3.6)
- **1.12** Frontend onboarding screen: Connect form, "I'll do this later" skip, reassurance text; tests render + skip→dashboard banner. COMMIT. (O1/O4)
- **1.13** Frontend import progress (poll import-status, animated steps) + error/retry; tests for each state. COMMIT. (O2/O3)
- **1.14** Defensive: retry/backoff + circuit-breaker around provider; `test_provider_retries_then_marks_error`. COMMIT. (§7)
- **1.15** QA manual O1–O4 + DI1 (compare 3 activities vs Garmin Connect) + SEC4 (token absent from any API response: test). COMMIT.

### US2 — Dashboard analytics (P0)
*Screen 4. QA D*. Depends on US1 data.*
- **2.1** AnalyticsEngine TSS: RED `test_tss_known_input` (fixed inputs → expected). GREEN pure function. COMMIT.
- **2.2** CTL/ATL/TSB recurrence: `test_pmc_series_matches_reference`. GREEN. COMMIT.
- **2.3** Recovery score blend: `test_recovery_score_bounds_and_weights`. GREEN. COMMIT.
- **2.4** Weekly summary aggregation + trend %, null-safe last-week: tests incl. empty last week (D3.5). GREEN. COMMIT.
- **2.5** `GET /dashboard` assembles summary + recent + (placeholder note); contract test. COMMIT.
- **2.6** `GET /analytics/training-load`; test shape + zone classification. COMMIT.
- **2.7** Metric cards component (4 cards, trend colors); tests value+trend color mapping (D3.4). COMMIT.
- **2.8** Training-load chart (Recharts) with zones, legend, tooltip; test renders series + "<2 weeks" empty state (D4.6). COMMIT.
- **2.9** Recent activities list + type filters (only present types) + AI badge; tests (D5.5/D5.6). COMMIT.
- **2.10** Dashboard states: skeleton, empty (no Garmin / 0 activities), error+retry; tests each (D7). COMMIT.
- **2.11** Mount dashboard inside the app shell (US10): `Dashboard` nav active-state, Free/Premium badge reflects live subscription, "Upgrade" visible only for free; tests (D1.4). *(Top bar/nav itself is built in US10 — this task is the dashboard's integration into it.)* COMMIT.
- **2.12** QA manual D1–D7 incl. verifying sums against raw (D3.2). COMMIT.

### US9 — Activity history / browse (P1)
*New screen `/activities` — the dashboard "Recent Activities" widget (screen-spec §4.5) promoted to a full page. Depends on US1 data + US2 list components + US10 shell + US12 states. QA: extends D5 (filters, AI badge, click-through) + full U1–U6 on the new page.*

**Screen — Activity History (`web/app/(app)/activities/page.tsx`):** full-width paginated list reusing `ActivityRow`; sticky controls bar with a search box (by activity name), filter chips (sport type, date range, "has AI analysis"), and a sort control (date / distance / duration, asc/desc); infinite scroll (load-more on scroll, not a 10-item cap). States: skeleton (initial), empty ("No activities match your filters"), end-of-list marker, error+retry. Reached from the dashboard "View all →".
- **9.1** Backend: extend `GET /activities` with `q, sport, date_from, date_to, has_analysis, sort, order, cursor, limit`. RED contract tests per filter + combined. GREEN router + service. COMMIT. (D5.5/D5.6)
- **9.2** Backend: name search (`ILIKE`) + sort whitelist (date/distance/duration only — reject arbitrary columns); tests for match + injection-safe sort. COMMIT.
- **9.3** Backend: stable keyset cursor pagination on `(start_time, id)`; `test_cursor_no_dupes_no_gaps` across pages. COMMIT.
- **9.4** Frontend page + infinite scroll (IntersectionObserver fetches next cursor); test "load more" appends without dupes. COMMIT.
- **9.5** Debounced search input → `q`; test typing updates results + clear resets. COMMIT.
- **9.6** Filters: sport tabs (only present types, D5.6), date-range picker, has-AI toggle; test filters apply + combine + reset. COMMIT.
- **9.7** Sort control (field + direction) persisted in the query string; test reorders list. COMMIT.
- **9.8** States: skeleton, empty-no-match, end-of-list, error+retry (reuse US12 primitives); tests each. COMMIT. (U3)
- **9.9** Dashboard "View all →" link → `/activities`; AI badge + row click → `/activity/{id}` preserved; tests. COMMIT. (D5.3/D5.4)
- **9.10** QA manual: D5 on the full page + universal U1–U6. COMMIT.

### US3 — AI activity analysis (P0)
*Screen 5. QA A4. Depends on US2 metrics.*
- **3.1** LLMProvider interface + Anthropic impl behind it; `test_llmprovider_called_with_structured_facts` (mock). GREEN. COMMIT.
- **3.2** Prompt builder: takes computed metrics + comparisons, **never raw streams**; `test_prompt_contains_no_invented_fields` + golden prompt snapshot (`prompt_version`). COMMIT. (A4.3)
- **3.3** Analysis generator job → `ai_analyses` (structured good/concern/recommendation); test persists + UNIQUE replace on regen. COMMIT.
- **3.4** Guardrails: system prompt forbids medical advice; `test_analysis_includes_disclaimer_when_health_flag` + refusal pattern test. COMMIT. (research §B7, C3.5)
- **3.5** Too-short activity (<10min) short-circuits (no LLM call): test. COMMIT. (A4.8)
- **3.6** `GET /activities/{id}` detail (metrics grid + comparisons + streams + laps + polyline); contract tests. COMMIT. (A2/A3/A5)
- **3.7** `GET /activities/{id}/analysis` (cached or 202) + regenerate (premium-gated); tests incl. 403 for free. COMMIT.
- **3.8** Activity detail UI: header, map (Mapbox; fallback icon no-GPS), metrics grid (unit-aware), HR/pace/elev chart, laps table; tests incl. no-GPS + no-HR (A1.5/A3.4/A5.3). COMMIT.
- **3.9** AI analysis UI: loading skeleton, content (3–5 paras), error+retry, "Discuss this run" → `/coach?activity=` ; tests (A4.6/A4.7/A4.5). COMMIT.
- **3.10** QA manual A1–A5 incl. hallucination spot-check (A4.3). COMMIT.

### US4 — Chat coach (P0)
*Screen 6. QA C*. Depends on US2/US3.*
- **4.1** Chat context assembler: pulls recent metrics/PMC/last activities into a compact context; `test_context_includes_user_facts_only`. COMMIT. (C3.1/C6.2)
- **4.2** Streaming chat endpoint (SSE) with history; `test_message_persisted_and_streamed` (mock LLM). COMMIT.
- **4.3** Guardrails reused (no medical advice, "I don't know" when out of scope); tests C3.4/C3.5. COMMIT.
- **4.4** Free quota enforcement on chat (`usage_counters`); `test_free_quota_exceeded_returns_429`. COMMIT. (C5.4)
- **4.5** Welcome message generator (personalized from data); test mentions real counts. COMMIT. (C5.2)
- **4.6** Dynamic suggestions endpoint; test relevance keys present. COMMIT. (C2)
- **4.7** Context injection from activity (`context_ref`); test first message references activity. COMMIT. (C6.1)
- **4.8** Chat UI: bubbles, input, Enter-send / Shift+Enter newline, "thinking…" dots, suggestions; tests (C1.4/C1.5/C5.1). COMMIT.
- **4.9** Chat history pagination + date grouping + >7d styling; tests (C4). COMMIT.
- **4.10** No-Garmin-data state (general answers ok); test. COMMIT. (C5.5)
- **4.11** QA manual C1–C6. COMMIT.

### US5 — Training plan generation (P1)
*Screen 7. QA P*. Depends on US2.*
- **5.1** Plan generator prompt + structured output schema (weeks → workouts); `test_plan_schema_valid` + conservative-load assertion (research §B7 overtraining). COMMIT.
- **5.2** `POST /plans` job → persists `training_plans` + `plan_workouts`; test persistence + week count vs race_date. COMMIT.
- **5.3** Guard: <2 weeks data → 422 with "keep logging" code; test. COMMIT. (P1.5)
- **5.4** Adapt: match completed activities to planned workouts; `test_adapt_marks_completed_missed_adapted`. COMMIT. (P3.5)
- **5.5** `GET /plans/active` + `/week/{i}`; contract tests. COMMIT.
- **5.6** Plan UI: generation form (validation: future date) + loading; tests (P1.1/P1.2). COMMIT.
- **5.7** Timeline (past/current/future weeks) + click→week; tests (P2). COMMIT.
- **5.8** Week view: load bar w/ color thresholds, per-day workout + status + coach note; tests (P3.3/P3.4). COMMIT.
- **5.9** Adapt button + confirm + reload; tests (P4). COMMIT.
- **5.10** QA manual P1–P4. COMMIT.

### US8 — Subscription management (P1, Paddle)
*Screen 9 + Settings §8.4. QA PR*, ST4.*
- **8.1** `GET /subscription`; test default 'free'. COMMIT.
- **8.2** Paddle webhook signature verify: `test_webhook_rejects_bad_signature`, `test_webhook_updates_subscription`. GREEN. COMMIT.
- **8.3** Premium gate dependency `require_premium`: `test_premium_route_403_for_free`. Apply to chat-unlimited/analysis-regen/plans/weekly-email. COMMIT. (A9)
- **8.4** `POST /subscription/checkout` returns Paddle txn; `GET /subscription/portal`; tests. COMMIT.
- **8.5** Pricing/Upgrade page: plans, "Current Plan" badge, toggle, Paddle.js overlay; tests (PR1). COMMIT.
- **8.6** Checkout return handling: success/cancel toasts + badge refresh; tests (PR2.2–2.6). COMMIT.
- **8.7** QA manual PR1–PR2 incl. cancel→back-to-free (E2E.2). COMMIT.

### US6 — Weekly email (P1, premium only)
*Screen 10. QA E*. Depends on US2/US3.*
- **6.1** Weekly digest builder (reuse dashboard summary + AI note + next-week preview); test content shape. COMMIT.
- **6.2** React Email template; snapshot test renders metrics + CTA + unsubscribe. COMMIT. (E1)
- **6.3** "We missed you" variant when 0 activities; test branch. COMMIT. (E2.3)
- **6.4** Scheduler: Monday 07:00 user-timezone, premium-only; `test_schedule_filters_free_users` + tz bucketing test. COMMIT. (E2.1/E2.2)
- **6.5** Resend send + unsubscribe token (one-click); test unsubscribe flips flag. COMMIT. (E3.4)
- **6.6** QA manual E1–E3 (Gmail/Apple/Outlook render check). COMMIT.

### US11a — Settings & profile (P1)
*Screen 8 (Profile, Goal Race, Garmin Connection, Subscription sections). QA ST1–ST4. Backend endpoints (`PATCH /me`, `/me/goal-race`, `/garmin/sync`, `/garmin/disconnect`, `/subscription/portal`) are already built in US1/US8 — this story is the Settings UI + wiring. (Logout lives in the US10 shell; ST6 verified there.)*
- **11a.1** Settings page scaffold `web/app/(app)/settings/page.tsx` with sectioned layout (Profile, Goal Race, Garmin, Subscription, Data & Privacy, Logout) + section anchors; test sections render. COMMIT.
- **11a.2** Profile form: first/last name editable, email read-only → `PATCH /me`; test validation + "Profile updated" toast. COMMIT. (ST1.1/ST1.2/ST1.4)
- **11a.3** Units toggle (km/miles) → `PATCH /me` + units context; test live propagation to metric displays across pages. COMMIT. (ST1.3)
- **11a.4** Goal Race form (distance, future-date validation, optional target time) → `POST /me/goal-race`; test save + plan-refresh trigger. COMMIT. (ST2)
- **11a.5** Garmin section: status + last-sync datetime, `Sync Now` (→`/garmin/sync` + toast), `Disconnect` (confirm modal → `/garmin/disconnect`, keeps data); tests incl. cancel. COMMIT. (ST3.1–ST3.6)
- **11a.6** Subscription section: current plan + expiry; `Upgrade`→`/pricing` (free) / `Manage`→Paddle portal (premium); tests by plan. COMMIT. (ST4)
- **11a.7** QA manual ST1–ST4. COMMIT.

### US11b — GDPR, data export/delete & security hardening (P0 — launch-blocking, Art. 9)
*Screen 8 (Data & Privacy section) + marketing Privacy/ToS pages + cross-app security. QA ST5, DI2, DI3, SEC1–SEC5. Absorbs old tasks G.2/G.3/G.4/G.6. §7.3.*
- **11b.1** `POST /gdpr/export` job → JSON+CSV bundle of all user tables; `test_export_contains_all_tables`. COMMIT. (DI3)
- **11b.2** Export UI: `Export My Data` triggers the job, polls status, surfaces a download link; test trigger + download. COMMIT. (ST5.1/ST5.2)
- **11b.3** `DELETE /gdpr/account`: cascade purge (all `user_id` FKs ON DELETE CASCADE, §2.4), revoke + delete Garmin token, write `audit_log`; `test_delete_purges_all_rows` + token-revoked assertion. COMMIT. (DI2, ST5.5)
- **11b.4** Delete confirm modal ("type DELETE" to enable) + cancel path; tests. COMMIT. (ST5.3/ST5.4)
- **11b.5** Post-delete: terminate session → redirect landing page; test. COMMIT. (ST5.5)
- **11b.6** Privacy Policy + ToS + Contact pages (`app/(marketing)/privacy`, `/terms`, `/contact`); test routes render + landing-footer links (L7.1) resolve. COMMIT.
- **11b.7** Security pass: `require_auth` on every app route (SEC1); ownership checks (`test_cannot_read_other_users_activity`→404, SEC2); password/Garmin token never in any response (SEC3/SEC4); HTTPS-forced redirect (SEC5). COMMIT.
- **11b.8** QA manual ST5 + DI2/DI3 + SEC1–SEC5. COMMIT.

---

## 5. Design System

Mobile-first. Light mode only (dark mode out of MVP per screen-spec).

### 5.1 Color palette (Tailwind tokens via shadcn CSS variables)
| Role | Token | Hex | Use |
|------|-------|-----|-----|
| Primary | `primary` | `#0F766E` (teal-700) | CTAs, links, active nav. "Endurance/energy" without Garmin's blue. |
| Primary fg | `primary-foreground` | `#FFFFFF` | text on primary |
| Accent | `accent` | `#F97316` (orange-500) | highlights, our comparison column, badges |
| Background | `background` | `#FFFFFF` | page |
| Muted bg | `muted` | `#F8FAFC` (slate-50) | section bands, cards-alt |
| Card | `card` | `#FFFFFF` + `border #E2E8F0` | metric cards |
| Foreground | `foreground` | `#0F172A` (slate-900) | primary text |
| Muted fg | `muted-foreground` | `#64748B` (slate-500) | sub-text, comparisons |
| Success | `success` | `#16A34A` | positive trend 🔺, optimal zone |
| Warning | `warning` | `#D97706` | caution zone, missed −20% |
| Error/Destructive | `destructive` | `#DC2626` | errors, disconnect, overtraining zone |
| Chart series | CTL `#0F766E`, ATL `#F97316`, TSB `#64748B` | | training-load chart |

Contrast ≥ 4.5:1 verified for all text/bg pairs (QA U5/accessibility §).

### 5.2 Typography
- Font: **Inter** (variable) via `next/font` (self-hosted → no fallback flash, U1.4). Numerals: `tabular-nums` for metrics.
- Scale (Tailwind): H1 `text-5xl/tight font-bold` (hero), H2 `text-3xl`, H3 `text-xl`, body `text-base/relaxed`, small `text-sm`, micro `text-xs` (comparisons, captions).
- Metric values: `text-4xl font-semibold tabular-nums`.

### 5.3 Component inventory
**shadcn/ui (use as-is):** Button, Input, Label, Card, Accordion (FAQ), Dialog (confirm modals), DropdownMenu (avatar), Tabs (activity filters), Toast/Sonner, Badge, Skeleton, Switch (units, billing toggle), Avatar, Separator, Tooltip, Progress, Alert (banners), Table (laps, comparison), Sheet (mobile nav), Form (react-hook-form + zod).

**Custom components:**
- `MetricCard` (value + unit + subtext + trend chip)
- `TrainingLoadChart` (Recharts, zoned background, legend)
- `ActivityRow` / `ActivityList`
- `ActivityMap` (Mapbox GL, polyline + start/end markers, no-GPS fallback)
- `HrPaceElevationChart` (multi-axis Recharts)
- `ChatBubble` / `ChatThread` / `ChatComposer` / `SuggestionChips`
- `PlanTimeline` / `PlanWeekView` / `WorkoutDay`
- `PricingTable` (toggle-aware)
- `CoachNoteCard`
- `EmptyState`, `ErrorState`, `LoadingSkeleton` (per-screen variants)
- `GarminConnectProgress` (stepped progress)

### 5.4 Responsive breakpoints (Tailwind defaults)
- Mobile `<768px` (`base`): 1 col, bottom icon-nav, full-width CTAs, cards stacked/2×2.
- Tablet `md ≥768px`: 2-col metric grids, side paddings.
- Desktop `lg ≥1024px` / `xl ≥1280px`: full layout, 4-col metric grid, top nav with labels.
- Touch targets ≥44×44px (U2.4).

### 5.5 Micro-interactions (from screen-spec)
Page fade 200ms; button hover scale 1.02 + border transition; card hover shadow; accordion 300ms; toast slide-in top-right 4s auto-dismiss; skeleton pulse; Garmin import stepped progress. Respect `prefers-reduced-motion`.

---

## 6. Implementation Sequence

### 6.1 Dependency graph
```
Story 0 (scaffold/CI/auth) ──► everything
      │
      ├─► US10 (app shell/nav/redirects) ─┐  foundational — every app page mounts in it
      ├─► US12 (global states/toasts)   ─┘  foundational — every page consumes it
      │
      ├─► US7a (landing)   ─┐  [no backend data dep — build in parallel early]
      ├─► US7b (auth forms)─┘
      │
      └─► US1 (Garmin import) ──► US1b (conversational onboarding coach)
                   │
                   └─► US13 (modular goal architecture) ──► US2 (dashboard, goal-lensed) ──► US9 (activity history)
                                       │
                                       ├──► US3 (activity AI) ──► US4 (chat) ──► US1b (shares chat UI)
                                       │
                                       └──► US5 (plans) ──► US5b (Push to Watch)   └──► US6 (weekly email)

            US8 (subscription/Paddle) ──► gates US4-unlimited / US5 / US6 (premium)
            US11a (settings) ──► needs US1 + US8 endpoints (UI + wiring only)
            US11b (GDPR/security) ──► final hardening; touches every story (cascade, ownership, SEC)
```

### 6.2 Two-week sequence (build order)
**Week 1 — foundation + free tier (the "aha" path)**
1. Story 0 (scaffold, auth, CI) — day 1.
2. US10 app shell/nav/redirects + US12 global states/toasts/errors — day 1 (foundation every page needs).
3. US7a landing + US7b auth — day 1–2, parallel to backend (unblocks demo + acquisition).
4. US1 Garmin import — day 2–4 (the hard, risky core; start early, §7).
5. US2 dashboard — day 4–5 (delivers the <2-min "aha moment").
6. US9 activity history/browse — day 5 (small; extends US2's list + `/activities` endpoint).

**Week 2 — AI value + monetization + compliance**
7. US3 activity AI analysis — day 6–7.
8. US4 chat coach — day 7–8.
9. US8 subscription (Paddle) + premium gating — day 8–9.
10. US5 training plans — day 9–10.
11. US6 weekly email — day 10–11.
12. US11a settings & profile — day 11.
13. US11b GDPR export/delete + security hardening — day 11–12 (launch-blocking, Art. 9).
14. QA-final (E2E, perf, security, data integrity) — day 12–14.

### 6.3 Parallelizable work
- US7a/US7b (frontend marketing + auth) are **fully parallel** to US1 backend — different files, no shared deps.
- US10 (shell) + US12 (global states) are built first so all later UI work plugs into them; US12 primitives (toast/empty/error/skeleton) are reused by every story.
- Within a story, AnalyticsEngine (pure Python) is parallel to its UI.
- Design-system tokens/components (§5) can be built up-front (day 1) and reused.
- US8 webhook/backend is parallel to US3/US4 (different routers).
- US9 backend (extend `/activities`) is parallel to US3 (different router/files).
- **Critical path** = US10/US12 → US1 → US2 → US3 → US4 (shell → data → metrics → AI). Protect it; everything else flexes around it.

### 6.4 Priority discipline
- **P0 (non-negotiable MVP):** S0, US10, US12, US7a, US7b, US1, US2, US3, US4 — the free "aha" path plus the shell/states/auth/landing every page depends on. Must be 100% QA-signed before P1.
- **P1 (ship behind flags if time slips):** US9, US5, US6, US8, US11a.
- **Launch-blocking regardless of tier:** US11b (GDPR export/delete + security hardening) — legally required (Art. 9, §7.3) and must pass SEC1–SEC5/DI2/DI3 before any real-user launch, even if other P1 work is flagged off.
No story starts until the previous P0 story is DONE (§9).

---

## 7. Risk Assessment

### 7.1 python-garminconnect fragility (EXISTENTIAL — research §B7, A2)
**Risk:** Unofficial, reverse-engineered, ToS-violating, can break on any Garmin change; login may hit MFA/captcha/rate-limit; legal risk.
**Mitigations:**
- **Isolation:** all garminconnect use behind `GarminProvider` interface (§1.4). Breakage is contained to one module; official-API swap is one new impl.
- **Defensive client:** retries with exponential backoff + jitter; circuit breaker that flips `garmin_connections.status='error'` and surfaces a clear UI message instead of crashing (task 1.14, O3).
- **Synthetic monitor:** a scheduled health-check job logs in with a test account daily; alerts on failure so we know before users do.
- **Pin + watch:** pin the library version; subscribe to its repo releases; integration tests run against recorded fixtures (VCR-style) so our suite doesn't depend on live Garmin.
- **Rate-limit hygiene:** incremental sync (since last_sync), nightly batched, never hammering on every page load.
- **Token, not password (A5):** cache the session token; avoid repeated full logins (which trigger Garmin's anti-bot).
**Fallbacks (in priority order):**
1. Apply to the **official Garmin Developer Program** in parallel from day 1 (2-week approval, research §B7) → swap `GarminProvider` impl when granted. This is the real long-term answer.
2. **Manual FIT/TCX upload** path (a `FileProvider` impl of the same interface) as a degraded-but-alive mode (research alternatives §). Ship as hidden fallback.
3. **Strava import** as a second connector (V2) to reduce single-platform dependence — aligns with the multi-brand pivot (research Option A).

### 7.2 AI hallucination / unsafe advice (research §B7, QA A4.3/C3.5)
**Risk:** Invented metrics; dangerous training/medical advice → injury liability.
**Mitigations:**
- **Numbers are never AI-generated** (§1.3): deterministic AnalyticsEngine computes all figures; LLM only narrates provided facts. Prompt explicitly lists allowed fields; golden-prompt snapshot test (task 3.2).
- **Guardrails:** system prompt forbids medical diagnosis/treatment; injects "consult a medical professional" disclaimer on health red-flags; conservative-by-default plans (task 3.4, 5.1). Refusal tests (C3.4/C3.5).
- **Transparency:** every analysis links to the metrics it cites (screen-spec — show the reasoning); `prompt_version` + `model` stored for audit.
- **EU AI Act:** "limited risk" → label AI clearly, keep technical docs (research §B8). Covered by disclaimers + provenance fields.

### 7.3 GDPR / health data (Art. 9 special category — research §B8)
**Risk:** Sensitive data; explicit consent, residency, export/delete obligations.
**Mitigations:** EU data residency (A3); explicit consent checkbox at Garmin connect; encryption at rest (Postgres) + in transit (HTTPS forced, SEC5) + app-level token encryption (A5); export (DI3) & hard-delete (DI2) endpoints + audit log; DPA with Anthropic/Resend, zero-retention AI where available; privacy policy + ToS pages.

### 7.4 Garmin trademark (research §B8)
**Risk:** "Garmin Coach" is Garmin's trademark.
**Mitigation:** product name = **Endurance Coach** (already adopted). Garmin referenced only nominatively ("import from Garmin"); Garmin branding shown per their attribution rules where required.

### 7.5 Platform dependency / API cutoff (research §B9, EXISTENTIAL)
**Risk:** Garmin can revoke access; single point of failure.
**Mitigation:** multi-brand provider interface from day 1 (even if only Garmin is implemented) → strategic reposition to "multi-brand endurance coach" (research Option A); Strava/COROS connectors on the V2 roadmap; the deterministic analytics + AI layer are platform-agnostic and retain value across connectors.

### 7.6 AI cost margin (research §B6)
**Risk:** Power users erode the 87.5% gross margin.
**Mitigation:** model router (Sonnet for chat/analysis, Opus only for plans — A4); aggressive caching (one analysis per activity, reused; dashboard note regen only on new data); prompt caching for the static system/context prefix; free-tier quotas (`usage_counters`, task 4.4); per-user token accounting (`chat_messages.tokens_*`) for cost dashboards & abuse detection.

### 7.7 Latency (QA U4, PF3 — no API call >5s)
**Risk:** Import + AI too slow for request/response.
**Mitigation:** async ARQ jobs + polling for import (A6); SSE streaming for chat (perceived latency); skeleton loaders everywhere (U3.1); pre-generate activity analysis on import so detail page is instant.

### 7.8 Scope / 2-week timeline
**Risk:** 14 stories (~120 TDD tasks) in 2 weeks is aggressive — the original 8-story breakdown hid app-shell, navigation, activity-history, global-states and GDPR/settings work inside a "cross-cutting" blob that under-counted the real scope.
**Mitigation:** strict P0/P1 split (§6.4); P0 free "aha" path (US10/US12 → US1→US2→US3→US4) is the floor; P1 (US9, US5, US6, US8, US11a) ship behind flags if needed; US11b (GDPR/security) is the only non-P0 item that is still launch-blocking. Foundational US10+US12 built day 1 so every later screen plugs into a stable shell + reused state primitives (no rework). TDD keeps regressions cheap; CI gates prevent rework.

---

## 8. Discrepancies Flagged for the Founder
1. **Payments:** screen-spec.md §8.4/§9.2 and qa-checklist.md PR/ST4 say "Stripe Customer Portal / Stripe Checkout". Task constraint says **Paddle**. This plan uses Paddle throughout (A1). Those docs should be updated to read "Paddle".
2. **python-garminconnect vs official API:** research.md strongly warns the unofficial lib is ToS-violating/fragile and recommends the official Developer Program. Task mandates python-garminconnect for MVP. Plan complies but treats the official API as the priority fallback (§7.1) and applies for it in parallel from day 1.
3. **OAuth wording:** US1 is titled "Garmin OAuth", but python-garminconnect uses **email+password login**, not OAuth. UI copy ("Connect Garmin") is fine; internally it is a credential login (A5). Worth aligning marketing language.

---

## 9. Definition of Done (per story, from qa-checklist.md)
A story is DONE only when: backend `pytest` 100% pass · frontend `vitest` 100% pass · `pnpm build` zero errors · `pnpm lint` zero warnings · screen-specific manual QA all pass · regression RG1–RG8 pass · committed & pushed · sign-off block filled. No story starts until the previous P0 story is DONE.
