# Acceptance Tracker — Endurance Coach build loop

> Source of truth for the loop. Detail for each ID: `docs/qa-checklist.md`. Visual ref: `docs/design/prototype.html`.
> `[ ]` todo · `[~]` in progress · `[x]` done (auto+visual validated). Append notes after `—`.
> Gate per batch: `pytest -q` + `ruff check .` + `pnpm vitest run` + `pnpm lint` + `pnpm build` + `playwright test capture` (review shots).

## Phase 0 — foundations
- [x] P0 deps/CI/dev.db/migrations/smoke — commit fc3d38b

## Phase 1 — design system
- [x] 1.1 design tokens (warm-stone light, 3px) — commit b1734cd
- [x] 1.x visual harness (Playwright public capture) — commit ba5d753
- [x] 1.x authed capture fixture (stub Supabase session + API, e2e/authed.spec.ts) — unblocks Phase 2/3 authed screens
- [x] 1.2 primitives: Button variants (Inter Tight 600, primary→accent-dk hover, outline=bordered ghost)
- [ ] 1.2 primitives: Pill/Badge (free/premium)
- [x] 1.2 primitives: Field (mono uppercase label + paper input, focus-orange) — commit pending
- [ ] 1.2 primitives: CoachCard (ai-dot + THIS WEEK badge)
- [ ] 1.2 primitives: Metric (4-up grid, 40px tabular value)
- [ ] 1.2 primitives: GoalBanner (dark gradient + progress bar)
- [ ] 1.2 primitives: ChatBubble (coach/user)
- [ ] 1.2 primitives: InsightToggle ([▸] rotate + expandable panel)
- [ ] 1.2 primitives: SignalChip (chip + sparkline + detail)
- [ ] 1.2 primitives: Sparkline (SVG)
- [ ] 1.2 primitives: Dialog/Modal (radix) + Toast

## Phase 2 — shell & navigation
- [x] MN1.1 bottom nav 4 tabs <768px (62px, font-display) — currently Progress/Coach/Plan/Settings
- [x] MN1.2 bottom nav hidden on landing/signup/onboarding (separate route groups)
- [x] MN1.3 active tab in accent color
- [x] MN1.4 all tabs navigate correctly
- [ ] More-sheet (swap 4th tab to More → Activities, Signals, Settings, Pricing, Log Out) — pending nav-items expansion
- [x] DL1.1 sidebar ≥1024px (240px, glyph, border-left orange active, Inter Tight links)
- [x] DL1.2 sidebar hidden on landing/signup/onboarding
- [x] DL1.3 bottom nav hidden on desktop
- [x] DL1.4 sidebar links functional
- [x] DL1.5 content takes remaining width
- [ ] sidebar athlete card at bottom (deferred — needs real user data, avoid demo)

## Phase 3 — reskin existing screens (pixel-match)
### Landing (L1–L7)
- [ ] L1 hero · L2 how-it-works · L3 features · L4 comparison · L5 pricing+toggle · L6 FAQ accordion · L7 footer/links
### Auth (S1–S3)
- [~] Auth shell reskin: paper card + mono field labels done; remaining: dup-email/loading/redirect behaviour AC
- [ ] S1 signup (validation, pw toggle, loading, dup-email, redirect)
- [ ] S2 login (invalid creds, redirect, forgot link)
- [ ] S3 forgot-password (no-leak message)
### Onboarding connect-garmin (O1–O4)
- [ ] O1 layout · O2 connect+progress+redirect · O3 errors+retry · O4 skip+banner
### Dashboard (D1–D7)
- [x] D1 nav/topbar (shell) · [x] D3 metric cards (mono label + 40px tabular) · [x] D4 load chart · [x] D6 coach note (Coach's Assessment card + THIS WEEK badge)
- [ ] D2 dynamic week period/subtitle · D5 recent activities list · D7 full states · goal-banner · This-Week table · key signals (need backend goal/recent data)
### Activity detail (A1–A5)
- [ ] A1 header/map · A2 metrics · A3 chart · A4 AI analysis · A5 laps
### Coach chat (C1–C6)
- [ ] C1 layout · C2 suggestions · C3 replies · C4 history · C5 states · C6 context
### Training plan (P1–P4)
- [ ] P1 generate · P2 timeline · P3 week detail · P4 adapt
### Settings (ST1–ST6)
- [ ] ST1 profile · ST2 goal race · ST3 garmin · ST4 subscription · ST5 data/GDPR · ST6 logout
### Subscription/Pricing (PR1–PR2)
- [ ] PR1 plans+toggle · PR2 checkout+success/cancel/error

## Phase 4 — new prototype screens
- [ ] Signals/Explore (question cards + coach interpretation)
- [ ] ON1.1–ON1.6 conversational onboarding coach
- [ ] Pricing page (/pricing) full
- [ ] GV1.1–GV1.5 goal-variant dashboards (marathon/weight-loss/health)
- [ ] PW1.1–PW1.5 push to watch
- [ ] E1–E3 weekly email template reskin

## Phase 5 — real integrations
- [ ] Garmin real import → real dashboard data (O2.6, DI1)
- [ ] OpenAI real (chat/analysis/plan) (A4, C3, P1)
- [ ] Paddle real checkout+webhook (E2E.2, PR2)
- [ ] Resend real weekly email (E2)
- [ ] Mapbox real maps (A1.3–A1.5)
- [ ] SEC1–SEC5 auth gating + RLS + no secret leaks + HTTPS

## Phase 6 — QA sweep
- [ ] U1 render · U2 responsive · U3 states · U4 perf · U5 a11y · U6 API
- [ ] PF1–PF3 Lighthouse/perf
- [ ] RG1–RG8 regression
- [ ] E2E.1–E2E.3 happy paths
- [ ] DI1–DI3 data integrity
