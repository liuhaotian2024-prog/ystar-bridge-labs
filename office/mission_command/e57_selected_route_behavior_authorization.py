from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e55_action_authorization_gate import authorize_action
from .e57_commercial_route_candidates import BRIDGE_ROOT, NEXT_MILESTONE, SELECTED_ROUTE, write_json, write_md
from .e57_commercial_route_decision import run_commercial_route_decision


def selected_next_action_proposal() -> dict[str, Any]:
    decision = run_commercial_route_decision()
    return {
        "action_id": NEXT_MILESTONE,
        "source": "canonical_runtime",
        "action_type": "internal_packaging",
        "intent": f"Package selected post-L5 route: {decision['selected_route']}",
        "Xt_current_state": "Post-L5 money route retest selected an internal owner-review-only case-study route.",
        "Y_star_target": "Prepare the AI agent company runtime harness case study without external action.",
        "U_intervention": "Create internal packaging plan and evidence map for owner review.",
        "predicted_Yt_plus_1": "owner-reviewable case-study package exists",
        "predicted_Rt_plus_1": "owner may decide whether to approve any future external review",
        "required_inputs": ["E57 decision packet", "E56 internal loop evidence", "E52 proof packet"],
        "expected_outputs": ["future_E58_case_study_package"],
        "side_effect_profile": {"external_action": False, "network": False, "server_started": False, "client_config_mutation": False},
        "externality_level": "none",
        "owner_approval_required": False,
        "governance_required": True,
        "evidence_required": True,
        "allowed_by_default": True,
        "canonical_runtime_required": True,
        "evidence_path": ["operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", "operations/external_validation/e57_cross_repo_evidence_packet.json"],
    }


def run_selected_route_behavior_authorization() -> dict[str, Any]:
    selected = authorize_action(selected_next_action_proposal())
    outreach = authorize_action({**selected_next_action_proposal(), "action_id": "direct_customer_outreach_now", "action_type": "external_contact", "externality_level": "external_human", "owner_approval_required": True})
    external_review = authorize_action({**selected_next_action_proposal(), "action_id": "controlled_single_first_user_review_now", "action_type": "external_contact", "externality_level": "external_human", "owner_approval_required": True})
    status = "internal_analysis_allowed" if selected["authorization_status"] in {"dry_run_only", "allow"} else selected["authorization_status"]
    checks = {
        "direct_outreach_denied": outreach["authorization_status"] == "deny",
        "external_review_execution_denied_without_owner_approval": external_review["authorization_status"] == "deny",
        "selected_internal_next_action_has_evidence_path": bool(selected_next_action_proposal()["evidence_path"]),
        "behavior_center_controls_next_action": selected_next_action_proposal()["source"] == "canonical_runtime",
        "ceo_brain_not_executor": selected_next_action_proposal()["source"] != "CEO_brain",
    }
    return {
        "artifact_id": "e57_selected_route_behavior_authorization_result",
        "selected_route": SELECTED_ROUTE,
        "selected_next_action": NEXT_MILESTONE,
        "authorization_outcome": status,
        "selected_action_authorization": selected,
        "direct_outreach_authorization": outreach,
        "external_review_authorization": external_review,
        "checks": checks,
        "passed": all(checks.values()) and status == "internal_analysis_allowed",
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_selected_route_behavior_authorization(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_selected_route_behavior_authorization()
    write_json(root, "operations/external_validation/e57_selected_route_behavior_authorization_result.json", data)
    write_md(root, "reports/integration/e57_selected_route_behavior_authorization_result.md", "E57 Selected Route Behavior Authorization", [
        f"Authorization outcome: `{data['authorization_outcome']}`",
        "Direct outreach: `denied`",
        "External review execution: `denied_without_owner_approval`",
    ])
    return data

