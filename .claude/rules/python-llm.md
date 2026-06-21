# Python Llm Rule

> Source: `rules/python-llm.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: LLM/bot project conventions — assistants, LangGraph, FastAPI, prompts, streaming
globs:
  - "**/assistants/**/*.py"
  - "**/graphs/**/*.py"
  - "**/gpts/**/*.py"
  - "**/routers/**/*.py"
  - "**/prompts/**/*.py"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# LLM/Bot Context

This file is part of an LLM or chatbot project (LangGraph assistants, prompt orchestration, streaming).

- Each assistant lives in `assistants/{name}/` with `assistant.py`, `nodes.py`, `tools.py`, `gpts.py`
- Conversation logic stays in assistant nodes — never in routers
- Resources (LLM clients, Redis, vector stores) in `resources/`; one module per external system
- Config via Pydantic `config.py` from env vars
- Prompts managed via `PromptsLibrary` + LangFuse; never hardcode prompt text in code

For deep work, apply `python-llm-expert` and read `langgraph-assistants`.

Do not suggest s1-s5 pipeline stages, model artifact storage, or GPU training in this context.
