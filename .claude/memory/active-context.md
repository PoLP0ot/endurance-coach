# Active Context

## Current Phase: BUILD (feature stories)

**Status:** Story 0 committed (scaffold + CI green: pytest, ruff, eslint, vitest, next build all pass). US7a landing page committed.

**Last completed:** US11b GDPR. Full feature set shipped (see below).
**Currently working on:** Build loop "pleinement fonctionnel + design = prototype" — see `docs/build-plan.md` (6 phases driven by `docs/qa-checklist.md` AC IDs).

### Functional-fix loop (started 2026-06-23) — see docs/functional-tracker.md
Real Garmin account connected; data live in api/dev.db (uid via `SELECT user_id FROM garmin_connections LIMIT 1`; user marc@endurance.coach.fr set premium via `subscription_status='active'`). Servers run locally: API `:8001` (uvicorn, ABSOLUTE python path required in bg tasks), web `:3000` (pnpm dev). No Redis locally → import uses inline fallback.
- **Done & verified:** cdc8ced (Redis-less inline import + garth error wrapping), a5aaa6f (0.3 real daily-health via per-day get_stats/get_sleep_data/get_hrv_data + `_client_from_token` display_name fix that also unblocked streams), 0.4 streams stored (43 rows), 7338aa4 (0.1a Sync-now card in settings), 0.5 connect() reuses stored token on login block, 0.1b ARQ cron_jobs (daily sync 03:00 + weekly email Mon 07:00).
- **Next (loop):** Palier 2 (2.1 goal-banner race_date, 2.2 This-Week table, 2.3 /signals endpoint, 2.4 activity map/HR-chart/laps from stored streams, 2.5 push_workouts) → Palier 3 (tests for new code, LLM error handling, logging) → Palier 4 (Dockerfiles/compose/vercel scaffold). [U] = Paddle/Resend/Mapbox keys, Postgres prod, deploy, device Lighthouse, multi-client email.

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
