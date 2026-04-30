#!/usr/bin/env python3
"""Commercial action queue storage for L8."""

from __future__ import annotations

from typing import Any

from .first_cash_path_model import get_packet, load_packets, now_iso, write_packet


def list_commercial_actions(status: str | None = None) -> list[dict[str, Any]]:
    actions = load_packets("commercial_action_queue")
    if status:
        return [action for action in actions if action.get("status") == status]
    return actions


def get_action(action_id: str) -> dict[str, Any]:
    action = get_packet("commercial_action_queue", action_id)
    if not action:
        raise ValueError(f"Unknown commercial action: {action_id}")
    return action


def save_action(action: dict[str, Any]) -> dict[str, Any]:
    action["updated_at"] = now_iso()
    return write_packet("commercial_action_queue", action["action_id"], action)


def pending_actions() -> list[dict[str, Any]]:
    return [
        action
        for action in list_commercial_actions()
        if action.get("status") in {"pending_owner_approval", "revision_requested", "hold"}
    ]

