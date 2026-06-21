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
- CTL (fitness): #6E7644 (olive)
- ATL (fatigue): #C4612F (rust)
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
- Mobile (375px): bottom nav (Progress, Coach, Plan, More), single column, stacked
- Desktop (≥1024px): sidebar navigation, multi-column, table layouts

### Components (shadcn/ui base + custom)
- MetricCard, CoachNoteCard, TrainingLoadChart (Recharts)
- ChatBubble, SuggestionChips, PlanTimeline
- EmptyState, ErrorState, LoadingSkeleton (per-screen variants)

### Interaction Standards
- Page transitions: fade 200ms
- Button hover: scale(1.02) + border-color transition
- Accordion: 300ms expand
- Toasts: slide-in top-right, 4s auto-dismiss
- Skeleton loaders: pulse animation
- Touch targets: min 44×44px

### Forbidden
- ❌ box-shadow on cards (hairline borders instead)
- ❌ rounded corners > 3px
- ❌ purple gradients, glassmorphism, blurred backdrops
- ❌ confetti, streak counters, gamification
- ❌ stock photos of smiling runners
