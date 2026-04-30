#!/usr/bin/env python3
"""Mission plan builder for delegated meta-development work."""

from __future__ import annotations

from typing import Any

from .mission_delegation_center import get_mission, update_mission_status
from .mission_model import base_packet, now_iso, write_packet
from .team_task_decomposer import decompose_mission


def build_mission_plan(mission_id: str | None = None) -> dict[str, Any]:
    mission = get_mission(mission_id)
    tasks = decompose_mission(mission)
    plan_id = f"mission_plan_{mission['mission_id']}"
    plan = {
        **base_packet("mission_plan"),
        "mission_plan_id": plan_id,
        "mission_id": mission["mission_id"],
        "decomposition_summary": "Aiden coordinates; Jinjin plans evidence; Sofia/Marco/Zara/Ethan analyze market, cash, strategy, and feasibility; Samantha archives.",
        "assigned_agents": [task["assigned_agent"] for task in tasks],
        "workstreams": [task["function"] for task in tasks],
        "expected_outputs": mission["expected_deliverables"],
        "review_points": mission["required_review_points"],
        "risk_boundary": "Tier 0/1 work may proceed within budget; side effects and core writeback escalate.",
        "created_at": now_iso(),
    }
    update_mission_status(mission["mission_id"], "planned")
    return write_packet("mission_plans", plan_id, plan)


def list_mission_plans() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("mission_plans")

