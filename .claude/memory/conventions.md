# Conventions

## Code Style
- TypeScript: strict mode, no `any`, explicit return types on public functions
- Python: type hints on ALL public functions, Google-style docstrings
- File naming: kebab-case for components, snake_case for Python modules
- Imports: grouped (stdlib → third-party → local), no wildcard imports

## Testing (TDD Required)
- RED: write failing test first
- GREEN: minimal code to pass
- REFACTOR: clean up while tests pass
- BUILD: `pnpm build` or `uv run` must succeed
- LINT: zero warnings
- COMMIT: conventional commit message

Backend: `cd api && pytest -q`
Frontend: `cd web && pnpm vitest run`

## Git
- Conventional commits: `feat(scope):`, `fix(scope):`, `refactor:`, `test:`, `docs:`, `chore:`
- One commit per story (squash if needed)
- Branch naming: `feat/story-N-short-name`

## API Design
- RESTful, JSON
- Error envelope: `{"error": {"code": "...", "message": "..."}}`
- Auth: Supabase JWT in Authorization header
- Pagination: cursor-based (keyset), `limit` + `cursor` params
- Async: long operations return `202 {job_id}` + polling endpoint

## Component Patterns
- shadcn/ui defaults — don't fight the library
- Custom components in `web/src/components/` (MetricCard, CoachNote, etc.)
- Server components by default, client only when interactive
- Mobile-first CSS, desktop via `@media (min-width: 1024px)`
