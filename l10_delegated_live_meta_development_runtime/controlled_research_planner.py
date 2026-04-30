#!/usr/bin/env python3
"""Build bounded controlled research plans for L10 missions."""

from __future__ import annotations

from typing import Any

from .mission_delegation_center import get_mission
from .mission_model import base_packet, now_iso, write_packet


def build_research_plan(mission_id: str | None = None) -> dict[str, Any]:
    mission = get_mission(mission_id)
    plan_id = f"research_plan_{mission['mission_id']}"
    queries = [
        "AI founder workflow bottleneck service market",
        "AI agent governance audit startup pain points",
        "AI operations audit small team pricing",
        "AI company cockpit setup founder operator needs",
        "coding agent governance consulting opportunity",
    ]
    plan = {
        **base_packet("controlled_research_plan"),
        "research_plan_id": plan_id,
        "mission_id": mission["mission_id"],
        "research_questions": [
            "Which urgent founder/operator pains map to current Labs capabilities?",
            "Which paths have fastest paid-signal potential?",
            "Which strategic paths compound beyond a single offer?",
        ],
        "search_queries": queries,
        "page_read_targets": [],
        "budget_id": mission["research_budget_id"],
        "expected_evidence": ["market pain signals", "pricing references", "competitor/service framing", "tooling gaps"],
        "stop_conditions": ["budget exhausted", "login/contact/submit/payment requested", "uncontrolled crawl attempted"],
        "created_at": now_iso(),
    }
    return write_packet("research_plans", plan_id, plan)


def list_research_plans() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("research_plans")

