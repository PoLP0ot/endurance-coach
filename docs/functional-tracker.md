# Functional Tracker — "make the app fully functional"

> Drives the functional-fix loop. Derived from the audit (2026-06-23).
> `[ ]` todo · `[~]` in progress · `[x]` done (verified) · `[U]` USER-BLOCKED (needs the user's real creds / a decision / a device — scaffold + flag, do NOT mark done).
> Real assets available for verification: a valid Garmin token + 43 imported activities live in `api/dev.db` (user_id 89e001dd…, marc@endurance.coach.fr, now premium). Use them to verify Garmin fixes for real.
>
> GATE per batch: `cd api && .venv/Scripts/python.exe -m pytest -q && .venv/Scripts/python.exe -m ruff check .` + `cd web && pnpm vitest run && pnpm lint && pnpm build` (+ Playwright capture for UI). For Garmin-data fixes, also run a real import script against dev.db's stored token and assert rows.

## 🔴 Palier 0 — core product

- [ ] 0.3 Rewrite `garmin.py list_daily_health` to real garminconnect 0.2.25 methods (sleep/RHR/HRV/body-battery/stress/weight) → health_days > 0 on real import; recovery uses real signals
- [ ] 0.4 Fix `get_activity_streams` to a real method → streams stored; unblocks activity map/HR chart/laps
- [ ] 0.1a Add `POST /garmin/sync` UI trigger ("Sync now" button in Settings + garmin status block) wired to existing endpoint
- [ ] 0.1b Add ARQ cron (`cron_jobs` in WorkerSettings) for periodic Garmin sync + the weekly-email fan-out (currently never scheduled)
- [ ] 0.5 Don't re-login when a valid stored token exists; surface MFA flow (code entry); add backoff on rate-limit
- [ ] 0.2 Document/scripts: run worker locally (`arq ...`) + Redis via docker-compose; keep inline fallback for dev. [U for managed Redis in prod]

## 🟠 Palier 1 — production / multi-user

- [ ] 1.1 Make DB swap clean: keep SQLite for dev, `DATABASE_URL` Postgres for prod; verify migrations on Postgres. [U to point at real Supabase Postgres]
- [U] 1.2 Paddle real checkout+webhook (needs PADDLE_* keys + sandbox purchase) — verify signature path with a test event
- [U] 1.3 Resend real weekly send (needs RESEND_API_KEY + worker/cron up)
- [U] 1.4 Mapbox map component (needs NEXT_PUBLIC_MAPBOX_TOKEN)
- [U] 1.5 Supabase email-confirmation decision + UI flow
- [ ] 1.6 Security sweep: confirm every API query filters by user_id; service-role key never reaches the client; tighten CORS to prod origins
- [ ] 1.7 Basic rate-limiting on auth/LLM routes

## 🟡 Palier 2 — prototype features needing backend data

- [ ] 2.1 Goal banner: add `race_name`/`race_date` to profile (model+migration+API+UI) → dashboard "Road to <race>" banner with countdown + progress
- [ ] 2.2 "This Week at a Glance" weekly aggregate in analytics + dashboard table
- [ ] 2.3 `/signals` endpoint with real per-signal narration (replace client-templated text in signals-view)
- [ ] 2.4 Activity detail: render map + HR/pace chart + laps from real streams (after 0.4)
- [ ] 2.5 Push-to-watch backend `GarminProvider.push_workouts()` (real workout upload) wired to the plan button
- [ ] 2.6 Goal-variant metrics (weight-loss/hyrox/triathlon) — needs weight/calorie + multi-sport load fields

## 🟢 Palier 3 — quality / tests / robustness

- [ ] 3.1 Tests for new code: inline-import fallback, signals-view, coach-onboard, push-to-watch, goal-lens, reskinned email
- [ ] 3.2 LLM error/timeout/quota handling (chat/analysis/plan) with clear UI messages + retry
- [ ] 3.3 Structured logging (api) + error surface; basic request logging
- [ ] 3.4 a11y + responsive verification pass (keyboard, 375/768/1440) [U for real-device Lighthouse]

## 🔵 Palier 4 — deployment (scaffold; execution is USER)

- [ ] 4.1 Dockerfile(s) for api + worker; docker-compose (api, worker, redis, postgres) for parity
- [ ] 4.2 `web` Vercel config + env documentation
- [U] 4.3 Provision Railway/Fly (EU) + managed Redis/Postgres; deploy
- [U] 4.4 Domain, HTTPS, uptime monitoring, Sentry
