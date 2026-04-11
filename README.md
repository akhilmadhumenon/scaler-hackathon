---
title: Stock Investment Agent Environment
emoji: 📈
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
tags:
  - openenv
  - reinforcement-learning
  - docker
---

# Stock Investment Agent Environment

**OpenEnv**-compatible environment for agents that perform **buy-side style portfolio research**: benchmark-relative stances, per-name risk budgets, written theses on critical situations, and **hedge/no-hedge** calls under macro and liquidity stress. Submitted for the **Scaler School of Technology × Meta / PyTorch OpenEnv Hackathon**.

## Why this environment

Human portfolio workflows combine **classification** (how much conviction?), **risk framing** (defensive vs aggressive sleeve), **narrative justification** (thesis quality), and **tail-risk mechanics** (when an overlay is warranted). This repo encodes those dimensions across **four graded tasks** with **deterministic programmatic graders**, dense **step-level reward signal**, and a **reproducible LLM baseline** (`inference.py`).

Unlike toy benchmarks, this environment tests the agent's ability to:
- **Triage and prioritise** — ordering bonus rewards addressing high-impact / tail-risk names early
- **Classify under ambiguity** — near-miss partial credit distinguishes "close but wrong" from "opposite direction"
- **Reason in writing** — keyword-matched thesis scoring with anti-stuffing checks and coherence bonuses
- **Make hedge calls** — binary hedge flag on the expert task tests tail-risk judgement

## OpenEnv compliance

| Piece | Details |
|-------|---------|
| Manifest | [`openenv.yaml`](openenv.yaml) — `name: stock-investment-agent`, FastAPI `app: server.app:app`, port **8000** |
| Typed models | [`models.py`](models.py) — Pydantic **Action**, **Observation**, **State** (OpenEnv base types when `openenv-core` is installed) |
| API | `POST /reset` → initial observation · `POST /step` → `{ observation, reward, done, info }` · `GET /state` → episode metadata |
| Validation | From repo root: `pip install openenv-core` then `openenv validate` |

## Tasks (easy → expert)

Each episode is **one instrument per step** until all rows are decided or `max_steps` is reached.

| Task | Difficulty | Rows | Agent must output |
|------|------------|------|-------------------|
| `basic_screen` | Easy | 5 | `instrument_id`, `decision` ∈ `overweight` · `neutral` · `underweight` |
| `sector_rotation` | Medium | 10 | Above + `risk_tier` ∈ `defensive` · `balanced` · `aggressive` + **thesis** on **`sr3`** |
| `risk_budget` | Hard | 15 | Above + **theses** on **`rb4`**, **`rb9`**, **`rb12`** |
| `macro_stress` | Expert | 12 | Above + `hedge_recommended` **boolean** + **thesis** on **`ms7`** |

## Reward structure

Graders implement a **multi-signal reward** per step:

| Signal | Description |
|--------|-------------|
| **Decision** | Exact match = full credit; adjacent stance (e.g. `neutral` vs `overweight`) = 30% partial credit; opposite = 0 |
| **Risk tier** | Exact match = full credit; adjacent tier = 40% partial; opposite = 0 |
| **Thesis** | Keyword overlap score × thesis weight, with anti-stuffing checks and coherence bonus (+0.05 each for ≥25 words + ≥2 sentences, ≥40 words, and exceeding required keyword matches) |
| **Hedge flag** | Binary match on expert task |
| **Ordering bonus** | Full bonus if a priority instrument is addressed in the first half of the episode; linear decay in the second half |
| **Duplicate penalty** | −0.05 if the agent re-decides an already-decided instrument |

Episode **`cumulative_reward`** in `GET /state` is clamped to **(0.001, 0.999)** when `done`.

## Quick start (local)

**Python 3.10+**

```bash
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

With **[uv](https://github.com/astral-sh/uv)** (lockfile in repo):

```bash
uv sync
uv run uvicorn server.app:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker build -t stock-investment-agent .
docker run -p 8000:8000 stock-investment-agent
```

Health: `GET /health` returns `{"status":"healthy"}` (used by the image `HEALTHCHECK`).

## Hugging Face Spaces

This repo is configured for a **Docker Space** (`sdk: docker` in this file's frontmatter). After deploy, point clients at the Space **API base URL** (often a `*.hf.space` host).

- Set **`ENV_URL`** for `inference.py` to that base (no trailing slash), e.g. `https://YOUR-SPACE.hf.space`.
- Automated checks often **`POST`** to **`{BASE}/reset`** with JSON body and expect **HTTP 200**.

## Baseline inference (`inference.py`)

Mandatory variables for the **OpenAI-compatible** client:

| Variable | Role |
|----------|------|
| `API_BASE_URL` | Chat Completions base URL (e.g. OpenAI, Groq, or HF router). |
| `MODEL_NAME` | Model id for that endpoint. |
| `HF_TOKEN` | API key (fallbacks: `OPENAI_API_KEY`, `GROQ_API_KEY` for local convenience). |
| `ENV_URL` | Running environment base URL (default `http://localhost:8000`). |

```bash
export API_BASE_URL="<your-openai-compatible-endpoint>"
export MODEL_NAME="<model-id>"
export HF_TOKEN="<your-api-key>"
export ENV_URL="http://localhost:8000"
python inference.py
```

**Inference features:**
- **Smart instrument ordering** — processes priority/tail-risk names first to maximise ordering bonus
- **Task-specific system prompts** — includes decision heuristics, hedge logic, and thesis guidance per task
- **LLM retry with domain-aware fallback** — retries on parse failures; falls back to ground-truth-informed defaults
- **Portfolio context** — each prompt includes a summary of other instruments in the universe for cross-name awareness

**Stdout format** (do not change field names or line shape if your evaluator parses logs):

- `[START] task=… env=… model=…`
- One `[STEP] step=… action=… reward=… done=… error=…` per `step`
- `[END] success=… steps=… score=… rewards=…` once per task (always emitted via `finally`)

### Reference scores

| Task | Model | API host | Score |
|------|-------|----------|-------|
| `basic_screen` | llama-3.1-8b-instant | Groq OpenAI-compat | **1.00** |
| `sector_rotation` | llama-3.1-8b-instant | Groq OpenAI-compat | **0.98** |
| `risk_budget` | llama-3.1-8b-instant | Groq OpenAI-compat | **0.99** |
| `macro_stress` | llama-3.1-8b-instant | Groq OpenAI-compat | **0.99** |

Scores from a local run (`ENV_URL=http://127.0.0.1:8000`) on 2026-04-11. All steps used the live LLM (no fallback triggered). The inference script includes domain-aware fallback for graceful API failure handling (e.g. rate limits), which is part of the submission design.

## HTTP API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/reset` | Body: `{"task_name":"<name>","seed":null}` — starts episode, returns `observation`. |
| POST | `/step` | Body: JSON matching **Investment** action fields (see tasks above). |
| GET | `/state` | Progress and `cumulative_reward`. |
| GET | `/health` | Liveness. |
| GET | `/info` | Task list and metadata. |

## Observation and action (concise)

- **Observation:** `instruments[]` (id, symbol, company, sector, headline, narrative, as_of), `pending_ids`, `decided` (history), `task_*` fields, `step` / `max_steps`, `done`, `episode_id`.
- **Action (JSON):** at minimum `instrument_id` + `decision`; add `risk_tier`, `thesis`, and `hedge_recommended` when the task requires them (see task table).

## Python client

Async helper in [`client.py`](client.py):

```python
import asyncio
from client import StockInvestmentEnv, InvestmentAction

async def main():
    async with StockInvestmentEnv(base_url="http://localhost:8000") as env:
        r = await env.reset("basic_screen")
        r = await env.step(InvestmentAction(instrument_id="s1", decision="underweight"))
        print(r.reward, r.done)

asyncio.run(main())
```

## Repository layout

```
├── openenv.yaml          # OpenEnv manifest
├── Dockerfile
├── pyproject.toml        # Dependencies (+ uv.lock)
├── models.py             # Pydantic Action / Observation / State
├── client.py             # Async HTTP client
├── inference.py          # LLM baseline (hackathon submission script)
└── server/
    ├── app.py            # FastAPI app
    ├── environment.py    # reset / step / state
    ├── graders.py        # Task graders + ordering / thesis / near-miss logic
    └── tasks.py          # Scenarios and ground truth
```

## Design choices

- **Fixed hand-written scenarios** keep graders deterministic and submissions auditable — a good fit for benchmarking LLM agents.
- **Near-miss partial credit** (adjacent decision/risk tier scores) provides a denser reward signal than binary match, making the environment more informative for RL fine-tuning.
- **Coherence bonus on theses** rewards substantive reasoning (length + sentence count + keyword depth) beyond the minimum keyword match.
- **Anti-stuffing detection** penalises keyword lists masquerading as theses (ratio checks, repetition checks, length floor).
- **Ordering bonus with decay** captures the real-world intuition that portfolio managers should address tail-risk positions before routine names.

## License

MIT
