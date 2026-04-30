#!/usr/bin/env python3
"""Unified L8 cockpit snapshot for the local Labs Office."""

from __future__ import annotations

from typing import Any

from .commercial_action_builder import build_commercial_actions
from .commercial_action_queue import list_commercial_actions
from .commercial_residual import list_commercial_residuals
from .customer_feedback_intake import list_customer_feedback
from .first_cash_path_loader import initialize_first_cash_path
from .first_cash_path_model import base_packet, load_packets, now_id, now_iso, write_packet
from .learning_candidate_builder import list_learning_candidates
from .manual_send_packet import list_manual_action_receipts, list_manual_send_packets
from .owner_approval_center import list_approval_decisions, list_pending_approvals


def build_cockpit_snapshot(snapshot_id: str | None = None) -> dict[str, Any]:
    path = initialize_first_cash_path()
    build_commercial_actions()
    actions = list_commercial_actions()
    approvals = list_pending_approvals()
    decisions = list_approval_decisions()
    manual_packets = list_manual_send_packets()
    receipts = list_manual_action_receipts()
    feedback = list_customer_feedback()
    residuals = list_commercial_residuals()
    candidates = list_learning_candidates()
    snapshot_id = snapshot_id or f"l8_cockpit_{now_id()}"
    snapshot = {
        **base_packet("l8_cockpit_snapshot"),
        "cockpit_snapshot_id": snapshot_id,
        "selected_first_cash_path": path,
        "current_commercial_stage": _stage(actions, manual_packets, feedback, residuals),
        "scheduler_state_ref": "GET /api/scheduler/status",
        "pending_commercial_actions": [action for action in actions if action.get("status") == "pending_owner_approval"],
        "pending_owner_approvals": approvals,
        "approved_manual_send_packets": manual_packets,
        "manual_action_receipts": receipts,
        "customer_feedback_packets": feedback,
        "commercial_residuals": residuals,
        "learning_candidates": candidates,
        "owner_approval_decisions": decisions,
        "paid_signal_status": _paid_signal_status(feedback),
        "next_recommended_owner_decision": _next_decision(actions, manual_packets, feedback, residuals, candidates),
        "grant_rfp_path_created_by_default": False,
        "tool_send_email_enabled": False,
        "external_side_effects_occurred": False,
        "core_writeback_occurred": False,
        "updated_at": now_iso(),
    }
    return write_packet("cockpit_snapshots", snapshot_id, snapshot)


def current_cockpit() -> dict[str, Any]:
    snapshots = load_packets("cockpit_snapshots")
    if snapshots:
        return snapshots[-1]
    return build_cockpit_snapshot()


def _stage(actions: list[dict[str, Any]], manual_packets: list[dict[str, Any]], feedback: list[dict[str, Any]], residuals: list[dict[str, Any]]) -> str:
    if residuals:
        return "feedback_analyzed_and_learning_candidate_ready"
    if feedback:
        return "customer_feedback_recorded"
    if manual_packets:
        return "manual_send_packet_ready_or_marked"
    if actions:
        return "commercial_actions_pending_owner_approval"
    return "first_cash_path_initialized"


def _paid_signal_status(feedback: list[dict[str, Any]]) -> str:
    if any(item.get("response_status") == "pilot_accepted" for item in feedback):
        return "pilot_accepted"
    if any(item.get("paid_signal") for item in feedback):
        return "paid_signal"
    return "not_yet_observed"


def _next_decision(
    actions: list[dict[str, Any]],
    manual_packets: list[dict[str, Any]],
    feedback: list[dict[str, Any]],
    residuals: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> str:
    if not actions:
        return "Build commercial action queue."
    if any(action.get("status") == "pending_owner_approval" for action in actions):
        return "Approve, reject, request revision, or hold one commercial action."
    if manual_packets and not feedback:
        return "Mark manual-send status and record customer feedback when available."
    if feedback and not residuals:
        return "Generate commercial residual from the latest feedback."
    if residuals and not candidates:
        return "Generate review-gated learning candidate from the residual."
    return "Review learning candidate and choose next owner decision."
