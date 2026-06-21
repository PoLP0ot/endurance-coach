---
name: react-foundation
description: React project foundation — folder structure, component organisation, kebab-case files, Zod schemas, as-const constants, shared base schemas, i18n, approved libraries, and cross-screen consistency. Use when bootstrapping features, organising files, defining models, or checking project conventions.
---

> Claude Code adaptation: migrated from `skills/react-foundation/SKILL.md`. Use as a project skill under `.claude/skills/react-foundation/SKILL.md`.

# React Foundation

React projects follow a common structure and conventions. Extend existing patterns in this project before inventing new ones. Working samples live under `src/pages/samples/` — use them as the first reference when building something similar.

## Approved stack

| Concern             | Library                                                          |
| ------------------- | ---------------------------------------------------------------- |
| Styling             | Tailwind CSS (tokens in `src/index.css` only)                    |
| UI primitives       | ShadCN on Radix (`components/ui/base/`, `components/ui/inputs/`) |
| Server state        | TanStack Query                                                   |
| Forms               | React Hook Form + `@hookform/resolvers/zod`                      |
| Validation / models | Zod (`src/schemas/`)                                             |
| Dates               | dayjs                                                            |
| Charts              | recharts (`components/ui/charts/`)                               |
| Toasts              | sonner                                                           |
| Routing             | React Router (`Button`/`Typography` with `to` prop)              |
| Tables              | TanStack Table via `components/ui/data-table/`                   |

Do not add alternate libraries for the same concern without explicit approval.

## Folder structure (`src/`)

```
components/
  ui/           # Generic UI — base (ShadCN), inputs, data-table, charts, typography
  rhf/          # RHF-controlled versions of every input in ui/inputs — use these inside forms
  layout/       # App shell, page wrappers, sidebar, header
  <domain>/     # Project-specific — see note below
hooks/
  data/         # TanStack Query hooks — per resource, or grouped by domain
  ui/           # UI-behavior hooks (useSearchParams, debounce, infinite scroll)
pages/          # Route-level composition — thin, delegates to components/
schemas/        # Zod schemas + z.infer types (no separate types/ folder)
  models/       # API/DB models
  locales/      # i18n key types
locale/         # Message JSON + typed intl wrapper
resources/      # API client functions
constants/      # as-const config objects
helpers/        # Pure utilities (cn, datetime, etc.)
```

`components/ui/`, `components/rhf/`, and `components/layout/` are invariant. The `<domain>/` layer is project-specific: use `features/` when the app is organised around navigation sections (e.g. `features/settings/`, `features/dashboard/`), or a model-centric structure when entities are shared across sections. A `common/` folder may also exist for reusable domain pieces shared across multiple areas (e.g. domain selects, shared form shells) — create it when the need arises. **Always match the existing project structure** — look at what is already there before adding new folders.

### Colocation

- Generic UI and reusable `hooks/data/*` → central folders above
- Feature-specific hooks and small sub-components → colocated with their feature block (e.g. `features/settings/blocks/departments/`)
- Multiple small components in one file is fine when they only serve one parent

### Input components and RHF wrappers

`components/ui/inputs/` contains standalone input components (uncontrolled, usable anywhere).
`components/rhf/inputs/` contains the RHF-controlled counterpart of each — these are what you use inside forms.

**Always use `RHF*` components inside forms** — never wire a raw `ui/inputs/` component to RHF manually.

If the input you need does not exist yet:

1. Add the base input to `components/ui/inputs/`
2. Add its RHF wrapper to `components/rhf/inputs/`

## File naming

- **kebab-case** for all files: `use-work-schedule.ts`, `create-user-role-form.tsx`
- Components: PascalCase export from a kebab-case file

## Schemas and types

- Zod schemas in `src/schemas/`; export types via `z.infer<typeof schema>`
- **`as const` objects** instead of TypeScript `enum`:

```ts
export const ROLES = { ADMIN: 'admin', DIRECTOR: 'director' } as const;
export type Role = (typeof ROLES)[keyof typeof ROLES];
```

- `z.nativeEnum(CONST_OBJECT)` to validate against const maps
- Factory schemas when error messages are i18n: `getCreateUserSchema(formatMessage)` returns Zod with translated messages

### Shared base schemas

All API model schemas extend `baseModelSchema` from `src/schemas/models/base-model.ts`:

```ts
export const myModelSchema = baseModelSchema.extend({
  id: z.number().int().positive(),
  name: z.string()
});
export type MyModel = z.infer<typeof myModelSchema>;
```

### Pagination and sorting

Reuse shared building blocks from `src/schemas/pagination.ts`:

- `paginationOptionsSchema` — `{ page, limit }` with coercion and defaults; base for list query param schemas
- `paginationSchema` — extends with `total`, `totalPages`
- `Sorting<TSortBy>` — `{ sortBy?, sortOrder? }` generic type
- `SortOrder` — `'asc' | 'desc'`

List query param schemas extend `paginationOptionsSchema` and add model-specific filters:

```ts
export const myListQueryParamsSchema = paginationOptionsSchema.extend({
  search: z.string().optional(),
  status: z.nativeEnum(STATUS).optional()
});
```

### URL params hooks

`hooks/ui/use-params.ts` provides two typed utilities:

- `useSearchParams(schema)` — reads/writes URL query params, Zod-parsed and auto-defaulted; returns `[params, setParams]`
- `useParams(schema)` — reads route path params, Zod-parsed

Use these instead of raw React Router hooks anywhere URL state is involved.

### Resources

`src/resources/` contains API client functions called by `queryFn` / `mutationFn`. One file per resource domain (e.g. `resources/department.ts`). Resources are plain async functions — no caching, no side effects; those live in hooks.

## i18n

- No hardcoded user-visible strings in components or hooks
- Use project `useIntl` / `FormattedMessage` from `src/locale/intl.tsx` — these are typed; IDs auto-complete
- Add keys under `src/locale/` message files
- Toast messages in command hooks via `formatMessage({ id: '...' })`

## Building features consistently

Before adding a screen:

1. Find the closest in-project sample under `src/pages/samples/` (page layout, tabs, form, data-table, etc.)
2. Reuse existing layout wrappers — never replicate Tailwind class strings to create layout
3. Extend UI primitives via new **cva variant** rather than a new one-off component
4. Wire data through hook patterns in `react-data-hooks` skill
5. Align with neighboring components in the same domain folder

## In-project samples

| Pattern                                     | Path                                              |
| ------------------------------------------- | ------------------------------------------------- |
| Simple RHF form (real page, good reference) | `src/pages/login.tsx`                             |
| RHF samples                                 | `src/pages/samples/tabs/tabs/react-hook-form.tsx` |
| Tables index                                | `src/pages/samples/tabs/tabs/tables/`             |
| Server table                                | `src/pages/samples/tabs/tabs/tables/data-table/`  |
| UI base                                     | `src/components/ui/base/`                         |
| RHF inputs                                  | `src/components/rhf/inputs/`                      |
