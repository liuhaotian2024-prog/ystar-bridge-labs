#!/usr/bin/env python3
"""Build 7-day/30-day action plans from L10 strategy briefs."""

from __future__ import annotations

from typing import Any

from .meta_strategy_brief_builder import list_meta_strategy_briefs
from .mission_model import base_packet, now_iso, write_packet


def build_action_plan(mission_id: str) -> dict[str, Any]:
    briefs = [item for item in list_meta_strategy_briefs() if item["mission_id"] == mission_id]
    brief = briefs[-1] if briefs else {}
    packet = {
        **base_packet("action_plan"),
        "action_plan_id": f"action_plan_{mission_id}",
        "mission_id": mission_id,
        "selected_recommendations": [
            brief.get("shortest_cash_recommendation", "Founder AI workflow audit first cash path"),
            brief.get("strategic_recommendation", "AI company cockpit setup strategic path"),
        ],
        "next_actions": [
            "Create owner-reviewed discovery packet",
            "Prepare sample proof/deliverable",
            "Ask owner to approve or revise escalation packet",
        ],
        "autonomous_actions": [
            "Refine strategy brief",
            "Summarize fixture/live evidence",
            "Update local opportunity signals",
            "Prepare draft-only materials",
        ],
        "approval_required_actions": [
            "contact customer",
            "send email/message",
            "publish content",
            "submit form",
            "request payment",
            "core writeback",
        ],
        "owner_decisions_needed": ["approve/reject/revise/hold escalation packet"],
        "created_at": now_iso(),
    }
    return write_packet("action_plans", packet["action_plan_id"], packet)


def list_action_plans() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("action_plans")

