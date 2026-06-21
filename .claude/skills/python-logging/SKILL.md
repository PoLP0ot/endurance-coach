---
name: python-logging
description: Structured logging conventions for Python services using saga-logger. Use when adding or modifying logs, logger setup, or log formatting in Python ML/LLM projects.
---

> Claude Code adaptation: migrated from `skills/python-logging/SKILL.md`. Use as a project skill under `.claude/skills/python-logging/SKILL.md`.

# Python Logging

## Logger

Use `saga-logger` (`SagaLogger`) — structured JSON logging targeting ELK/Datadog.

```python
from saga_logger import SagaLogger

logger = SagaLogger(__name__)
logger.info("EVENT_NAME", index={"key": "value"}, raw={"context": data})
```

## Log shape

- **`event`** (first arg): `UPPER_SNAKE_CASE` event name
- **`index`**: stable, searchable fields — keys must be **camelCase** and scalar (no nested objects)
- **`raw`**: context data, non-indexed (request body, stack trace)

## Rules

- The set of `index` keys must be **fixed per event** — no conditional keys. If a value is absent, pass `None`.
- Use `logger.warn(...)` — not `logger.warning(...)`.
- Available levels: `trace`, `debug`, `info`, `warn`, `error`, `fatal`.

## Environment variables

| Var | Purpose | Default |
|-----|---------|---------|
| `LOG_LEVEL` | Minimum level (debug/info/warn/error) | `info` |
| `LOG_PRETTY` | Human-readable colored output for local dev | `false` |
| `LOG_STACK_LEVEL` | Include call stack info | `false` |

- `LOG_PRETTY=true`: colored multi-line format locally (level colors: grey/blue/green/yellow/red)
- `LOG_PRETTY=false`: single-line JSON for production (ELK/Datadog ingestion)
