# Active Context

## Current Phase: PRODUCTIZATION (sellable product)

### Productization loop (2026-07-06) — AUDIT.md → BACKLOG.md → S1–S5 shipped
Business audit + prioritized backlog at repo root (AUDIT.md, BACKLOG.md, DONE.md).
Shipped with full QA gates (104 pytest, 73 vitest, ruff/eslint/build green):
- **S1 legal**: real `/terms` `/privacy` `/contact` (LegalShell) — Paddle-approval + GDPR prerequisite; footer links were dead.
- **S2 Garmin MFA**: provider login via `garth.sso.login(return_on_mfa=True)` (garminconnect 0.2.25 can't resume); `POST /garmin/mfa`; pending challenges in `services/garmin_mfa.py` (in-process, TTL 300 s, single-instance); onboarding UI has a code step + distinct 401/423 messages.
- **S3 billing**: `POST /subscription/cancel` (Paddle API, injected canceller dep), `cancel_at_period_end` col (migration 0011) mirrored from webhook `scheduled_change`; **past_due now keeps premium** (dunning grace, D1-A); UI cancel confirm + payment-failed banner.
- **S4 brief**: BriefCard on dashboard replaces CoachNote when `GET /coach/brief` succeeds; fallback (free/402/error) keeps the weekly assessment — one narrative always.
- **S5 rate limiting**: `core/ratelimit.py` per-user sliding window (chat 20/min, garmin_login 5/5min, plans 5/h), 429+Retry-After, `rate_limit_enabled=False` autouse in tests.
Second pass same day — S6/S7/S8/S10 shipped too (107 pytest, 79 vitest):
- **S6**: import auth failures (401/403) set connection `auth_expired` (`garmin_import.is_auth_failure`); dashboard `GarminStatusBanner` prompts reconnect.
- **S7**: `paddle_price_id_annual` config; checkout accepts `{interval: month|year}` (503 `annual_price_not_configured`); subscription UI has a Monthly/Annual selector.
- **S8**: `adapt_plan` records `structure.last_adaptation {at, adherence_pct, changes[week, from, to]}` (no migration — lives in the structure JSON); plan page shows a 7-day notice.
- **S10**: worker retries transient import failures via `arq Retry` (linear backoff, `MAX_IMPORT_TRIES=3`, job requeued with visible label); auth failures never retry.
- Docs/deps: CLAUDE.md + memory corrected (LLM = OpenAI); `anthropic` + `paddle-billing-client` dropped from requirements (unused).
Remaining backlog: S9 Sentry only (new dep — needs explicit approval). User-blocked launch items in DONE.md.

### Epic MUSCU (2026-07-12) — strength sessions, stories M1–M5 in BACKLOG.md
Dataset `hasaneyldrm/exercises-dataset` (1,324 exercises, JSON MIT; GIFs © Gym
Visual — founder accepted use while pre-revenue, MUST re-decide before selling).
GIFs served from jsDelivr CDN, not vendored (repo is 127 MB). Scope: exercise
library (M1 data/API, M2 UI), coach session builder with deterministic composer
+ chat tool (M3), in-session set logging weight×reps×RPE (M4), progression +
coach_facts + adherence integration (M5). M3 rescoped by founder: LONG-TERM
periodized strength programs (StrengthPlan, blocks adaptation→hypertrophy→
force→deload), not standalone sessions; M5 = perf-driven progression (double
progression) reusing the adapt_plan re-seed mechanic.
**M1 DONE**: `Exercise` model (dataset id PK, migration 0012), idempotent
`upsert_exercises` + `scripts/seed_exercises.py` (1,324 rows seeded in dev.db),
`GET /exercises` (body_part/target/equipment/q filters, keyset by name+id) +
`GET /exercises/{id}` (instructions EN steps), auth required, free tier.
CDN base in `services/exercises.py::CDN_BASE`. Front URL (real):
https://endurance-coach-coach8.vercel.app — CORS verified OK against prod API,
but **Vercel Deployment Protection still ON** (302 → vercel.com/sso-api).
Prod checks 2026-07-12: API /health 200, 401 clean, 117 pytest + 82 vitest
green, ruff clean. `endurance-coach.vercel.app` is NOT our project (title
"Frontend") — real Vercel URL unknown locally; CORS origin unverifiable without
it. Resend: no `resend._domainkey` TXT on endurancecoach.app yet (domain is on
Zoho mail) — weekly email from coach@endurancecoach.app still blocked.

## Previous Phase: BUILD (feature stories)

**Status:** Story 0 committed (scaffold + CI green: pytest, ruff, eslint, vitest, next build all pass). US7a landing page committed.

**Last completed:** US11b GDPR. Full feature set shipped (see below).
**Currently working on:** Build loop "pleinement fonctionnel + design = prototype" — see `docs/build-plan.md` (6 phases driven by `docs/qa-checklist.md` AC IDs).

### Design audit loop (2026-07-06) — 5 commits c740baa→09d15a0
Full-browser audit (Playwright desktop/tablet/mobile, 48 shots in `web/e2e/__shots__/`). Fixed: recharts bug (Line inside AreaChart never renders → ComposedChart; ATL/TSB were invisible on the dashboard chart), chart/metric colors aligned to tokens (CTL olive/ATL rust/TSB taupe), Card shadow+radius violation, BodyCard dark filler cell. Restructures: GoalHero merges GoalBanner+GoalProgressBanner (deleted both + GoalVariantPanels; goal panels dedupe into core grid — "one number once"), plan page leads with plan (regenerate collapsed at bottom, current week highlighted), activity rows carry sport glyph/pace/TSS, coach starter chips on empty thread, sidebar nav gains Activities+Signals (was orphaned), mobile bottom nav stays 4 slots. Playwright config now has a tablet project. L3s approved by user and done (3 more commits): /explore folded into dashboard as SignalsCard (route redirects, SignalsView/Sparkline deleted, nav item removed); plan schema now parses day-level `sessions` and the current week expands into Monday-first day rows (today marked, rest explicit); `--destructive` split to deep brick hsl(8 56% 40%) ≈ #9F3C2D (activity HR line moved off destructive onto the rust data token).

### MVP coaching loop (2026-06-24) — see C:\Users\THOMAS\.claude\plans\joyful-napping-harp.md
Turned the app from data-display into a goal-driven coach for ANY goal (5 bespoke goals, full closed loop, agentic AI). All phases done + verified on real dev.db + Playwright.
- **Goal engine** (`api/app/services/goals/`): `GoalDefinition` strategy per kind (marathon/weight_loss/hyrox/triathlon/health) over a pure `GoalContext`; `get_goal_definition()` (health fallback). Each gives progress/projection (Riegel race-time, weight-trajectory ETA, consistency streak…), on-track band, dashboard panels, daily-session microcycle. `User.goal_params` JSON (migration 0009) holds per-goal targets, validated by `app/schemas/goal_params.py`; onboarding collects them.
- **Goal-aware dashboard**: `build_dashboard` emits `goal_structured` (band+projection) + `goal_variant` (per-goal panels). Frontend: GoalProgressBanner, GoalVariantPanels, TodayCard.
- **AI** (`coach_facts.build_coach_facts` = single goal-aware fact source plumbed into chat/signals/email/analysis). **Fixed real bug**: activity_analysis now parses raw-Garmin streams via `normalize_streams` (HR zones were dead code). **Agentic**: `llm.converse()` OpenAI tool-loop + `coach_tools.py` (get_goal_progress/recent_activities/health_trend/adherence); chat uses it behind `settings.coach_tools_enabled` (stubs w/o `converse` fall back to `narrate`). LIVE-verified: coach calls tools, cites only tool numbers. **Daily brief** (`brief.py`, DailyBrief model migration 0010, `GET /coach/brief` premium, 05:30 cron).
- **Closed loop**: plan weeks now carry day-level `sessions` (goal microcycle); `adherence.match_week` (completed/partial/missed/extra); `adaptation.adapt_plan` re-seeds upcoming weeks from real CTL+adherence (Sun 18:00 cron, never rewrites past); `GET /coach/today` (today.todays_session).
- **Invariant kept**: AI never computes numbers — tools/definitions are pure over analytics.py.
- **Test counts after MVP**: ~166 pytest + 61 vitest green; ruff/eslint/tsc clean; migrations 0009+0010 applied.

### Functional-fix loop (2026-06-23/24) — see docs/functional-tracker.md — PALIERS 0,2,3,4 DONE
Real Garmin account connected; data live in api/dev.db (uid via `SELECT user_id FROM garmin_connections LIMIT 1`; user marc@endurance.coach.fr premium). Servers: API `:8001` (uvicorn — **launch with CWD = api/ via `cd api && .venv/Scripts/python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001`**; `.env` is loaded relative to CWD, so `--app-dir` alone is NOT enough — wrong CWD → empty SUPABASE_URL → malformed JWKS URL → every authed request 500s "couldn't load …"), web `:3000` (pnpm dev). No Redis locally → import uses inline fallback. **Real-data note:** imported activities/health are dated ~early June 2026; verify time-windowed features with an explicit `today` in that range (e.g. health snapshot non-null only around 2026-06-06).
- **Palier 0 done:** cdc8ced (Redis-less inline import + garth wrapping), a5aaa6f (real daily-health + `_client_from_token` display_name fix), streams stored, 7338aa4 (Sync-now card), 0.5/797f00a (connect() reuses stored token only on rate-limit, never on auth-fail), 0.1b ARQ cron_jobs.
- **Palier 2 done:** goal banner (race_name/race_date, migration 0008), This-Week aggregate, `/signals` endpoint (premium=LLM, free=template), activity `normalize_streams` (route+HR/elev chart+km splits, no Mapbox), push-to-watch (`workout_push` + `POST /plans/push`), goal-aware "Your Body" health snapshot (fixed unbounded-window bug). All verified on real dev.db + Playwright shots (desktop+mobile).
- **Palier 3 done:** typed `LLMError` (timeout 30s, quota/rate_limit/auth → 503/502 global handler) + UI "coach unavailable"+retry; structured JSON logging (`app/core/logging.py`) + request middleware (X-Request-ID); tests for inline-import fallback, push flow, signals.
- **Palier 4 done:** `api/Dockerfile`+`.dockerignore`, root `docker-compose.yml` (pg+redis+api+worker), `web/vercel.json`, README deploy section. compose config validated (live build = deploy step).
- **Remaining = [U] user-blocked only:** 0.2 managed Redis prod, 1.1 Postgres prod swap, 1.2 Paddle keys, 1.3 Resend send, 1.4 Mapbox token, 1.5 Supabase email-confirm, 1.6/1.7 prod security sweep + rate-limiting, 4.3/4.4 deploy+domain, device Lighthouse, multi-client email. MFA code-entry flow for Garmin still TODO.
- **Test counts after loop:** ~116 pytest + 58 vitest, all green; ruff + eslint + tsc clean.

### Build-loop progress (started 2026-06-22)
- **Phase 0 ✅** (`fc3d38b`): added `openai` (imported by `services/llm.py` but missing from requirements — would crash at runtime), added `ruff` dep, restored `.github/workflows/ci.yml`, untracked `api/dev.db` + ignore `*.db`. Migrations confirmed SQLite-compatible (`alembic upgrade head` green). Runtime config is **SQLite** (`DATABASE_URL=sqlite:///./dev.db`), API on **:8001**.
- **Phase 1.1 ✅** (`b1734cd`): replaced dark electric-blue theme with prototype's **warm-stone light** system (bg `#E9E4D8`, primary burnt-orange `#D9703A`, accent olive `#6E7644`, destructive rust, radius 3px). Tokens in `web/src/app/globals.css` (HSL channels), Tailwind colors now use `<alpha-value>` so opacity modifiers work; signature tokens exposed (ink/paper/line/olive/rust/taupe). Dropped forced `.dark`. Confirmed on screen (landing + login match prototype direction).
- **Visual harness ✅** (`ba5d753`): Playwright (`web/playwright.config.ts` + `e2e/capture.spec.ts`). gstack/Chromium daemon would NOT start on the Windows host — use Playwright instead. Loop = code → `pnpm exec playwright test capture` → review shots in `web/e2e/__shots__/` vs `docs/design/prototype.html`.
- **Note:** code LLM = **OpenAI/GPT** (`gpt-4o-mini`/`gpt-4o`), not Anthropic despite CLAUDE.md. `supabase_service_key` defined but unused.
- **Progress (loop run 1):** Phase 1 primitives (Button/Field/Input/auth-card) ✅ · Phase 2 shell (sidebar border-left orange, bottom-nav 62px) ✅ (More-sheet + athlete card deferred) · Phase 3 reskins ✅ for dashboard (Coach's Assessment card + metric grid), coach chat (bubbles+pill input), plan (timeline+phase pills), settings (paper card+switch), subscription, privacy, activity list. Commits 1dac6af→9c452e0 + activity/privacy.
- **Loop validation:** `e2e/authed.spec.ts` stubs Supabase session + API; AUTHED_ROUTES now covers dashboard/coach/plan/settings/subscription/activities/privacy. Mobile project forced to chromium (webkit not installed). Build MUST run with port 3000 free (dev server corrupts shared .next).
- **Loop run 1 complete (fc3d38b→…):** Phases 1–4 done. Phase 3 all 10 screens reskinned (incl. activity detail). Phase 4 new screens: /pricing, Signals-Explore (/explore + Sparkline), conversational onboarding (/coachonboard), push-to-watch UI (plan), goal-variant dashboard lens, weekly-email reskin (warm-stone, email-safe). All gated (pytest+ruff+vitest+lint+build) and visually validated via Playwright.
- **Remaining = USER-BLOCKED / backend-data (Phase 5/6):** real Garmin import (user runtime creds) → real dashboard/activity data; real OpenAI exercise of chat/analysis/plan (key configured, needs real activity data + spend); Paddle real checkout+webhook; Resend real Monday send (needs Redis/ARQ up); Mapbox activity map; activity chart/laps + dashboard goal-banner/This-Week-table/key-signal-chips (need backend stream/goal-date fields); Lighthouse on device; multi-client email rendering; More-sheet + sidebar athlete card (minor). See docs/acceptance-tracker.md.
**Test counts:** 96 pytest + 52 vitest, all green; ruff + eslint + next build pass.

### Feature stories delivered (US1 → US11b)
- **US10 App Shell** — `components/shell/` (nav-items, app-shell); route group `web/src/app/(app)/` (dashboard, coach, plan, settings, activities). Desktop sidebar + mobile bottom nav, active-route highlight, sign-out.
- **US12 Global States** — `components/states/` EmptyState / ErrorState / LoadingState + `ui/skeleton`. Reused across every screen.
- **US2 Dashboard** — `services/dashboard.build_dashboard` (daily TSS series → CTL/ATL/TSB, recovery, form band); analytics `activity_tss` + `form_assessment`. `GET /dashboard`. Frontend DashboardView (CoachNote, MetricCard, TrainingLoadChart via recharts).
- **US9 Activity History** — `services/activity_history.list_activities` (keyset cursor pagination, free-tier 30-day window via `subscriptions.is_premium`); `GET /activities`, `GET /activities/{id}`. Frontend ActivityList (load-more) + `lib/format`.
- **US3 Activity AI** — `services/activity_analysis` (deterministic facts: pace/TSS/HR-zones; cached `get_or_create_analysis`); `deps.require_premium` (402) + `deps.get_llm_provider`; `GET /activities/{id}/analysis`. Frontend ActivityDetail "What this run means" + premium upsell + evidence.
- **US4 Coach Chat** — `models/chat` (int PK), `services/chat` (grounded in dashboard facts); `GET /chat/messages`, `POST /chat` (premium). Frontend ChatView (optimistic send). Migration 0003.
- **US5 Training Plan** — `services/plans.build_plan_structure` (base/build/peak/taper periodization, recovery + taper) + `create_plan`/`current_plan`; `models/plan`. `POST /plans`, `GET /plans/current` (premium). Frontend PlanView + PlanTimeline. Migration 0004.
- **US8 Subscriptions** — `models/subscription`, `services/subscriptions` (Paddle signature verify + webhook apply); `GET /subscription/status`, `POST /subscription/checkout`, `POST /subscription/webhook`. Frontend SubscriptionView (Paddle checkout). Migration 0005.
- **US6 Weekly Email** — `services/email` (EmailProvider/Resend lazy, render_weekly_email, build_weekly_email); ARQ `send_weekly_email`/`send_weekly_emails`; `GET /email/weekly/preview`. User `units` + `weekly_email_opt_in` cols. Migration 0006.
- **US11a Settings** — `GET`/`PATCH /profile` (auto-provision, goal/units validation). Frontend SettingsView + `ui/switch`.
- **US11b GDPR** — `models/audit` (FK-free GdprAuditLog), `services/gdpr` (build_export JSON+CSV, delete_user_data cascade purge); `GET /gdpr/export`, `DELETE /gdpr/account`. Frontend PrivacyView. Migration 0007.

**Premium gating:** `require_premium` → 402 `premium_required`; statuses premium/active/trialing unlock. Frontend detects 402 → upsell to `/settings/subscription`.
**LLM in tests:** override `get_llm_provider` dep with a stub; services accept a `_Narrator` protocol so the Anthropic SDK is never imported in tests.

## Backend test strategy
Models are cross-dialect (GUID/JSONType TypeDecorators in `models/base.py`): native UUID/JSONB on Postgres, CHAR(36)/JSON on SQLite. Tests use an in-memory SQLite session fixture (`db_session`) + dependency-overridden `app_client` (get_db/get_current_user/get_enqueuer). CI has no Postgres/Redis — keep DB tests SQLite-compatible.

## Key Decisions
- **A13:** Modular Goal Architecture (marathon, weight loss, hyrox, triathlon, health)
- **A14:** Push to Watch via python-garminconnect
- **A15:** Conversational Onboarding (coach discovers goal through dialogue)
- tmux interactive mode for implementation (not print mode)
- Hook-based state signaling via /tmp/claude-state.json
- Mobile-first responsive (375px phone + 1024px+ desktop sidebar)

## Blockers
- pnpm install getting rejected (background command issue) — use foreground
- Missing .claude/memory files getting filled now

## Open Questions
- GitHub repo not created yet (no gh CLI)
- Supabase project not provisioned (need account setup)
- Redis instance not provisioned (need for ARQ jobs)
- Garmin API access — apply to Developer Program in parallel
