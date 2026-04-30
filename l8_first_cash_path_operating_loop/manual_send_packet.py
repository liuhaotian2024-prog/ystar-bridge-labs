#!/usr/bin/env python3
"""Manual-send commercial action packets and owner execution receipts."""

from __future__ import annotations

from typing import Any

from .commercial_action_queue import get_action, save_action
from .first_cash_path_model import base_packet, get_packet, load_packets, now_id, now_iso, write_packet


def disabled_tool_send_email_future_slot() -> dict[str, Any]:
    return {
        "slot_name": "disabled_tool_send_email_future_slot",
        "enabled": False,
        "can_execute": False,
        "reason": "Automatic email sending is not implemented or allowed in L8.0.",
    }


def create_manual_send_packet(action: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    packet_id = f"manual_send_{action['action_id']}_{now_id()}"
    body = action["draft_content"]
    packet = {
        **base_packet("manual_send_packet"),
        "packet_id": packet_id,
        "action_id": action["action_id"],
        "approved_decision_id": decision["decision_id"],
        "recipient_placeholder": "[OWNER_SELECTS_RECIPIENT_MANUALLY]",
        "channel": "owner_manual_email_or_dm_outside_system",
        "subject_or_opening": action["title"],
        "body": body,
        "send_instructions": [
            "Owner reviews recipient, channel, claims, price language, and risk boundary.",
            "Owner sends manually outside this system only if still approved.",
            "Return to the Office UI and mark the packet status after manual action.",
        ],
        "owner_checklist": [
            "Recipient manually selected and appropriate.",
            "No unsupported claims.",
            "No payment link or checkout included unless separately approved.",
            "No customer commitment beyond a conversation or pilot review.",
        ],
        "status": "ready_for_owner_manual_send",
        "tool_send_email_slot": disabled_tool_send_email_future_slot(),
    }
    return write_packet("manual_send_packets", packet_id, packet)


def list_manual_send_packets() -> list[dict[str, Any]]:
    return load_packets("manual_send_packets")


def get_manual_send_packet(packet_id: str) -> dict[str, Any]:
    packet = get_packet("manual_send_packets", packet_id)
    if not packet:
        raise ValueError(f"Unknown manual-send packet: {packet_id}")
    return packet


def mark_manual_send_packet(packet_id: str, owner_marked_status: str, owner_note: str = "") -> dict[str, Any]:
    allowed = {"marked_sent_by_owner", "not_sent", "revised_outside_system", "customer_replied", "no_response", "interested", "not_interested", "paid_signal", "pilot_accepted"}
    if owner_marked_status not in allowed:
        raise ValueError(f"Unsupported manual-send status: {owner_marked_status}")
    packet = get_manual_send_packet(packet_id)
    packet["status"] = owner_marked_status
    packet["updated_at"] = now_iso()
    write_packet("manual_send_packets", packet_id, packet)
    receipt_id = f"manual_receipt_{packet_id}_{now_id()}"
    receipt = {
        **base_packet("manual_action_receipt"),
        "receipt_id": receipt_id,
        "manual_send_packet_id": packet_id,
        "action_id": packet["action_id"],
        "owner_marked_status": owner_marked_status,
        "owner_note": owner_note,
        "timestamp": now_iso(),
        "automatic_send_executed": False,
    }
    action = get_action(packet["action_id"])
    action["status"] = f"manual_packet_{owner_marked_status}"
    save_action(action)
    return write_packet("manual_action_receipts", receipt_id, receipt)


def list_manual_action_receipts() -> list[dict[str, Any]]:
    return load_packets("manual_action_receipts")

