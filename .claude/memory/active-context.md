# Active Context

## Current Phase: BUILD (feature stories)

**Status:** Story 0 committed (scaffold + CI green: pytest, ruff, eslint, vitest, next build all pass). US7a landing page committed.

**Last completed:** US1 Garmin import. Backend: typed GarminProvider errors (auth/MFA/locked) + daily-health method; `garmin_import.py` (idempotent upsert_activities/upsert_daily_health, store_streams+downsample cap, resolve_since incremental, run_import with progress labels); `routers/garmin.py` (connect/status/import-status/sync/disconnect, ownership-checked); DailyHealth + ImportJob models; ARQ worker runs real import; migration 0002 + schema.sql. Frontend: `/onboarding` ConnectGarmin (connect → poll import-status → redirect, encrypted reassurance, skip). 37 pytest + 24 vitest.
**Currently working on:** Paused for review after US1 (per user direction).
**Next:** US1b → US13 → US2 → US9 → US3 → US4 → US5 → US5b → US8 → US6 → US11a → US11b

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
