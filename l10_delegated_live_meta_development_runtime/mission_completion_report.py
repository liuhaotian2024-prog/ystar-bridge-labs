#!/usr/bin/env python3
"""Completion reports for L10 delegated missions."""

from __future__ import annotations

from typing import Any

from .action_plan_builder import list_action_plans
from .escalation_packet_builder import list_escalation_packets
from .evidence_packet_builder import list_evidence_packets
from .mission_model import base_packet, now_iso, write_packet


def build_mission_completion_report(mission_id: str) -> dict[str, Any]:
    evidence = [item for item in list_evidence_packets() if item["mission_id"] == mission_id]
    escalations = [item for item in list_escalation_packets() if item["mission_id"] == mission_id]
    plans = [item for item in list_action_plans() if item["mission_id"] == mission_id]
    packet = {
        **base_packet("mission_completion_report"),
        "report_id": f"mission_completion_{mission_id}",
        "mission_id": mission_id,
        "mission_status": "completed_local_demo_or_bounded_run",
        "deliverables": ["mission plan", "research plan", "evidence packets", "source summary", "strategy brief", "action plan", "escalation packets"],
        "evidence_index": [item["evidence_id"] for item in evidence],
        "decisions_needed": [item["requested_action"] for item in escalations],
        "escalations": [item["escalation_id"] for item in escalations],
        "next_recommended_mission": "Run owner-approved validation or refresh live read-only research if configured.",
        "action_plan_refs": [item["action_plan_id"] for item in plans],
        "created_at": now_iso(),
    }
    return write_packet("mission_completion_reports", packet["report_id"], packet)


def list_mission_completion_reports() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("mission_completion_reports")

