---
name: ml-training-pipelines
description: Classical ML pipeline architecture, predictor contract, GPU server workflow, model artifacts, and data management. Use when working on training pipelines, predictors, hyperoptimization, evaluation, GPU Docker services, or remote server sync scripts.
---

> Claude Code adaptation: migrated from `skills/ml-training-pipelines/SKILL.md`. Use as a project skill under `.claude/skills/ml-training-pipelines/SKILL.md`.

# ML Training Pipelines

## Pipeline architecture

Numbered stages in `src/`:

```
s1_data_loaders/      → Load and split raw data
s2_data_transformers/ → Feature engineering
s3_models/            → Model definition
s4_trainers/          → Training logic
s5_evaluaters/        → Validation metrics
```

Orchestrated by `training_pipeline.py`, `hyperoptimization_pipeline.py`, `testing_pipeline.py` — each accepts `--config config/<name>.json`.

## Predictor contract (`BasePredictor`)

```python
class Predictor(BasePredictor):
    def load(self):        # Load model from self.model_path
    def get_report(self):  # Return metrics dict (report.json)
    def predict(self, data: InputModel) -> OutputModel:
```

Served via `saga-predictor`: `python -m src.resources.predictor` → Flask on configured port.

## `helpers/`

All inference-time logic lives here. The predictor imports from `helpers/`; pipeline stages also reference it for consistency between training and serving.

## Model artifacts

- Local: `model/` folder (pickle, weights, report.json, md5)
- Production: uploaded to S3 (`s3://{bucket}/models/model_latest`); pulled at container start if `api_pulls_model_from_s3=true`

## Remote server workflow

Primary execution happens on Sagacify servers — not locally. Local machine is for editing + IDE only.

**Connecting to the server:**

The target server depends on the project — check `sync.sh` or AGENTS.md for the hostname.

```bash
ssh -i ~/.ssh/{key} {username}@{ML_SERVER_HOSTNAME}
cd ~/projects/{client}/{project}
```

SSH key path, username, and hostname are project-specific.

| Step | Command/action |
|------|----------------|
| Sync code to server | `./sync.sh` (rsync over SSH; excludes `.venv`, `data`, `model`, `notebooks`) |
| Upload notebooks | `./sync_notebooks.sh` |
| Download notebooks | `./download_notebooks.sh` |
| Download model | `./download_model.sh` |
| Start notebooks | On server: `docker compose up notebooks` → access `http://{ML_SERVER_HOSTNAME}:{TRUE_PORT}/lab` |
| Run training (CPU) | `docker compose run --rm notebooks uv run --no-sync python src/training_pipeline.py --config config/training_config.json` |
| Run training (GPU) | `docker compose run --rm gpu uv run --no-sync python src/training_pipeline.py --config config/training_config.json` |

## GPU services

- Separate `gpu.Dockerfile` (CUDA runtime, may compile extensions)
- `runtime: nvidia`, `shm_size: 8gb`
- GPU pinning: `NVIDIA_VISIBLE_DEVICES` (UUID avoids conflicts) + `CUDA_VISIBLE_DEVICES` (index inside container)
- `TRUE_HOSTNAME` + `TRUE_PORT` configure Jupyter for remote browser access

## Data volumes

- Server: `/media/data/{client}/{project}/` mounted into containers
- Local: data volume lines commented out in `docker-compose.yml`
- Docker entrypoint remaps UID/GID (`FIXUID`/`FIXGID`) + supplementary groups for shared dirs

## Data management

Functions in `data/data_management.py` — callable from pipeline script or notebook cells. No loose code outside function definitions.

## Config

JSON files in `config/` drive all pipeline behavior: data paths, model params, hyperopt search space, eval metrics.
