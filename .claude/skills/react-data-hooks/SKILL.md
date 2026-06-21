---
name: react-data-hooks
description: TanStack Query data hooks for React apps — CQRS query vs command hooks, stable query keys, URL-synced filters via useSearchParams+zod, invalidation, toasts, and optimistic rules. Use when creating or modifying hooks in src/hooks/data or feature data fetching.
---

> Claude Code adaptation: migrated from `skills/react-data-hooks/SKILL.md`. Use as a project skill under `.claude/skills/react-data-hooks/SKILL.md`.

# React Data Hooks (TanStack Query + CQRS)

## CQRS split

| Kind        | Naming                                                              | Responsibility                                      |
| ----------- | ------------------------------------------------------------------- | --------------------------------------------------- |
| **Query**   | `useXxxListQuery`, `useXxxByIdQuery`                                | Read-only fetch via `useQuery` / `useInfiniteQuery` |
| **Command** | `useCreateXxxCommand`, `useUpdateXxxCommand`, `useDeleteXxxCommand` | Writes via `useMutation`; owns all side effects     |

Commands **invalidate** queries — never permanently replace read models with `setQueryData`.

## Query hooks

Two common shapes — pick based on the use case:

```ts
// Plain list — for dropdowns, selects, reference data. No URL params.
export const useDepartmentListQuery = () =>
  useQuery<Department[]>({ queryKey: DEPARTMENT_LIST_KEY, queryFn: getDepartmentList });

// URL-driven list — for data tables with filters, sort, pagination in the URL.
export const useWorkScheduleListQuery = () => {
  /* see URL-synced section below */
};
```

- `queryFn` calls `resources/*` API functions
- Map API → UI shape inside the hook (defaults, flattened pages)
- Export **stable query key constants** at the top of the file; build a factory function when filters/pagination vary:

```ts
export const WORK_SCHEDULE_KEY = 'work-schedule' as const;
export const WORK_SCHEDULE_LIST_KEY = [WORK_SCHEDULE_KEY, 'list'] as const;

const getWorkScheduleListQueryKey = (
  page?: number,
  limit?: number,
  filters?: WorkSchedulesFilters
) => [...WORK_SCHEDULE_LIST_KEY, page, limit, filters];
```

For a plain list (no pagination), a constant key is enough: `export const DEPARTMENT_LIST_KEY = [DEPARTMENT_KEY, 'list'] as const;`

- Include filters, sort, and pagination in the query key
- Return `setFilters`, `setPagination`, `setSorting` helpers when the list is URL-driven

## URL-synced list params

URL syncing applies to list hooks that are the **primary content of a page** — paginated or infinite lists where the user actively filters, sorts, or paginates (data tables, infinite scroll cards, etc.) and where preserving that state in the URL makes sense. Do not apply it to hooks that fetch reference data for a select/dropdown (those are plain `useQuery` with no search params).

Filters/sort/pagination/search that change the dataset **live in the data hook**, not in the component:

```ts
export const useWorkScheduleListQuery = () => {
  const [params, setParams] = useSearchParams(workSchedulesListQueryParamsSchema);
  const { page, limit, ...filters } = params;

  const query = useQuery<WorkSchedulesPaginatedList>({
    queryKey: getWorkScheduleListQueryKey(page, limit, filters),
    queryFn: () => getWorkScheduleList({ page, limit, filters })
  });

  return {
    ...query,
    data: {
      data: query.data?.data ?? [],
      pagination: query.data?.pagination ?? { page: 0, limit: 0, total: 0, totalPages: 0 }
    },

    filters,

    setPagination: (pagination: { page: number; limit: number }) =>
      setParams({ ...params, page: pagination.page, limit: pagination.limit }),

    setFilters: (f: Partial<typeof filters>) => setParams({ ...params, page: 1, ...f }),

    setSorting: ({ sortBy, sortOrder }: Sorting<WorkScheduleSortBy>) =>
      setParams({ ...params, page: 1, sortBy, sortOrder })
  };
};
```

- Define `*ListQueryParamsSchema` next to the model in `schemas/models/`
- Reset `page` to 1 on filter or sort change
- Debounce text inputs in the UI layer, not in the schema or hook

## Command hooks

Each command hook is fully self-contained:

```ts
export const useCreateWorkScheduleCommand = () => {
  const queryClient = useQueryClient();
  const { formatMessage } = useIntl();
  return useMutation<WorkSchedule, AxiosError, CreateWorkSchedule>({
    mutationFn: data => createWorkSchedule(data),
    onSuccess: () => {
      toast.success(formatMessage({ id: 'workSchedules.upsertForm.toasts.create.successMessage' }));
      queryClient.invalidateQueries({
        queryKey: WORK_SCHEDULE_LIST_KEY
      });
    },
    onError: () => {
      toast.error(formatMessage({ id: 'workSchedules.upsertForm.toasts.create.errorMessage' }));
    }
  });
};
```

Owns: toasts, `invalidateQueries`, `useNavigate` redirects, cross-entity invalidation.
Does **not**: duplicate toasts in the form component; update state without invalidating.

## Debounce

Filter inputs that write to URL params must debounce. Prefer existing debounced input components from `components/ui/inputs/` (`SearchInput`, `DebouncedSelectInput`) — they handle debouncing internally via `useDebounceValueChanges`. See `react-ui` skill for the full convention and how to add a missing debounced variant.

When you need to debounce directly in a hook or custom component, use `hooks/ui/use-debounce.ts`:

- `useDebounceValue(value, delayMs?)` — debounced derived value; for read-only/uncontrolled cases
- `useDebounceValueChanges(value, onValueChange, delayMs?)` — controlled: local state updates immediately, `onValueChange` fires debounced; `handleClear` cancels pending and fires immediately

## Infinite scroll

Infinite lists need two pieces:

1. `useInfiniteQuery` in the data hook (with `getNextPageParam`)

```ts
export const usePointOfServiceInfiniteListQuery = () => {
  const [params, setParams] = useSearchParams(pointsOfServiceListQueryParamsSchema);
  const { ...filters } = params;

  const query = useInfiniteQuery({
    queryKey: getPointOfServiceListQueryKey(filters),
    queryFn: ({ pageParam }) => getPointOfServiceList({ page: pageParam, filters, limit: 50 }),
    initialPageParam: 1,
    getNextPageParam: lastPage => {
      const { page, totalPages } = lastPage.pagination;
      return page < totalPages ? page + 1 : undefined;
    },
    refetchOnWindowFocus: true
  });

  return {
    ...query,
    data: query.data?.pages.flatMap(page => page.data) ?? [],
    totalCount: query.data?.pages[0]?.pagination.total ?? 0,
    filters,
    setFilters: (f: Partial<typeof filters>) => setParams({ ...params, ...f })
  };
};
```

2. `useInfiniteScrollTrigger` from `hooks/ui/use-infinite-scroll-trigger.ts` — wires an `IntersectionObserver` ref to `fetchNextPage`

```ts
const {
  data: pointsOfServices,
  totalCount: totalPointsOfServicesCount,
  isLoading: isLoadingPointsOfServices,
  isError: isErrorPointsOfServices,
  filters,
  setFilters,
  fetchNextPage,
  hasNextPage,
  isFetchingNextPage
} = usePointOfServiceInfiniteListQuery();

const containerRef = useRef<HTMLDivElement>(null);
const { ref: sentinelRef } = useInfiniteScrollTrigger({
  hasNextPage,
  isFetchingNextPage,
  fetchNextPage,
  options: { root: containerRef.current ?? undefined, threshold: 0.1 }
});
// Render: <div ref={sentinelRef} /> at the bottom of the list
```

## Components stay dumb

- Components receive `data`, `isLoading`, `isError`, `setFilters`, etc. from hooks — no local filter state
- Feature orchestration hooks colocate with the feature block, not in `src/hooks/data/`

## Caching

- Prefer broad invalidation over fragile partial updates
- Use `enabled` when a query depends on route params or prior data
- List + detail share key prefixes so detail mutations refresh the list on back navigation

## Optimistic updates

- Temporary `setQueryData` patch before server confirms: allowed
- Permanent replacement without invalidation: **not allowed**
- Skip invalidation: **not allowed**
- Optimistic auth / security-critical state: **not allowed**

## Hook placement

| Scope                              | Location                                                                                              |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Single resource                    | `src/hooks/data/use-<resource>.ts` (e.g. `use-department.ts`)                                         |
| Domain with multiple sub-resources | `src/hooks/data/<domain>/use-<resource>.ts` (e.g. `point-of-service/use-point-of-service.ts`)         |
| Feature-specific orchestration     | Colocated next to the feature block (e.g. `use-selected-department.ts` next to the departments block) |

## References (in this project)

- Simple CRUD: `src/hooks/data/use-<resource>.ts`
- URL + pagination + sort: see any `useXxxListQuery` that uses `useSearchParams`
- Table query: `src/pages/samples/tabs/tabs/tables/data-table/use-test-data.ts`
