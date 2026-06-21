# Python Ml Rule

> Source: `rules/python-ml.mdc`. Adapted for Claude Code. Cursor frontmatter was converted to prose because Claude Code does not support Cursor `globs` / `alwaysApply` semantics directly.

## Source metadata

```yaml
description: Classical ML project conventions — pipeline stages, predictor, model artifacts, GPU training
globs:
  - "**/s[0-9]_*/**/*.py"
  - "**/*_pipeline.py"
  - "**/config/*.json"
  - "**/model/**/*.py"
```

## Claude Code application guidance

- If this rule was `alwaysApply`, treat it as general project guidance.
- If this rule had `globs`, apply it when the touched files match the source metadata patterns.
- Deterministic safety constraints should be enforced by hooks in `.claude/hooks/`, not by prose alone.

# Classical ML Context

This file is part of a classical ML project (training pipelines, model artifacts, saga-predictor).

- Pipeline stages: `s1_data_loaders` → `s2_data_transformers` → `s3_models` → `s4_trainers` → `s5_evaluaters`
- Inference-time logic belongs in `helpers/`; the predictor loads from there
- Config lives in `config/*.json`; pipelines accept `--config` argument
- Model artifacts in `model/` locally, uploaded to S3 for production
- Data management via functions in `data/data_management.py` (no loose code outside functions)

For deep work, apply `python-ml-expert` and read `ml-training-pipelines`.

Do not suggest LangGraph, FastAPI, LangFuse, or assistant patterns in this context.
