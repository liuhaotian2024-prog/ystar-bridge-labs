#!/usr/bin/env python3
"""Bridge selected L9 opportunities into the L8-style action loop shape."""

from __future__ import annotations

from typing import Any

from .execution_plan_generator import list_execution_plans
from .opportunity_model import base_packet, load_packets, now_iso, write_packet


def build_l8_bridge_packet(execution_plan_id: str | None = None) -> dict[str, Any]:
    plan = _execution_plan(execution_plan_id)
    bridge_id = f"l8_bridge_{plan['execution_plan_id']}"
    action_payload = {
        "action_id": f"l9_action_{plan['money_path_id']}",
        "cash_path_id": f"l9_{plan['money_path_id']}",
        "action_type": "l9_selected_opportunity_manual_action",
        "title": plan["selected_offer"],
        "target_profile": plan["target_customer_profile"],
        "draft_content": _draft_content(plan),
        "risk_boundary": "Manual-send only; owner approval required before any external action.",
        "approval_required": True,
        "execution_mode": "manual_send_packet",
        "status": "pending_owner_approval",
    }
    packet = {
        **base_packet("l8_bridge_packet"),
        "bridge_packet_id": bridge_id,
        "execution_plan_id": plan["execution_plan_id"],
        "opportunity_id": plan["opportunity_id"],
        "money_path_id": plan["money_path_id"],
        "l8_action_queue_ready": True,
        "commercial_action_payload": action_payload,
        "approval_required": True,
        "manual_send_only": True,
        "tool_send_email_enabled": False,
        "status": "ready_for_l8_style_owner_approval",
        "created_at": now_iso(),
    }
    return write_packet("l8_bridge_packets", bridge_id, packet)


def list_l8_bridge_packets() -> list[dict[str, Any]]:
    return load_packets("l8_bridge_packets")


def _execution_plan(execution_plan_id: str | None) -> dict[str, Any]:
    plans = list_execution_plans()
    if execution_plan_id:
        for plan in plans:
            if plan.get("execution_plan_id") == execution_plan_id:
                return plan
        raise ValueError(f"unknown L9 execution plan: {execution_plan_id}")
    if not plans:
        raise ValueError("no L9 execution plan is available for L8 bridge")
    return plans[-1]


def _draft_content(plan: dict[str, Any]) -> str:
    return (
        f"Review-only commercial action for {plan['target_customer_profile']}: "
        f"{plan['selected_offer']} First action: {plan['first_action']} "
        "This packet is not sent by the system."
    )
