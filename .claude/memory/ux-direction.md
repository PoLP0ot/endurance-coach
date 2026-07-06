# UX Direction

## Design System: Vibe-Hybrid A (Swiss Precision) × D (Alpine Technical)

**Theme:** "A field laboratory for the serious endurance athlete."

### Palette
- Background: #E9E4D8 (warm stone, NOT white, NOT gray)
- Cards: #F3EFE5 (warm paper)
- Text: #38382C (deep olive-brown, NOT black)
- Muted: #7C7765 (warm slate)
- Lines: #CFC7B4 (warm taupe, 1px)
- Accent: #D9703A (trail rust/orange)
- Destructive: #9F3C2D (deep brick, hsl 8 56% 40%) — danger/errors ONLY, never a data color; must stay visually distinct from the accent orange
- CTL (fitness): #6E7644 (olive)
- ATL (fatigue) + HR data lines: #C4612F (rust — data color, not destructive)
- TSB (form): #A99C7F (taupe)

### Typography
- Display/Headings: Inter Tight (600, 700), letter-spacing -0.02em
- Body: Inter (400, 500), 15px base, 1.55 line-height
- Data/Mono: JetBrains Mono, tabular-nums, font-variant-numeric: tabular-nums

### Design Principles
1. **Numbers are the hero** — data carries the page, decoration removed until only measurement + unit + trend remain
2. **Hairlines, not boxes** — structure from 12-column grid + 1px taupe rules, never heavy fills or shadows
3. **Warm restraint** — one accent (trail rust), stone/olive/limestone do the rest. Calm enough to live outdoors

### Coach-First Philosophy
- Every screen answers ONE question
- Coach narrative BEFORE raw data
- Data shown as EVIDENCE for coach's reasoning ([▸] expand to see)
- Never dump metrics without context ("this is your HRV, it means...")

### Layout
- Mobile (375px): bottom nav (Progress, Coach, Plan, Settings), single column, stacked
- Desktop (≥1024px): sidebar navigation (adds Activities — every shipped route must be reachable from the shell), multi-column, table layouts
- Signals live ON the dashboard (SignalsCard under the load chart); /explore redirects to /dashboard — a separate page duplicating dashboard concepts didn't earn its existence

### Components (shadcn/ui base + custom)
- MetricCard, CoachNoteCard, TrainingLoadChart (Recharts ComposedChart — Line inside AreaChart is silently dropped)
- GoalHero (single north-star card: race + countdown + band + projection; dark ink variant for race goals, paper variant otherwise)
- ChatBubble, SuggestionChips (starter questions on empty coach thread), PlanTimeline (current week highlighted + expanded into Monday-first day rows with today marked; rest days explicit)
- SignalsCard (per-metric coach reads as questions, dashboard-inline; progressive — renders nothing while loading/on failure)
- EmptyState, ErrorState, LoadingSkeleton (per-screen variants)

### One-number-once rule (added after 2026-07-06 audit — dashboard showed Fitness/Form twice)
A metric appears exactly once per screen. Goal-variant panels are deduped
against the core grid and Your Body; unique ones join the core metric grid.
Series/metric colors correspond: CTL/Fitness olive, ATL/Fatigue rust, TSB taupe.

### Interaction Standards
- Page transitions: fade 200ms
- Button hover: scale(1.02) + border-color transition
- Accordion: 300ms expand
- Toasts: slide-in top-right, 4s auto-dismiss
- Skeleton loaders: pulse animation
- Touch targets: min 44×44px

### Theme & language decisions (2026-07-06 design audit)
- **Light-only is the brand** (Direction A): warm-stone doesn't invert; a dark
  theme requires its own "night trail" palette study — backlog D6, post-launch.
- **English-only at launch** (Direction A): react.md's useIntl rule is a
  documented deviation until D7; no i18n infra installed, copy stays in
  components.
- Motion: implemented standards = 200ms page fade (app template.tsx) + button
  press; everything respects `prefers-reduced-motion`. No decorative motion.
- Data-viz accessibility: series are distinguishable without color — CTL solid
  olive, ATL dashed rust, TSB long-dash taupe.

### Forbidden
- ❌ box-shadow on cards (hairline borders instead)
- ❌ rounded corners > 3px
- ❌ purple gradients, glassmorphism, blurred backdrops
- ❌ confetti, streak counters, gamification
- ❌ stock photos of smiling runners
