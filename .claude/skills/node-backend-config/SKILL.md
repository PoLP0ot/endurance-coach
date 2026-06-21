---
name: node-backend-config
description: Node.js backend configuration and external resource patterns. Use when working on config.ts, environment variables, src/resources/, or test config overrides in Node backends.
---

> Claude Code adaptation: migrated from `skills/node-backend-config/SKILL.md`. Use as a project skill under `.claude/skills/node-backend-config/SKILL.md`.

# Node Backend Config

## Configuration and environment variables

- **Mirror env names in config**: use a predictable mapping from `process.env` to the config object (e.g. `APP_*` → `config.app.*`, `PG_*` → `config.pg.*`, `LOG_*` → `config.log.*`). Avoid renaming env vars to different property names unless there is a strong reason.
- **No hidden env "magic"**: build `configValues` with straightforward assignments from `process.env`. Do not wrap reads in helpers whose behavior is non-obvious; validation belongs in one place (e.g. a Zod `configSchema.parse(configValues)` at the end).
- **Structured values in env**: when a setting is naturally a list or object (allowed CORS origins, feature flags, etc.), store it as a **JSON string** in a single env var and assign with **`JSON.parse(env.MY_VAR ?? '')`** (or an explicit sentinel like `'[]'` only if the team agrees). The parsed value is what lands on the config object; **Zod** should still validate shape and types on the full config.
- **Operational defaults**: document non-secret defaults in **Docker Compose** (or equivalent) so `docker compose up` matches local expectations. Secrets stay out of compose files unless using secrets/CI injection.
- **Tests**: the test runner must define any env vars that are **required** at import time (e.g. `APP_ALLOWED_ORIGINS` when config uses `JSON.parse` without a safe empty default). Prefer `vitest.config.ts` `test.env` (or the project's equivalent) so `npm test` works without hand-exporting variables.
- **`NODE_ENV === 'test'` overrides**: force fake or local-safe values **only** in **`config.ts`** (single `if (NODE_ENV === 'test') { ... }` block). Do not scatter `NODE_ENV` checks across resources, helpers, or routes to special-case tests.
- **CORS and auth origins**: when using cookie-based auth, keep **CORS `origin`** and the auth library's **`trustedOrigins`** (or equivalent) aligned with `config.app.allowedOrigins` (plus the API's own `app.url` where needed), all driven from the same env-backed config.

## External resources (`src/resources/`)

- **One module per external system**: whenever the app needs a long-lived client or connection to something outside the process (PostgreSQL via Prisma, **S3**, **SQS**, **Redis**, a typed HTTP client for a third-party API, etc.), initialize it in **`src/resources/<name>.ts`** (e.g. `db.ts`, `s3.ts`, `sqs.ts`).
- **Resources read `config`**: wire credentials, endpoints, regions, and pools from **`config`** only inside resource modules — same pattern as `db.ts`.
- **Helpers and routes stay dumb**: **helpers** must not construct SDK clients or call `config` for connection setup. They should accept already-built clients (and primitives like bucket names) as **parameters**, or be thin wrappers called from routes that import from `resources/`.
- **Fakes in tests**: if an integration must be avoided in CI (no real AWS/SQS), expose behavior via **config fields** set **only in the `config.ts` test block** (e.g. stub base URLs, fake buckets). Resources stay real clients built from that config; routes may branch on config flags/optional URLs, not on `NODE_ENV`.
