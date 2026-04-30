#!/usr/bin/env python3
"""Build approval escalation packets for L10 missions."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, now_iso, write_packet


def build_escalation_packets(mission_id: str) -> list[dict[str, Any]]:
    packets = [
        _packet(
            mission_id,
            "approve_manual_customer_discovery_message",
            "customer_contact",
            "Owner-approved manual discovery message to founder/operator archetype.",
            "Could produce first real commercial signal without locking into one offer.",
            "No automatic send; owner manually reviews and sends if approved.",
        ),
        _packet(
            mission_id,
            "approve_public_positioning_draft",
            "publication",
            "Owner-reviewed public positioning draft for the Labs meta-development story.",
            "Could clarify trust/proof narrative before outreach.",
            "Draft only; no publication in L10.",
        ),
    ]
    return [write_packet("escalation_packets", packet["escalation_id"], packet) for packet in packets]


def list_escalation_packets() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("escalation_packets")


def _packet(mission_id: str, action: str, action_class: str, content: str, value: str, boundary: str) -> dict[str, Any]:
    return {
        **base_packet("escalation_packet"),
        "escalation_id": f"escalation_{mission_id}_{action}",
        "mission_id": mission_id,
        "requested_action": action,
        "action_class": action_class,
        "permission_tier_required": "tier_2",
        "reason": "Mission strategy generated an action that requires explicit owner approval before any external side effect.",
        "expected_business_value": value,
        "risk_summary": "External contact/publication could create reputation, commitment, or compliance risk if executed without review.",
        "exact_proposed_content": content,
        "execution_boundary": boundary,
        "approval_options": ["approve", "reject", "request_revision", "hold"],
        "status": "waiting_for_owner_review",
        "created_at": now_iso(),
    }

