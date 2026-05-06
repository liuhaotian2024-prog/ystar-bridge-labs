from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e55_behavior_queue import enqueue_action_proposal, validate_queue_item
from .e56_counterfactual_internal_action_selector import run_counterfactual_internal_action_selection
from .e56_internal_company_loop_model import BRIDGE_ROOT, SELECTED_ACTION, write_json


def selected_action_proposal() -> dict[str, Any]:
    selection = run_counterfactual_internal_action_selection()
    return {
        "action_id": selection["selected_action"],
        "source": "canonical_runtime",
        "action_type": "internal_validation",
        "intent": "Run the E56 internal operating loop self-test as dry-run only.",
        "Xt_current_state": selection["Xt_current_state"],
        "Y_star_target": selection["Y_star_target"],
        "U_intervention": "enqueue internal loop self-test through behavior center",
        "predicted_Yt_plus_1": "internal company operating loop L5 proof passes",
        "predicted_Rt_plus_1": "E57_post_L5_money_route_retest becomes justified",
        "required_inputs": ["E54 brain L5", "E55 behavior center L5", "E53 pending owner decision"],
        "expected_outputs": ["operations/external_validation/e56_internal_loop_dry_run_result.json"],
        "side_effect_profile": {"external_action": False, "network": False, "server_started": False, "client_config_mutation": False},
        "externality_level": "none",
        "owner_approval_required": False,
        "governance_required": True,
        "evidence_required": True,
        "allowed_by_default": True,
        "canonical_runtime_required": True,
        "evidence_path": ["operations/external_validation/e56_internal_loop_evidence_packet.json"],
    }


def build_internal_loop_behavior_queue() -> dict[str, Any]:
    selected = enqueue_action_proposal(selected_action_proposal())
    external = enqueue_action_proposal({**selected_action_proposal(), "action_id": "execute_external_first_user_review_now", "action_type": "external_contact", "intent": "external review remains blocked", "externality_level": "external_human", "owner_approval_required": True})
    external["queue_status"] = "blocked_pending_owner_decision"
    items = [selected, external]
    validations = {item["action_id"]: validate_queue_item(item) for item in items}
    return {
        "artifact_id": "e56_internal_loop_behavior_queue",
        "queue_status": "valid",
        "selected_action": SELECTED_ACTION,
        "items": items,
        "validations": validations,
        "selected_action_queued": selected["action_id"] == SELECTED_ACTION and validations[SELECTED_ACTION]["valid"],
        "external_first_user_review_denied": external["queue_status"] == "blocked_pending_owner_decision",
        "external_action_allowed": False,
        "owner_decision_status": "pending_owner_decision",
        "no_external_action": True,
    }


def write_internal_loop_behavior_queue(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = build_internal_loop_behavior_queue()
    write_json(root, "operations/external_validation/e56_internal_loop_behavior_queue.json", data)
    return data

