#!/usr/bin/env python3
"""Create and manage delegated meta-development missions."""

from __future__ import annotations

from typing import Any

from .mission_model import DEFAULT_MISSION_TITLE, DEFAULT_OWNER_GOAL, FORBIDDEN_ACTION_CLASSES, base_packet, get_packet, load_packets, now_iso, safe_id, write_packet
from .research_budget_model import create_research_budget


def create_default_mission() -> dict[str, Any]:
    return create_mission(
        title=DEFAULT_MISSION_TITLE,
        owner_goal=DEFAULT_OWNER_GOAL,
        mission_type="meta_development_strategy",
        allowed_permission_tier="tier_1",
    )


def create_mission(
    title: str,
    owner_goal: str,
    mission_type: str = "meta_development_strategy",
    allowed_permission_tier: str = "tier_0",
    autonomy_scope: str = "bounded_internal_and_budgeted_read_only",
) -> dict[str, Any]:
    mission_id = f"mission_{safe_id(title.lower())}"
    budget = create_research_budget(mission_id, allow_external_observation=allowed_permission_tier == "tier_1")
    mission = {
        **base_packet("delegated_mission"),
        "mission_id": mission_id,
        "title": title,
        "owner_goal": owner_goal,
        "mission_type": mission_type,
        "allowed_permission_tier": allowed_permission_tier,
        "autonomy_scope": autonomy_scope,
        "expected_deliverables": [
            "internal/external situation summary",
            "updated opportunity signals",
            "top money paths",
            "shortest cash recommendation",
            "strategic recommendation",
            "7-day action plan",
            "30-day action plan",
            "approval escalation packets",
            "next autonomous mission proposal",
        ],
        "research_budget_id": budget["budget_id"],
        "forbidden_action_classes": FORBIDDEN_ACTION_CLASSES,
        "required_review_points": ["external side-effect request", "Tier 3/Tier 4 action", "core writeback proposal"],
        "status": "created",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    return write_packet("missions", mission_id, mission)


def list_missions() -> list[dict[str, Any]]:
    return load_packets("missions")


def get_mission(mission_id: str | None = None) -> dict[str, Any]:
    if mission_id:
        packet = get_packet("missions", mission_id)
        if not packet:
            raise ValueError(f"unknown mission: {mission_id}")
        return packet
    missions = list_missions()
    if not missions:
        return create_default_mission()
    return missions[-1]


def update_mission_status(mission_id: str, status: str) -> dict[str, Any]:
    mission = get_mission(mission_id)
    mission["status"] = status
    mission["updated_at"] = now_iso()
    return write_packet("missions", mission_id, mission)

