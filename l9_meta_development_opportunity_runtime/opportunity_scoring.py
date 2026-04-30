#!/usr/bin/env python3
"""Multi-lens opportunity scoring for L9."""

from __future__ import annotations

from typing import Any

from .opportunity_model import base_packet


LENS_WEIGHTS = {
    "shortest_cash": {"shortest_cash_score": 4, "capability_fit_score": 2, "implementation_ease_score": 2, "risk_penalty": -2},
    "strategic_long_term": {"strategic_value_score": 4, "productization_score": 2, "owner_leverage_score": 2, "risk_penalty": -1},
    "low_effort": {"implementation_ease_score": 4, "owner_leverage_score": 2, "capability_fit_score": 2, "risk_penalty": -2},
    "fastest_feedback": {"feedback_speed_score": 4, "shortest_cash_score": 2, "demo_value_score": 2, "risk_penalty": -1},
    "productizable": {"productization_score": 4, "strategic_value_score": 2, "capability_fit_score": 1, "risk_penalty": -1},
    "demo_value": {"demo_value_score": 4, "feedback_speed_score": 2, "owner_leverage_score": 1, "risk_penalty": -1},
    "owner_leverage": {"owner_leverage_score": 4, "implementation_ease_score": 2, "strategic_value_score": 1, "risk_penalty": -1},
    "balanced": {
        "shortest_cash_score": 2,
        "strategic_value_score": 2,
        "capability_fit_score": 2,
        "implementation_ease_score": 1,
        "feedback_speed_score": 1,
        "productization_score": 1,
        "owner_leverage_score": 1,
        "risk_penalty": -2,
    },
}


def score_money_path(path: dict[str, Any], lens: str) -> dict[str, Any]:
    signal_days = int(path.get("time_to_first_signal_days", 30))
    cash_days = int(path.get("time_to_first_cash_days", 60))
    difficulty = int(path.get("execution_difficulty", 3))
    owner_load = int(path.get("owner_load", 3))
    risk = int(path.get("risk_level", 3))
    scores = {
        "shortest_cash_score": _score_low(cash_days, [14, 30, 45, 60]),
        "strategic_value_score": int(path.get("strategic_value", 3)),
        "capability_fit_score": int(path.get("current_capability_fit", 3)),
        "implementation_ease_score": max(1, 6 - difficulty),
        "feedback_speed_score": _score_low(signal_days, [7, 14, 21, 30]),
        "productization_score": int(path.get("productization_potential", 3)),
        "demo_value_score": 5 if any(word in path["path_title"].lower() for word in ["cockpit", "audit", "runtime"]) else 3,
        "owner_leverage_score": max(1, 6 - owner_load),
        "risk_penalty": max(0, risk - 2),
    }
    weights = LENS_WEIGHTS[lens]
    total = 0
    for key, weight in weights.items():
        if key == "risk_penalty":
            total += weight * scores[key]
        else:
            total += weight * scores[key]
    score_id = f"score_{lens}_{path['money_path_id']}"
    return {
        **base_packet("opportunity_score"),
        "score_id": score_id,
        "opportunity_id": path["opportunity_id"],
        "money_path_id": path["money_path_id"],
        **scores,
        "total_score": total,
        "ranking_lens": lens,
        "explanation": (
            f"{lens} score weighs cash speed, capability fit, owner load, productization, and risk penalties. "
            f"Risk penalty={scores['risk_penalty']} for difficulty/unclear delivery/credibility exposure."
        ),
    }


def _score_low(value: int, thresholds: list[int]) -> int:
    if value <= thresholds[0]:
        return 5
    if value <= thresholds[1]:
        return 4
    if value <= thresholds[2]:
        return 3
    if value <= thresholds[3]:
        return 2
    return 1

