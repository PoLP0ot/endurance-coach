# React Rule

> Source: `rules/react.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: React frontend conventions
globs:
  - '**/*.tsx'
  - '**/*.jsx'
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# React

React apps follow a common set of conventions. Match existing structure and patterns in this project before adding new ones.

- Handle UI states: loading, empty, error, disabled
- Use ShadCN components: check `components/ui/base/` first; if missing, copy from https://ui.shadcn.com/docs/components into that folder — never build custom alternatives; extend via cva variants, not one-off styled elements
- Zod schemas in `src/schemas/`; `as const` over enums; no `types/` folder; no `any`
- User-visible text via typed `useIntl` / `FormattedMessage`; keys in `src/locale/`
- Kebab-case file names
- Small, composable components; extract logic to hooks
- List/detail views share TanStack Query cache; mutations invalidate list keys

When implementing UI without designer specs, apply `ux-designer-expert` and read `ux-design` first.

For deep work, apply `react-frontend-expert` and read the relevant skill:

- `react-foundation` — structure, schemas, libraries, consistency
- `react-data-hooks` — query/command hooks, URL filters, cache keys
- `react-ui` — Tailwind tokens, ShadCN, layout, a11y
- `react-forms-tables` — RHF + zod, server-side data tables
