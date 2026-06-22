# Garmin Coach — Pipeline State

> **Project:** Garmin Coach (Endurance Coach) — Virtual coach app powered by Garmin connected watch data
> **Started:** 2026-06-21
> **Pipeline:** Company OS v1

---

## State Machine

```
IDLE ──→ IDEATE ──→ ANALYZE ──→ BUILD ──→ MARKET ──→ SELL ──→ OPERATE
  ✓        ✓          ✓           ◐           ☐          ☐          ☐
```

**Current:** BUILD — in progress (prototype phase)
**Last transition:** 2026-06-21 — ANALYZE completed (Go decision), BUILD started; interactive prototype built

## Phase Status

| Phase | Status | Started | Completed | Output |
|-------|--------|---------|-----------|--------|
| IDEATE | completed | 2026-06-21 | 2026-06-21 | brief.md |
| ANALYZE | completed | 2026-06-21 | 2026-06-21 | go-to-market.md, research.md |
| BUILD | in progress — prototype phase | 2026-06-21 | — | screen-spec.md, tech-plan.md, qa-checklist.md, interactive prototype (prototype.html) |
| MARKET | pending | — | — | marketing/ |
| SELL | pending | — | — | sales/ |
| OPERATE | pending | — | — | finance/ |

## Go/No-Go Gates

| Gate | Decision | Rationale |
|------|----------|-----------|
| IDEATE → ANALYZE | GO | Score 6.8/10. Real pain (documented complaints), 7 competitors mapped, differentiated combo of analytics+AI coaching, market large & growing. |
| ANALYZE → BUILD | GO | WTP validated ($6–18/mo market; coach gap 15–25×); Garmin frustration real; users already export to ChatGPT. Specs (screen-spec, tech-plan, qa-checklist) authored. |
| BUILD → MARKET | pending | — |
| MARKET → SELL | pending | — |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-21 | Project selected | Garmin Connect UX pain point, real API, clear market |
| 2026-06-21 | **Coach-first, not data-first** | Every screen answers one question; coach narrative before raw data; rich signals (HRV, sleep, body battery, stress, VO2Max, RHR, training status) used but never dumped, surfaced via `[▸]` expandable insights |
| 2026-06-21 | **Modular Goal Architecture** (tech-plan A13) | Dashboard is a "lens" by goal: marathon / weight loss / general health (fully rendered) + hyrox / triathlon (architecture ready). No one-size-fits-all dashboard |
| 2026-06-21 | **Conversational onboarding** (A15) | After Garmin import, a chat with the coach (not a static menu) determines the goal; coach references imported data naturally |
| 2026-06-21 | **Push to Watch** (A14) | Plan weeks send structured workouts to the Garmin watch via the GarminProvider interface; closes the loop plan → watch |
| 2026-06-21 | **Mobile-first + desktop responsive** | Primary target = phone (375px, bottom nav: Progress/Coach/Plan/More); desktop = 240px sidebar, multi-column layouts |
| 2026-06-21 | Payments = Paddle (MoR), AI = Anthropic Claude, Auth = Supabase, EU data residency | tech-plan §0 (A1, A4, A7, A3) |

## Open Questions

- Push to Watch via python-garminconnect: does workout upload/schedule stay stable enough for MVP, or gate behind official Garmin API? (A2/A14 risk)
- Hyrox & Triathlon dashboards: ship dedicated lenses in MVP or keep the health/hybrid fallback until post-launch?
- Conversational onboarding: run fully client-side (current prototype) or back it with an LLM call for free-text goals beyond the keyword classifier?
- Free vs Premium gating across goal types — same gate for all lenses, or goal-specific?
- Product/domain name confirmed? (prototype uses "Endurance Coach"; "Garmin Coach" is trademarked — unusable)
- Conversion target & pricing per the GTM ($7–9/mo) — validate against multi-goal positioning (not just marathon)
