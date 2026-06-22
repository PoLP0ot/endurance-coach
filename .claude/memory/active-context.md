# Active Context

## Current Phase: BUILD (feature stories)

**Status:** Story 0 committed (scaffold + CI green: pytest, ruff, eslint, vitest, next build all pass). US7a landing page committed.

**Last completed:** US11b GDPR. Full feature set shipped (see below).
**Currently working on:** Feature stories complete — ready for QA review.
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
