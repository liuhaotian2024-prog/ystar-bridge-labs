#!/usr/bin/env python3
"""Controlled research executor with fixture and disabled-live modes."""

from __future__ import annotations

from typing import Any

from .controlled_research_planner import build_research_plan
from .evidence_packet_builder import build_fixture_evidence_packets
from .mission_delegation_center import get_mission
from .mission_model import base_packet, now_iso, write_packet


def run_fixture_research_demo(mission_id: str | None = None) -> dict[str, Any]:
    mission = get_mission(mission_id)
    plan = build_research_plan(mission["mission_id"])
    evidence = build_fixture_evidence_packets(mission["mission_id"])
    receipt = {
        **base_packet("research_budget_receipt"),
        "receipt_id": f"research_receipt_{mission['mission_id']}_fixture_demo",
        "mission_id": mission["mission_id"],
        "budget_id": mission["research_budget_id"],
        "queries_used": min(len(plan["search_queries"]), 5),
        "pages_read": len(evidence),
        "domains_used": 1,
        "external_observation_executed": False,
        "mode": "fixture_demo",
        "stopped_reason": "fixture_demo_complete_no_network",
        "created_at": now_iso(),
    }
    receipt = write_packet("research_budget_receipts", receipt["receipt_id"], receipt)
    return {"ok": True, "mode": "fixture_demo", "research_plan": plan, "evidence_packets": evidence, "budget_receipt": receipt}


def run_configured_live_read_only(mission_id: str | None = None, explicitly_enabled: bool = False) -> dict[str, Any]:
    mission = get_mission(mission_id)
    receipt = {
        **base_packet("research_budget_receipt"),
        "receipt_id": f"research_receipt_{mission['mission_id']}_configured_live_read_only_disabled",
        "mission_id": mission["mission_id"],
        "budget_id": mission["research_budget_id"],
        "queries_used": 0,
        "pages_read": 0,
        "domains_used": 0,
        "external_observation_executed": False,
        "mode": "configured_live_read_only",
        "configured_live_read_only_available": False,
        "stopped_reason": "disabled_unless_explicitly_configured_and_safe",
        "created_at": now_iso(),
    }
    return {"ok": True, "configured_live_read_only_executed": False, "budget_receipt": write_packet("research_budget_receipts", receipt["receipt_id"], receipt)}

