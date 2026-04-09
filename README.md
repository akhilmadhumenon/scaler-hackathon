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

An OpenEnv-compatible reinforcement learning environment that simulates **buy-side portfolio research**: benchmark-relative stances, risk budgeting, cycle theses, and hedge decisions under macro stress. Built for the **Scaler School of Technology × Meta/PyTorch OpenEnv Hackathon**.

## Overview

An agent receives a universe of **instrument scenarios** (equity credit stories, multi-asset notes, structured sleeves, etc.) and must emit structured JSON decisions each step — mirroring how PMs and research analysts triage names under constraints.

### Tasks

| Task | Difficulty | Instruments | Requirements | Max reward (design) |
|------|------------|-------------|--------------|---------------------|
| `basic_screen` | Easy | 5 | `overweight` / `neutral` / `underweight` | 1.0 |
| `sector_rotation` | Medium | 10 | Stance + `risk_tier` + cycle thesis on `sr3` | 1.0 |
| `risk_budget` | Hard | 15 | Stance + `risk_tier` + theses on `rb4`, `rb9`, `rb12` | 1.0 |
| `macro_stress` | Expert | 12 | Stance + `risk_tier` + `hedge_recommended` + thesis on `ms7` | 1.0 |

### Reward system

- **Partial credit:** Per-instrument grading (not only terminal success).
- **Ordering bonus:** Higher credit when **priority / tail-risk** names are decided earlier in the episode.
- **Thesis quality:** Keyword coverage with **anti-keyword-stuffing** penalties.
- **Penalties:** −0.05 for re-deciding an already processed instrument.
- **Expert task:** Boolean **hedge_recommended** scored against deterministic ground truth.

## Quick start

### Run the server

```bash
pip install -e .
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

### Run inference (baseline)

```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your-api-key"
export ENV_URL="http://localhost:8000"
python inference.py
```

### Docker

```bash
docker build -t stock-investment-agent .
docker run -p 8000:8000 stock-investment-agent
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/reset` | Start a new episode |
| POST | `/step` | Execute one instrument decision |
| GET | `/state` | Current episode metadata |
| GET | `/health` | Health check |
| GET | `/info` | Environment metadata |

## Action / observation (summary)

- **Action:** `instrument_id`, `decision` (`overweight` \| `neutral` \| `underweight`), optional `risk_tier`, `hedge_recommended`, `thesis` per task instructions.
- **Observation:** Full `instruments[]`, `pending_ids`, `decided` history, task copy, step counters, `episode_id`.

## Project structure

```
├── openenv.yaml          # OpenEnv manifest
├── pyproject.toml        # Dependencies
├── Dockerfile            # Container image
├── models.py             # Pydantic models (Action, Observation, State)
├── client.py             # Async HTTP client
├── inference.py          # Baseline inference script
├── __init__.py           # Package exports
└── server/
    ├── app.py            # FastAPI server
    ├── environment.py    # Core environment logic
    ├── graders.py        # Grading / reward functions
    └── tasks.py          # Scenarios & task configs
```

## Baseline scores

Run `python inference.py` with your LLM credentials and read the `[END]` lines per task; scores are normalised into **(0, 1)** in `state()` for reporting consistency.

## License

MIT
