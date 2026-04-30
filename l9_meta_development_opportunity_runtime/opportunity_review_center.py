#!/usr/bin/env python3
"""Owner review center for L9 opportunity portfolio decisions."""

from __future__ import annotations

from typing import Any

from .money_path_model import get_money_path, save_money_path
from .opportunity_model import base_packet, get_packet, load_packets, now_iso, write_packet
from .opportunity_portfolio import get_opportunity, save_opportunity

ALLOWED_DECISIONS = {
    "select_for_execution",
    "reject",
    "hold",
    "request_revision",
    "request_more_evidence",
}

STATUS_BY_DECISION = {
    "select_for_execution": "selected_for_execution",
    "reject": "rejected",
    "hold": "held",
    "request_revision": "revision_needed",
    "request_more_evidence": "evidence_needed",
}


def decide_opportunity(
    decision_packet_id: str,
    decision: str,
    decision_note: str = "",
    decided_by: str = "owner",
) -> dict[str, Any]:
    """Record an owner review decision and update local portfolio state.

    This function only writes local L9 packets. It does not generate execution
    plans for rejected/held/revision/evidence decisions and never triggers
    external observation, outreach, or L8 execution by itself.
    """
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"unsupported L9 opportunity decision: {decision}")
    packet = get_packet("owner_decision_packets", decision_packet_id)
    if not packet:
        raise ValueError(f"unknown decision packet: {decision_packet_id}")

    opportunity = get_opportunity(packet["opportunity_id"])
    money_path = get_money_path(packet["money_path_id"])
    status = STATUS_BY_DECISION[decision]
    opportunity["current_status"] = status
    opportunity["updated_at"] = now_iso()
    money_path["status"] = status
    money_path["updated_at"] = now_iso()
    save_opportunity(opportunity)
    save_money_path(money_path)

    review_id = f"review_{decision}_{packet['money_path_id']}"
    review = {
        **base_packet("opportunity_review_decision"),
        "review_decision_id": review_id,
        "decision_packet_id": decision_packet_id,
        "opportunity_id": packet["opportunity_id"],
        "money_path_id": packet["money_path_id"],
        "decision": decision,
        "decided_by": decided_by,
        "decision_note": decision_note,
        "created_at": now_iso(),
        "execution_plan_created": False,
        "controlled_observation_planning_only": decision == "request_more_evidence",
        "uncontrolled_external_search_run": False,
        "external_side_effects": False,
    }
    return {
        "ok": True,
        "review_decision": write_packet("opportunity_review_decisions", review_id, review),
        "opportunity": opportunity,
        "money_path": money_path,
        "next_step": _next_step(decision),
    }


def list_opportunity_review_decisions() -> list[dict[str, Any]]:
    return load_packets("opportunity_review_decisions")


def selected_money_paths() -> list[dict[str, Any]]:
    return [path for path in load_packets("money_path_candidates") if path.get("status") == "selected_for_execution"]


def _next_step(decision: str) -> str:
    if decision == "select_for_execution":
        return "generate_manual_send_only_execution_plan"
    if decision == "request_more_evidence":
        return "create_controlled_read_only_observation_plan_before_any_external_action"
    if decision == "request_revision":
        return "ask_labs_team_to_revise_opportunity_packet"
    if decision == "hold":
        return "keep_in_portfolio_without_execution"
    return "do_not_create_execution_plan"
