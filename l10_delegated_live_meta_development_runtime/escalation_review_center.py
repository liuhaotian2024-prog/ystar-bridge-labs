#!/usr/bin/env python3
"""Owner review decisions for L10 escalation packets."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, get_packet, load_packets, now_iso, write_packet

ALLOWED_DECISIONS = {"approve", "reject", "request_revision", "hold"}


def decide_escalation(escalation_id: str, decision: str, decision_note: str = "", decided_by: str = "owner") -> dict[str, Any]:
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"unsupported escalation decision: {decision}")
    escalation = get_packet("escalation_packets", escalation_id)
    if not escalation:
        raise ValueError(f"unknown escalation: {escalation_id}")
    escalation["status"] = f"{decision}_recorded_no_execution"
    write_packet("escalation_packets", escalation_id, escalation)
    decision_id = f"escalation_decision_{escalation_id}_{decision}"
    packet = {
        **base_packet("escalation_review_decision"),
        "decision_id": decision_id,
        "escalation_id": escalation_id,
        "mission_id": escalation["mission_id"],
        "decision": decision,
        "decided_by": decided_by,
        "decision_note": decision_note,
        "created_at": now_iso(),
        "external_action_executed": False,
    }
    return write_packet("escalation_review_decisions", decision_id, packet)


def list_escalation_review_decisions() -> list[dict[str, Any]]:
    return load_packets("escalation_review_decisions")

