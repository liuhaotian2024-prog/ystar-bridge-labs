#!/usr/bin/env python3
"""Decompose delegated missions into legacy-agent workstreams."""

from __future__ import annotations

from typing import Any

from .mission_model import LEGACY_AGENT_IDS, base_packet, now_iso, write_packet


TASK_TEMPLATES = [
    ("aiden_ceo", "mission_commander", "Interpret owner goal and coordinate delegated mission"),
    ("jinjin_k9_scout", "research_lead", "Build read-only research and evidence plan"),
    ("sofia_cmo", "market_pain", "Analyze customer pain and positioning"),
    ("marco_cfo", "cash_path", "Analyze pricing, revenue logic, and cash-path tradeoffs"),
    ("zara_cso", "strategy_risk", "Analyze strategic fit, defensibility, and risk boundary"),
    ("ethan_cto", "technical_feasibility", "Analyze deliverability and runtime/tool implications"),
    ("samantha_secretary", "archive_decision_log", "Archive packets and prepare decision log"),
    ("leo_engineer", "tooling_support", "Check tooling feasibility and workflow support"),
]


def decompose_mission(mission: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = []
    for agent_id, function, title in TASK_TEMPLATES:
        if agent_id not in LEGACY_AGENT_IDS:
            raise ValueError(f"non-legacy agent assigned: {agent_id}")
        task_id = f"task_{mission['mission_id']}_{function}"
        task = {
            **base_packet("mission_team_task"),
            "task_id": task_id,
            "mission_id": mission["mission_id"],
            "assigned_agent": agent_id,
            "function": function,
            "task_title": title,
            "task_description": f"{title} for: {mission['owner_goal']}",
            "permission_tier_required": "tier_0" if function != "research_lead" else mission["allowed_permission_tier"],
            "status": "assigned",
            "output_refs": [],
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        tasks.append(write_packet("mission_team_tasks", task_id, task))
    return tasks

