#!/usr/bin/env python3
"""Manual-send-only bridge from L10 escalations to L8-style action loops."""

from __future__ import annotations

from typing import Any

from .escalation_packet_builder import list_escalation_packets
from .mission_model import base_packet, write_packet


def build_l8_action_loop_escalation_packet(mission_id: str) -> dict[str, Any]:
    escalations = [item for item in list_escalation_packets() if item["mission_id"] == mission_id]
    escalation = escalations[0] if escalations else None
    packet_id = f"l8_action_loop_escalation_{mission_id}"
    packet = {
        **base_packet("l8_action_loop_escalation_packet"),
        "packet_id": packet_id,
        "mission_id": mission_id,
        "source_escalation_id": escalation["escalation_id"] if escalation else None,
        "manual_send_only": True,
        "approval_required": True,
        "tool_send_email_enabled": False,
        "commercial_action_payload": {
            "action_type": "l10_escalation_manual_action",
            "draft_content": escalation["exact_proposed_content"] if escalation else "No escalation available.",
            "execution_mode": "manual_send_packet",
            "status": "pending_owner_approval",
        },
    }
    return write_packet("l8_action_loop_escalation_packets", packet_id, packet)


def list_l8_action_loop_escalation_packets() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("l8_action_loop_escalation_packets")

