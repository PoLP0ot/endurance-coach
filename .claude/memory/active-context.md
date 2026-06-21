# Active Context

## Current Phase: BUILD (Story 0 — Scaffold)

**Status:** Scaffold initiated (47 files from print mode). Dependency installation in progress. Hook-based state signaling configured and working.

**Last completed:** Design + interactive prototype (vibe-hybrid A×D)
**Currently working on:** Story 0 completion (deps, tests, CI)
**Next:** US7a Landing Page, US7b Signup/Login, US10 App Shell, US12 Global States

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
