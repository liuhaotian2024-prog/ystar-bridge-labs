#!/usr/bin/env python3
"""Owner approval center for L8 commercial actions."""

from __future__ import annotations

from typing import Any

from .commercial_action_builder import build_commercial_actions
from .commercial_action_queue import get_action, list_commercial_actions, save_action
from .first_cash_path_model import base_packet, load_packets, now_id, now_iso, write_packet
from .manual_send_packet import create_manual_send_packet


ALLOWED_DECISIONS = {"approve", "reject", "request_revision", "hold"}


def list_pending_approvals() -> list[dict[str, Any]]:
    build_commercial_actions()
    return [action for action in list_commercial_actions() if action.get("status") in {"pending_owner_approval", "revision_requested", "hold"}]


def decide_action(action_id: str, decision: str, decision_note: str = "", decided_by: str = "owner") -> dict[str, Any]:
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"Unsupported approval decision: {decision}")
    action = get_action(action_id)
    decision_id = f"approval_decision_{action_id}_{now_id()}"
    record = {
        **base_packet("owner_approval_decision"),
        "decision_id": decision_id,
        "action_id": action_id,
        "decision": decision,
        "decided_by": decided_by,
        "decision_note": decision_note,
        "created_at": now_iso(),
    }
    write_packet("owner_approval_decisions", decision_id, record)
    manual_packet = None
    if decision == "approve":
        action["status"] = "approved_manual_send_packet_ready"
        manual_packet = create_manual_send_packet(action, record)
    elif decision == "reject":
        action["status"] = "rejected"
    elif decision == "request_revision":
        action["status"] = "revision_requested"
    elif decision == "hold":
        action["status"] = "hold"
    save_action(action)
    return {"ok": True, "decision": record, "action": action, "manual_send_packet": manual_packet}


def list_approval_decisions() -> list[dict[str, Any]]:
    return load_packets("owner_approval_decisions")

