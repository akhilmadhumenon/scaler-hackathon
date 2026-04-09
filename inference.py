#!/usr/bin/env python3
"""
Baseline inference script for the Stock Investment Agent environment.

Uses the OpenAI API client to run a model against all tasks and produce
reproducible baseline scores.

Required environment variables:
    API_BASE_URL  – The API endpoint for the LLM.
    MODEL_NAME    – The model identifier to use for inference.
    HF_TOKEN      – Your Hugging Face / API key.

STDOUT FORMAT (mandatory):
    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

import requests
from openai import OpenAI

# ────────────────────────────────────────────────────────────────────────────────
# Configuration from env vars
# ────────────────────────────────────────────────────────────────────────────────

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or ""

ENV_URL = os.getenv("ENV_URL", "http://localhost:8000")

BENCHMARK = "stock-investment-agent"
TASKS = ["basic_screen", "sector_rotation", "risk_budget", "macro_stress"]

# ────────────────────────────────────────────────────────────────────────────────
# OpenAI client
# ────────────────────────────────────────────────────────────────────────────────

client = OpenAI(
    api_key=HF_TOKEN,
    base_url=API_BASE_URL,
)


# ────────────────────────────────────────────────────────────────────────────────
# Structured stdout logging (mandatory format)
# ────────────────────────────────────────────────────────────────────────────────

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


# ────────────────────────────────────────────────────────────────────────────────
# Environment HTTP helpers
# ────────────────────────────────────────────────────────────────────────────────

def env_reset(task_name: str) -> dict:
    resp = requests.post(
        f"{ENV_URL}/reset",
        json={"task_name": task_name, "seed": None},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_step(action: dict) -> dict:
    resp = requests.post(
        f"{ENV_URL}/step",
        json=action,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def env_state() -> dict:
    resp = requests.get(f"{ENV_URL}/state", timeout=30)
    resp.raise_for_status()
    return resp.json()


# ────────────────────────────────────────────────────────────────────────────────
# LLM helper
# ────────────────────────────────────────────────────────────────────────────────

def ask_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=1024,
    )
    content = response.choices[0].message.content
    return (content or "").strip()


def parse_action(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [ln for ln in lines if not ln.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
        raise


# ────────────────────────────────────────────────────────────────────────────────
# Run a single task
# ────────────────────────────────────────────────────────────────────────────────

def run_task(task_name: str) -> dict:
    """Run one full episode on the given task. Emits [START]/[STEP]/[END] logs."""

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    done = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset_data = env_reset(task_name)
        obs = reset_data["observation"]

        task_desc = obs.get("task_description", "")
        instructions = obs.get("instructions", "")
        instruments = obs.get("instruments", [])
        max_steps = obs.get("max_steps", len(instruments))

        system_prompt = (
            "You are a buy-side research analyst. Output exactly one JSON object per turn — "
            "no markdown fences, no commentary.\n\n"
            f"Task: {task_desc}\n\n"
            f"Instructions:\n{instructions}"
        )

        while not done and steps_taken < max_steps:
            pending = obs.get("pending_ids", [])
            if not pending:
                break

            target_id = pending[0]
            target = next((x for x in instruments if x["id"] == target_id), None)
            if target is None:
                break

            user_prompt = (
                f"Decide the next pending instrument (process in order unless you intentionally "
                f"prioritise risk — still use id {target_id!r} for this step).\n\n"
                f"ID: {target['id']}\n"
                f"Symbol: {target['symbol']}\n"
                f"Company: {target['company']}\n"
                f"Sector: {target['sector']}\n"
                f"Headline: {target['headline']}\n"
                f"Narrative: {target['narrative']}\n"
                f"As of: {target['as_of']}\n\n"
                "Respond with ONLY a JSON object matching this task's schema. "
            )

            if task_name == "basic_screen":
                user_prompt += '{"instrument_id": "<id>", "decision": "<overweight|neutral|underweight>"}'
            elif task_name == "sector_rotation":
                user_prompt += (
                    '{"instrument_id": "<id>", "decision": "<overweight|neutral|underweight>", '
                    '"risk_tier": "<defensive|balanced|aggressive>", '
                    '"thesis": "<text or null>"}'
                )
            elif task_name == "risk_budget":
                user_prompt += (
                    '{"instrument_id": "<id>", "decision": "<overweight|neutral|underweight>", '
                    '"risk_tier": "<defensive|balanced|aggressive>", '
                    '"thesis": "<text or null>"}'
                )
            elif task_name == "macro_stress":
                user_prompt += (
                    '{"instrument_id": "<id>", "decision": "<overweight|neutral|underweight>", '
                    '"risk_tier": "<defensive|balanced|aggressive>", '
                    '"hedge_recommended": <true|false>, '
                    '"thesis": "<text or null>"}'
                )

            error_msg: Optional[str] = None
            try:
                raw_response = ask_llm(system_prompt, user_prompt)
                action = parse_action(raw_response)
                action["instrument_id"] = target_id
            except Exception as e:
                error_msg = str(e)
                action = {"instrument_id": target_id, "decision": "neutral"}
                if task_name in ("sector_rotation", "risk_budget", "macro_stress"):
                    action["risk_tier"] = "balanced"
                if task_name == "macro_stress":
                    action["hedge_recommended"] = False

            step_result = env_step(action)
            obs = step_result["observation"]
            reward = step_result.get("reward", 0.0)
            done = step_result.get("done", False)
            info = step_result.get("info", {})

            env_err = info.get("error") or info.get("warning")
            if env_err:
                error_msg = env_err if error_msg is None else f"{error_msg}; {env_err}"

            steps_taken += 1
            rewards.append(reward)

            action_str = (
                f"decide({target_id},{action.get('decision','?')},"
                f"risk={action.get('risk_tier','-')},hedge={action.get('hedge_recommended','-')})"
            )
            log_step(
                step=steps_taken,
                action=action_str,
                reward=reward,
                done=done,
                error=error_msg,
            )

        final_state = env_state()
        score = final_state.get("cumulative_reward", sum(rewards))

        if score <= 0.0:
            score = 0.01
        elif score >= 1.0:
            score = 0.99

        success = score > 0.1

    except Exception:
        traceback.print_exc()
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return {
        "task_name": task_name,
        "steps": steps_taken,
        "score": round(score, 4),
        "done": done,
        "rewards": rewards,
    }


# ────────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────────

def main() -> int:
    for task_name in TASKS:
        try:
            run_task(task_name)
        except Exception as e:
            print(f"[DEBUG] ERROR running task '{task_name}': {e}", flush=True)
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    sys.exit(main())
