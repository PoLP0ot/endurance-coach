---
name: ux-design
description: >-
  Product UI/UX design — hierarchy, layout, interaction, accessibility,
  and dev-led screens when no designer deliverable exists. Use for new screens, small features,
  design review, responsive decisions, shadCN/shadCN blocks selection, or matching external
  design specs (Figma, Lovable, Claude Design, exports, screenshots). Stack-agnostic; pair with react-ui for React implementation.
---

> Claude Code adaptation: migrated from `skills/ux-design/SKILL.md`. Use as a project skill under `.claude/skills/ux-design/SKILL.md`.

# UX Design

Design expertise for **what** users see and **how** it behaves — not framework wiring. For React token/ShadCN implementation details, read `react-ui` after design decisions are set.

## Design sources

| Source                                              | Role                                                                                                                                      |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Designer deliverable**                            | Link, export, or capture from any design tool (e.g. Figma, Lovable, Claude Design) — match spacing, hierarchy, and flows; do not reinvent |
| **Dev-led UI**                                      | No deliverable — common for small features or new screens; you own the quality bar                                                        |
| **shadCN + [blocks](https://ui.shadcn.com/blocks)** | Default web component vocabulary — prefer existing primitives/blocks over custom UI                                                       |

Ask once if unclear: **Is this app responsive?** Some products are desktop-only (fixed layouts OK); others need mobile/tablet breakpoints. Do not assume mobile-first unless the project or user says so.

## Before designing or coding UI

1. **Scan the app** — adjacent screens, nav patterns, density, empty/error/loading states, terminology.
2. **Find specs** — designer deliverable (URL, export, screenshot) or `AGENTS.md` / design notes in the repo.
3. **No spec?** — Treat as dev-led: mirror the closest existing screen; one primary action per view; reuse labels from i18n/locale files.
4. **Constraints** — brand colors/fonts if documented; WCAG 2.1 AA contrast; no new visual language without reason.

## Visual design

- **Hierarchy** — one focal point per section; size/weight/color guide scanning (title → supporting text → metadata).
- **Spacing** — consistent rhythm (e.g. 4/8px scale); align to existing pages, not arbitrary gaps.
- **Color** — semantic roles (primary, muted, destructive, border); never raw hex in components when tokens exist.
- **Typography** — limited scale (2–3 levels per block); line length ~45–75 characters for body copy.
- **Density** — match app norm (admin dense vs marketing airy); don't mix both on one flow.

## Interaction design

- **Navigation** — predictable placement; back/cancel always reachable; breadcrumbs or context title when depth > 2.
- **Actions** — one primary CTA per card/modal; destructive actions visually distinct and confirm when irreversible.
- **Feedback** — loading for >300ms async work; success/error toasts or inline messages; disabled states explain why when possible.
- **Forms** — label every field; errors next to the field; logical tab order; sensible defaults.
- **Motion** — subtle transitions only; respect `prefers-reduced-motion`.

## Information architecture

- Group related actions; progressive disclosure for advanced options.
- Tables/lists: clear column headers, sort/filter when data is large, empty states with next step.
- Search/filter placement consistent with other list pages in the project.

## Accessibility (minimum bar)

- Contrast ≥ 4.5:1 for normal text, 3:1 for large text (WCAG AA).
- Keyboard: all interactive elements focusable; visible focus ring; no keyboard traps in modals.
- Screen readers: semantic structure (`main`, headings in order); `aria-label` on icon-only controls.
- Touch (when responsive): targets ≥ 44×44px; adequate spacing between tappable items.

## Responsive (when required)

- **Breakpoints** — follow project Tailwind/config breakpoints; test at least narrow + desktop widths.
- **Content priority** — stack or hide secondary columns on small viewports; avoid horizontal scroll for core tasks.
- **Patterns** — collapsible sidebar, sheet/drawer for filters on mobile, responsive tables (card fallback or horizontal scroll with clear affordance).
- **Forms** — single column on narrow screens; appropriate `input` types on mobile.

When **not** responsive: still use fluid widths within the target viewport; avoid fixed pixel widths that clip on slightly smaller monitors.

## shadCN and blocks

1. Check project `components/ui/` for an existing primitive before adding anything.
2. Browse [shadCN components](https://ui.shadcn.com/docs/components) and [blocks](https://ui.shadcn.com/blocks) for dashboards, auth, settings, sidebars — adapt block structure, swap copy and data bindings.
3. Extend via variants (cva), not one-off styled duplicates.
4. Compose: `Card` + `Table` + `Dialog`/`Sheet` + `Button` variants — same patterns across admin-style apps.

## Dev-led screen workflow

Use when there is no designer deliverable. In Claude Code chat, `/design-screen` runs the full structured workflow (brief → confirm → implement).

```
1. Name the user goal in one sentence
2. List required data/actions (must-have vs nice-to-have)
3. Pick a reference screen in the same app → same layout shell
4. Sketch structure (ASCII or bullet hierarchy):
   - Page title + primary action
   - Filters / toolbar (if list)
   - Main content + empty/loading/error
   - Secondary panel or modal only if needed
5. Choose shadCN block or existing page pattern
6. Implement → verify states and a11y checklist below
```

## Pre-ship checklist

- [ ] Loading, empty, error, and success paths
- [ ] Primary action obvious; destructive actions guarded
- [ ] Copy consistent with rest of app (i18n keys, not hardcoded English in FR apps)
- [ ] Responsive rules respected for this project
- [ ] Contrast and keyboard path checked on changed UI
- [ ] No duplicate component that already exists in `components/ui/`

## Output when advising (no code)

For design-only requests, respond with:

1. **Goal** — user outcome in one line
2. **Structure** — section hierarchy (bullets or simple ASCII)
3. **Components** — suggested shadCN primitives/blocks
4. **States** — loading / empty / error / edge cases
5. **Open questions** — brand, responsive yes/no, copy tone, analytics

Keep proposals implementable by a dev in one session — no exhaustive design-system docs unless asked.
