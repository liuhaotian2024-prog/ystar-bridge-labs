#!/usr/bin/env python3
"""Meta-development strategy brief generation for L10 missions."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, now_iso, write_packet
from .opportunity_signal_extractor import list_opportunity_signals


def build_meta_strategy_brief(mission_id: str) -> dict[str, Any]:
    signals = [item for item in list_opportunity_signals() if item["mission_id"] == mission_id]
    top = [item["possible_offer"] for item in signals] or ["Founder AI workflow audit", "AI company cockpit setup", "Coding-agent governance audit"]
    packet = {
        **base_packet("meta_strategy_brief"),
        "brief_id": f"meta_strategy_brief_{mission_id}",
        "mission_id": mission_id,
        "executive_summary": "The team should keep L8 first-cash as a seed while testing adjacent service/setup paths that reuse the Office, scheduler, and approval loop.",
        "top_opportunities": top[:5],
        "shortest_cash_recommendation": "Founder AI workflow audit / CEO command brief remains the fastest paid-signal service path.",
        "strategic_recommendation": "AI company cockpit setup and governance-template support are stronger compounding paths after proof.",
        "low_effort_recommendation": "Use manual-send-only owner-approved diagnostic outreach packets and fixture-backed proof examples.",
        "fastest_feedback_recommendation": "Run owner-approved customer discovery on one founder/operator archetype before building more tooling.",
        "7_day_plan": [
            "Refresh top three opportunity packets.",
            "Prepare one owner-approved manual discovery packet.",
            "Create one sample deliverable/proof packet.",
        ],
        "30_day_plan": [
            "Run 3-5 owner-approved/manual discovery conversations or equivalent strong-signal checks.",
            "Convert feedback into L9 residuals and review-gated learning candidates.",
            "Pick one repeatable service package and one compounding productized path.",
        ],
        "risks": ["No live customer proof yet", "Owner approval still required for external action", "Fixture evidence is not market proof"],
        "required_owner_decisions": ["Select which escalation packet to approve/revise/hold", "Approve any external customer contact"],
        "evidence_index": [ref for signal in signals for ref in signal["evidence_refs"]],
        "created_at": now_iso(),
    }
    return write_packet("meta_strategy_briefs", packet["brief_id"], packet)


def list_meta_strategy_briefs() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("meta_strategy_briefs")

