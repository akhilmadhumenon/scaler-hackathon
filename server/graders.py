"""
Grading logic for all four stock-investment tasks.

Each grader receives the task config and the action the agent submitted,
then returns an immediate step reward in [0.0, 1.0] (before normalisation).

Features:
- Per-step grading with partial credit
- Conviction-ordering bonus (rewards deciding priority/tail-risk names early)
- Anti-exploit thesis validation (keyword stuffing detection)
- Hedge flag grading on the expert task
"""

from __future__ import annotations

from typing import Any


# ─── Anti-exploit helpers ────────────────────────────────────────────────────

def _detect_keyword_stuffing(text: str, keywords: list[str]) -> bool:
    """
    Detect if a thesis is likely keyword-stuffed (gaming the grader).

    Heuristics:
    - If text is shorter than 15 words but contains 5+ keywords → suspicious
    - If the ratio of keywords to total words is > 0.6 → suspicious
    - If the same word is repeated 4+ times → suspicious
    """
    if not text:
        return False

    words = text.lower().split()
    if len(words) < 3:
        return True

    matched = sum(1 for kw in keywords if kw.lower() in text.lower())
    keyword_ratio = matched / max(len(words), 1)
    if len(words) < 15 and matched >= 5:
        return True
    if keyword_ratio > 0.6:
        return True

    from collections import Counter
    word_counts = Counter(words)
    if any(c >= 4 for c in word_counts.values()):
        return True

    return False


def _score_thesis(
    thesis: str | None,
    keyword_cfg: dict[str, Any],
) -> float:
    """
    Score a thesis by keyword matching with anti-exploit checks.

    Returns a float in [0.0, 1.0] representing quality.
    Partial credit: matched / required_matches, capped at 1.0.
    """
    if not thesis:
        return 0.0

    if len(thesis.strip()) < 20:
        return 0.05

    keywords: list[str] = keyword_cfg.get("keywords", [])
    required: int = keyword_cfg.get("required_matches", 1)

    if _detect_keyword_stuffing(thesis, keywords):
        return 0.1

    thesis_lower = thesis.lower()
    matched = sum(1 for kw in keywords if kw.lower() in thesis_lower)
    base_score = min(1.0, matched / required) if required > 0 else 0.0

    return base_score


# ─── Ordering bonus ────────────────────────────────────────────────────────────

def _compute_ordering_bonus(
    task_cfg: dict[str, Any],
    instrument_id: str,
    decided: dict[str, Any],
) -> float:
    """
    Bonus for addressing priority (high-impact / tail-risk) names earlier in the episode.
    """
    priority_ids: list[str] = task_cfg.get("priority_ids", [])
    total_bonus: float = task_cfg.get("ordering_bonus", 0.0)

    if instrument_id not in priority_ids or total_bonus <= 0:
        return 0.0

    num_priority = len(priority_ids)
    per_bonus = total_bonus / num_priority if num_priority > 0 else 0.0

    position = len(decided) + 1
    total_n = len(task_cfg.get("instruments", []))
    halfway = total_n / 2

    if position <= halfway:
        return round(per_bonus, 6)
    decay = 1.0 - ((position - halfway) / halfway)
    return round(per_bonus * max(0.0, decay), 6)


# ─── Task 1: basic_screen ─────────────────────────────────────────────────────

def grade_basic_screen(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct: str = gt.get("decision", "")

    if decision == correct:
        return task_cfg["decision_reward"], f"Correct stance '{decision}' for {instrument_id}"
    return 0.001, f"Wrong stance '{decision}' (expected '{correct}') for {instrument_id}"


# ─── Task 2: sector_rotation ──────────────────────────────────────────────────

def grade_sector_rotation(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()
    risk_tier: str = (action.get("risk_tier") or "").lower().strip()
    thesis: str | None = action.get("thesis") or None

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct_decision: str = gt.get("decision", "")
    correct_risk: str = gt.get("risk_tier", "")

    reward = 0.0
    parts: list[str] = []

    if decision == correct_decision:
        reward += task_cfg["decision_reward"]
        parts.append(f"decision=✓({decision})")
    else:
        parts.append(f"decision=✗({decision}≠{correct_decision})")

    if risk_tier == correct_risk:
        reward += task_cfg["risk_tier_reward"]
        parts.append(f"risk_tier=✓({risk_tier})")
    else:
        parts.append(f"risk_tier=✗({risk_tier}≠{correct_risk})")

    if instrument_id in task_cfg["thesis_required_for"]:
        kw_cfg = task_cfg["thesis_keywords"].get(instrument_id, {})
        quality = _score_thesis(thesis, kw_cfg)
        tr = round(task_cfg["thesis_reward"] * quality, 6)
        reward += tr
        parts.append(f"thesis_quality={quality:.2f}(+{tr:.3f})")

    order_bonus = _compute_ordering_bonus(task_cfg, instrument_id, decided)
    if order_bonus > 0:
        reward += order_bonus
        parts.append(f"ordering_bonus=+{order_bonus:.4f}")

    return round(reward, 6), " | ".join(parts)


# ─── Task 3: risk_budget ─────────────────────────────────────────────────────

def grade_risk_budget(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()
    risk_tier: str = (action.get("risk_tier") or "").lower().strip()
    thesis: str | None = action.get("thesis") or None

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct_decision: str = gt.get("decision", "")
    correct_risk: str = gt.get("risk_tier", "")

    reward = 0.0
    parts: list[str] = []

    if decision == correct_decision:
        reward += task_cfg["decision_reward"]
        parts.append(f"decision=✓({decision})")
    else:
        parts.append(f"decision=✗({decision}≠{correct_decision})")

    if risk_tier == correct_risk:
        reward += task_cfg["risk_tier_reward"]
        parts.append(f"risk_tier=✓({risk_tier})")
    else:
        parts.append(f"risk_tier=✗({risk_tier}≠{correct_risk})")

    if instrument_id in task_cfg["thesis_required_for"]:
        kw_cfg = task_cfg["thesis_keywords"].get(instrument_id, {})
        quality = _score_thesis(thesis, kw_cfg)
        tr = round(task_cfg["thesis_reward"] * quality, 6)
        reward += tr
        parts.append(f"thesis_quality={quality:.2f}(+{tr:.4f})")

    order_bonus = _compute_ordering_bonus(task_cfg, instrument_id, decided)
    if order_bonus > 0:
        reward += order_bonus
        parts.append(f"ordering_bonus=+{order_bonus:.4f}")

    return round(reward, 6), " | ".join(parts)


# ─── Task 4: macro_stress ────────────────────────────────────────────────────

def grade_macro_stress(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    instrument_id: str = action.get("instrument_id", "")
    decision: str = (action.get("decision") or "").lower().strip()
    risk_tier: str = (action.get("risk_tier") or "").lower().strip()
    thesis: str | None = action.get("thesis") or None

    raw_hedge = action.get("hedge_recommended")
    if isinstance(raw_hedge, bool):
        hedge = raw_hedge
    elif isinstance(raw_hedge, str):
        hedge = raw_hedge.lower().strip() == "true"
    else:
        hedge = False

    gt: dict[str, Any] = task_cfg["ground_truth"].get(instrument_id, {})
    correct_decision: str = gt.get("decision", "")
    correct_risk: str = gt.get("risk_tier", "")
    correct_hedge: bool = gt.get("hedge_recommended", False)

    reward = 0.0
    parts: list[str] = []

    if decision == correct_decision:
        reward += task_cfg["decision_reward"]
        parts.append(f"decision=✓({decision})")
    else:
        parts.append(f"decision=✗({decision}≠{correct_decision})")

    if risk_tier == correct_risk:
        reward += task_cfg["risk_tier_reward"]
        parts.append(f"risk_tier=✓({risk_tier})")
    else:
        parts.append(f"risk_tier=✗({risk_tier}≠{correct_risk})")

    if hedge == correct_hedge:
        reward += task_cfg.get("hedge_reward", 0.0)
        parts.append(f"hedge=✓({hedge})")
    else:
        parts.append(f"hedge=✗({hedge}≠{correct_hedge})")

    if instrument_id in task_cfg["thesis_required_for"]:
        kw_cfg = task_cfg["thesis_keywords"].get(instrument_id, {})
        quality = _score_thesis(thesis, kw_cfg)
        tr = round(task_cfg["thesis_reward"] * quality, 6)
        reward += tr
        parts.append(f"thesis_quality={quality:.2f}(+{tr:.4f})")

    order_bonus = _compute_ordering_bonus(task_cfg, instrument_id, decided)
    if order_bonus > 0:
        reward += order_bonus
        parts.append(f"ordering_bonus=+{order_bonus:.4f}")

    return round(reward, 6), " | ".join(parts)


# ─── Dispatcher ───────────────────────────────────────────────────────────────

GRADERS = {
    "basic_screen": grade_basic_screen,
    "sector_rotation": grade_sector_rotation,
    "risk_budget": grade_risk_budget,
    "macro_stress": grade_macro_stress,
}


def grade_action(
    task_cfg: dict[str, Any],
    action: dict[str, Any],
    decided: dict[str, Any],
) -> tuple[float, str]:
    """Dispatch to the right grader and return (reward, reason)."""
    task_name: str = task_cfg["name"]
    grader = GRADERS.get(task_name)
    if grader is None:
        return 0.0, f"No grader found for task '{task_name}'"
    return grader(task_cfg, action, decided)
