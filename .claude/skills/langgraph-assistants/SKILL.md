---
name: langgraph-assistants
description: LangGraph assistant architecture, BaseAssistant contract, state checkpointing, async execution, Redis streaming, prompt management. Use when building or modifying LLM assistants, graph nodes, tools, or chatbot infrastructure.
---

> Claude Code adaptation: migrated from `skills/langgraph-assistants/SKILL.md`. Use as a project skill under `.claude/skills/langgraph-assistants/SKILL.md`.

# LangGraph Assistants

## Assistant folder structure

```
assistants/
└── {name}/
    ├── assistant.py   # Extends BaseAssistant, builds the graph
    ├── nodes.py       # Graph node functions (business logic)
    ├── tools.py       # LangChain tools bound to nodes
    └── gpts.py        # Per-node LLM chain definitions (BaseGPT)
```

Register each assistant in `assistants/__init__.py`.

## BaseAssistant contract (saga-python-utils)

```python
class MyAssistant(BaseAssistant):
    def _build_graph(self) -> CompiledStateGraph:  # Define nodes + edges
    def _is_starting_state(self, state) -> bool:   # Validate entry state
    def _is_ending_state(self, state) -> bool:     # Detect terminal state
    def _update_state_with_error(self, state, error):  # Error handling
```

Methods available: `invoke(state, execution_id)`, `stream(state, execution_id)`, `get_state(execution_id, checkpoint_id)`.

## State and checkpointing

- LangGraph state persisted via `langgraph-checkpoint-postgres` (PostgresSaver)
- Checkpointer pool initialized in `crud/checkpointer.py`
- State retrieval: `GET /assistant/{slug}/execution/{id}/state/{checkpoint_id}`

## Async execution pattern (template-bot)

```
POST /predict → 202 Accepted (background graph execution)
  ├── Callbacks → executionStart / executionDone / executionError
  ├── Tokens → Redis pub/sub ({prefix}:conversation:{execution_id})
  └── State → Postgres checkpoints
```

Sentinel tokens: `[DONE]`, `[ERROR]`.

## Resources

One module per external system in `resources/`:

- `azure_openai.py`, `bedrock.py` — LLM clients
- `redis.py` — streaming pub/sub
- `langfuse.py` — tracing + prompt sync
- `vector_store.py` — pgvector retrieval (if RAG)

## Config

Pydantic model in `config.py` loading from env vars. All secrets via environment, never in code.

## Prompt management

- `PromptsLibrary` from saga-python-utils syncs with LangFuse
- Dev: auto-pushes prompt updates on startup
- Prod: fetches tagged versions only
- Never hardcode prompt text in source files

## BaseGPT pattern

Wraps `prompts_library.build_llm_chain(prompt_name, llm)` with optional `output_model` for structured responses.

## Simple LLM projects (template-llm)

- Served via `saga-predictor.serve()` (Flask), not FastAPI
- `predict()` delegates to `helpers/predict.py`
- `get_report()` returns `{}` (no trained model)
- No checkpointing, no Redis streaming, no callbacks

## Testing

- `MemorySaver` instead of real Postgres checkpointer
- Mock LLM responses in `tests/mocks/` (canned completions, streaming chunks)
- Mock Redis publish; mock callback HTTP calls
- `FastAPI TestClient` for router tests
- `conftest.py` clears env and injects test config
