---
name: node-backend-logging
description: Defines structured logging conventions for Node.js backends targeting ELK. Use when adding or modifying backend logs, logger setup, or error logging (event names, indexed/raw fields, saga-logger, pino).
---

> Claude Code adaptation: migrated from `skills/node-backend-logging/SKILL.md`. Use as a project skill under `.claude/skills/node-backend-logging/SKILL.md`.

# Node Backend Logging

When working on Node.js backends:

- **Event names**: `UPPER_SNAKE_CASE`.
- **ELK target**: one index per service per day.
- **Log shape**:
  - `event` (required)
  - `indexed` (stable, searchable fields)
  - `raw` (context, non-indexed)
  - `error` (dedicated field for errors)

## If `saga-logger` exists

Log with: `(event, indexed, raw)`.

## Else (default: `pino`)

Log a single object:

```js
logger.info({
  event: 'EVENT_NAME',
  indexed: {},
  raw: {},
  error: {},
  anyRawField: 123,
})
```
