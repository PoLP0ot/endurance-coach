---
name: react-ui
description: React UI — Tailwind design tokens in index.css, ShadCN/Radix components, cva variants, layout wrappers, typography, navigation, charts, and accessibility. Use when styling components, adding ShadCN primitives, or enforcing visual consistency.
---

> Claude Code adaptation: migrated from `skills/react-ui/SKILL.md`. Use as a project skill under `.claude/skills/react-ui/SKILL.md`.

# React UI (Tailwind + ShadCN)

## New screens

Before adding a page, major layout, or substantial UI surface, read **`ux-design`** (or run `/design-screen` for the full dev-led workflow):

- Confirm responsive vs desktop-only for this project
- Match designer deliverables when they exist; otherwise mirror the closest existing screen
- Lock hierarchy, primary CTA, and loading/empty/error states before picking components

Then implement here — tokens, ShadCN primitives, layout wrappers, typography.

## Tailwind and tokens

- No inline styles; no raw hex/rgb values in components
- All design tokens (colors, fonts, radii, shadows) defined in **`src/index.css`** (`@theme`, CSS variables)
- Use semantic token classes: `bg-primary`, `text-muted-foreground`, `border-input`, etc.
- Compose conditional classes with `cn()` from `@/helpers/tailwind`
- Repeated layout class strings → extract a wrapper component

## ShadCN / Radix

- Check `src/components/ui/base/` first — the component may already be there
- If missing, copy it from https://ui.shadcn.com/docs/components into `src/components/ui/base/` following the same structure as existing ones
- **Never** rebuild a ShadCN component from scratch — Dialog, Sheet, Popover, Select, etc. already exist in the library
- Extend via **cva variants**; add a new variant rather than a one-off styled element:

```ts
const buttonVariants = cva('...base...', {
  variants: { variant: { default: '...', destructive: '...' }, size: { ... } },
  defaultVariants: { variant: 'default', size: 'default' }
});
```

- Inputs: use `components/ui/inputs/` — `SearchInput`, `DebouncedSelectInput`, `DateRangePicker`, etc.

### Debounced inputs

Filter inputs that write to URL params must debounce to avoid triggering a query on every keystroke.

- `SearchInput` — debounce is built in; use it directly for text search filters
- `DebouncedSelectInput` — debounced version of `SelectInput`; exported from the same file

When a debounced variant is missing for an input you need:

1. Add `Debounced<InputName>` in the **same file** as the base input
2. Wrap it with `useDebounceValueChanges` from `hooks/ui/use-debounce.ts` — same pattern as `DebouncedSelectInput`

Do not debounce inside data hooks or components — debouncing belongs in the input component itself.

## Layout and typography

- Use layout wrapper components (`Layout`, page containers, section wrappers) — never replicate structure in Tailwind
- Cards, tables, modals from `components/ui/` — not ad-hoc div stacks

### Typography

All text rendering goes through `components/ui/typography.tsx`. It exports a `Typography` object with semantic sub-components (`Typography.h1`, `Typography.h2`, `Typography.p`, `Typography.link`, etc.), each accepting `style` and `color` cva variant props.

**Rules:**

- Never write raw `<h1>`, `<p>`, `<span>` with Tailwind text classes for any text that appears more than once
- Reused text styles → add a **variant** to `typographyVariants` in `typography.tsx`
- One-off adjustments → pass extra classes via `className` on top of the Typography component
- Preserve semantic order (h1 → h2 → h3) for both a11y and visual hierarchy

```tsx
// correct
<Typography.h2 style="h3" color="secondary" className="mt-4">Title</Typography.h2>

// wrong — hardcoded text style scattered in a component
<p className="text-lg font-semibold text-secondary mt-4">Title</p>
```

When a new text style is needed project-wide, add it as a `style` or `color` variant in `typographyVariants` — not inline in the component.

## Navigation and forms

- No `onClick` on `Button` for in-app navigation — use `Button` / `Typography` with **`to`** prop (renders React Router `Link`)
- Submit buttons must have `type="submit"` inside a `<form>` — enables Enter key and correct a11y; cancel/secondary buttons must have `type="button"` to avoid accidental submission

## Charts and feedback

- Charts: `components/ui/charts/` (recharts wrappers — `BarChart`, `AreaChart`, `PieChart`, `ChartCard`)
- Toasts: **sonner** — fired from command hooks, not from components
- Loading: `Spinner` / `Skeleton` from `components/ui/base/`

## Accessibility

- ShadCN/Radix components handle ARIA, keyboard, and focus management — prefer them
- Semantic HTML first; add ARIA only when semantics are insufficient
- All inputs have visible labels; icon-only controls have `aria-label`

## UI folder map

```
components/ui/
  base/         # ShadCN primitives — button, badge, dialog, card, tooltip, ...
  inputs/       # Composed inputs — text, select, date, search, debounced, ...
  data-table/   # Table, DataTable, DataTableWithServerSidePagination
  charts/       # bar, area, pie, chart-card
  typography.tsx
components/layout/
  index.tsx, app-header, app-sidebar, ...
```
