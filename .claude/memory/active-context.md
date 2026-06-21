# Active Context

## Current Phase: BUILD (feature stories)

**Status:** Story 0 committed (scaffold + CI green: pytest, ruff, eslint, vitest, next build all pass). US7a landing page committed.

**Last completed:** US7a Landing page (hero, how-it-works, features, comparison, pricing toggle, testimonials pre-launch variant, FAQ accordion, footer) — `web/src/components/marketing/*`, composed in `app/page.tsx`. 12 vitest tests.
**Currently working on:** US7b Signup/Login (next in user-directed order)
**Next:** US7b → US1 → US1b → US13 → US2 → US9 → US3 → US4 → US5 → US5b → US8 → US6 → US11a → US11b

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
