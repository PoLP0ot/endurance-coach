---
name: react-forms-tables
description: React forms and tables — React Hook Form with zodResolver, RHF input components, useFieldArray, Form patterns, and TanStack Table with server-side pagination and URL filters. Use when building forms, list pages, or data tables.
---

> Claude Code adaptation: migrated from `skills/react-forms-tables/SKILL.md`. Use as a project skill under `.claude/skills/react-forms-tables/SKILL.md`.

# React Forms & Tables

## Forms (React Hook Form + Zod)

### Required pattern

1. Schema in `src/schemas/` — use `getXxxSchema(formatMessage)` factory when error messages are i18n
2. `useForm<T>({ resolver: zodResolver(schema) })`
3. Render inside `Form` from `@/components/rhf/form` (or a project-level `UpsertForm` wrapper for create/edit flows)
4. Fields via **`RHF*`** components from `@/components/rhf/inputs/` — never `<input {...register()}>` when an RHF wrapper exists
5. Submit: `handleSubmit` → command hook `mutateAsync` → optional `onSuccess` callback
6. Conditional fields: `useWatch` to read dependent value + `setValue` / `useEffect` to clear it

```tsx
const { formatMessage } = useIntl();
const createUserRoleCommand = useCreateUserRoleCommand();

const methods = useForm<CreateUserRole>({
  resolver: zodResolver(getCreateUserRoleSchema(formatMessage))
});

const onSubmit = useCallback(
  async (data: CreateUserRole) => {
    await createUserRoleCommand.mutateAsync({ userId, data });
    onSuccess?.();
  },
  [createUserRoleCommand, onSuccess]
);

const role = useWatch({ control: methods.control, name: 'role' });
const isDepartmentRole = useMemo(() => isRole.departmentRole(role), [role]);
const isPointOfServiceRole = useMemo(() => isRole.pointOfServiceRole(role), [role]);

useEffect(() => {
  if (!isDepartmentRole) {
    methods.setValue('departmentId', null);
  }
  if (!isPointOfServiceRole) {
    methods.setValue('pointOfServiceId', null);
  }
}, [isDepartmentRole, isPointOfServiceRole]);

return (
  <Form
    methods={methods}
    onSubmit={onSubmit}
    className={cn('w-full flex flex-col gap-6 justify-center', className)}
  >
    <RHFRoleSelect
      name='role'
      label={formatMessage({
        id: 'users.createUserRoleForm.inputs.role.label'
      })}
      placeholder={formatMessage({
        id: 'users.createUserRoleForm.inputs.role.placeholder'
      })}
      required
    />
    {isDepartmentRole && (
      <RHFDepartmentSelect
        name='departmentId'
        label={formatMessage({
          id: 'users.createUserRoleForm.inputs.department.label'
        })}
        placeholder={formatMessage({
          id: 'users.createUserRoleForm.inputs.department.placeholder'
        })}
        className='w-full'
        required
      />
    )}
    {isPointOfServiceRole && (
      <RHFPointOfServiceSelect
        name='pointOfServiceId'
        label={formatMessage({
          id: 'users.createUserRoleForm.inputs.pointOfService.label'
        })}
        placeholder={formatMessage({
          id: 'users.createUserRoleForm.inputs.pointOfService.placeholder'
        })}
        className='w-full'
        required
      />
    )}
    <RHFTextInput
      name='description'
      placeholder={formatMessage({ id: 'users.createUserRoleForm.inputs.description.label' })}
      label={formatMessage({ id: 'users.createUserRoleForm.inputs.description.label' })}
    />
    <div className='mt-4 w-full flex justify-end items-center gap-2.5'>
      <Button
        type='button'
        variant='outline'
        onClick={onCancel}
        disabled={methods.formState.isSubmitting}
      >
        {formatMessage({ id: 'cancel' })}
      </Button>
      <Button type='submit' disabled={methods.formState.isSubmitting}>
        {formatMessage({ id: 'create' })}
      </Button>
    </div>
  </Form>
);
```

### useFieldArray

Use for dynamic repeating rows with the same RHF + zod discipline.

### Samples (in this project)

- RHF samples: `src/pages/samples/tabs/tabs/react-hook-form.tsx`
- Schema factory pattern: `src/schemas/` — `getXxxSchema(formatMessage)` returns Zod with i18n errors

## Tables (TanStack Table)

### Choose the right component

| Need                               | Component                                                         |
| ---------------------------------- | ----------------------------------------------------------------- |
| Server pagination + sort + filters | `DataTableWithServerSidePagination`                               |
| Client-only pagination/sort        | `DataTable`                                                       |
| Fully custom layout                | `{ Table }` from `@/components/ui/data-table/table` — last resort |

### Server-side list page

1. **Query hook** owns URL params + `useQuery` — see `react-data-hooks` skill
2. **Column defs** in `useMemo`; `ColumnDef<T>[]` with `enableSorting` aligned to API sort keys
3. **Filters** via debounced inputs from `components/ui/inputs/` (`SearchInput`, `DebouncedSelectInput`, etc.)
4. Pass `data`, `pagination`, `sorting`, `onPaginationChange`, `onSortingChange`, `isLoading` to `DataTableWithServerSidePagination`
5. Always provide `getRowId` for stable row selection

### Feature file layout

```
<domain>/blocks/<resource>/
  index.tsx               # composes filters + table
  <resource>-table.tsx    # column defs + DataTableWithServerSidePagination
  <resource>-filters.tsx  # optional — split out when filter bar is complex
```

(`<domain>/` follows the project's existing folder convention — may be `features/`, a model name, etc.)

Data hook lives in `src/hooks/data/use-<resource>.ts` and exports `useXxxListQuery`. For example: `hooks/data/use-work-schedule.ts` → `useWorkScheduleListQuery`.

### References (in this project)

- Sample: `src/pages/samples/tabs/tabs/tables/data-table/index.tsx`
- Component: `src/components/ui/data-table/data-table-with-server-side-pagination.tsx`

## Forms + tables together

- Table row actions (edit, delete) call **command hooks** — invalidate list query keys on success
- Create/edit modals reuse the same `CreateX` / `UpdateX` Zod types as the form schema

## Anti-patterns

- Multiple `useState` calls for filter fields on a list page
- `useEffect` + manual fetch instead of TanStack Query
- `<input {...register('field')} />` when `RHFTextInput` exists
- Inline column render logic duplicated across pages — extract shared cell components
