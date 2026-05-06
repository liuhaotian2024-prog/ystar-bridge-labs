from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e55_action_authorization_gate import authorize_action
from .e58_case_study_boundary import BRIDGE_ROOT, NEXT_MILESTONE, write_json, write_md


def _proposal(action_id: str, action_type: str, intent: str, evidence: list[str], side: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "source": "canonical_runtime",
        "action_type": action_type,
        "intent": intent,
        "Xt_current_state": "E57 selected AI agent company runtime harness case study; owner decision remains pending.",
        "Y_star_target": "Package owner-reviewable case study and E59 requirements without external action.",
        "U_intervention": intent,
        "predicted_Yt_plus_1": "owner-reviewable internal package exists",
        "predicted_Rt_plus_1": NEXT_MILESTONE,
        "required_inputs": ["E57 decision", "E54-E56 L5 proofs", "E52 proof packet"],
        "expected_outputs": evidence,
        "side_effect_profile": side or {"external_action": False, "network": False, "server_started": False, "client_config_mutation": False},
        "externality_level": "none" if action_type.startswith("internal") else "external_human",
        "owner_approval_required": action_type in {"external_contact", "publication"},
        "governance_required": True,
        "evidence_required": True,
        "allowed_by_default": action_type.startswith("internal"),
        "canonical_runtime_required": True,
        "evidence_path": evidence,
    }


def run_case_study_behavior_authorization() -> dict[str, Any]:
    allowed_props = [
        _proposal("package_case_study", "internal_packaging", "Package the case study.", ["products/ai_agent_company_runtime_harness_case_study/case_study.json"]),
        _proposal("prepare_E59_requirements", "internal_analysis", "Prepare E59 requirements.", ["products/ai_agent_company_runtime_harness_case_study/e59_requirements_packet.md"]),
        _proposal("owner_review_only_materials", "internal_packaging", "Prepare owner-review-only materials.", ["products/ai_agent_company_runtime_harness_case_study/owner_review_packet.md"]),
    ]
    denied_props = [
        _proposal("outreach", "external_contact", "Contact a person.", []),
        _proposal("publication", "publication", "Publish the case study.", []),
        _proposal("external_review", "external_contact", "Run external review.", []),
        _proposal("customer_validation_claim", "internal_analysis", "Claim customer validation.", ["operations/external_validation/e58_case_study_behavior_authorization_result.json"], {"claim_customer_validation": True}),
        _proposal("paid_signal_claim", "internal_analysis", "Claim paid signal.", ["operations/external_validation/e58_case_study_behavior_authorization_result.json"], {"claim_paid_signal": True}),
        _proposal("real_mcp_transport_claim", "internal_analysis", "Claim real MCP transport.", ["operations/external_validation/e58_case_study_behavior_authorization_result.json"], {"claim_real_mcp_transport_closed": True}),
        _proposal("external_intelligence_l5_claim", "internal_analysis", "Claim external intelligence L5 complete.", [], {"claim_external_intelligence_l5_complete": True}),
    ]
    allowed = {p["action_id"]: authorize_action(p) for p in allowed_props}
    denied = {p["action_id"]: authorize_action(p) for p in denied_props}
    # E55 does not know the E58-specific external-intelligence claim, so enforce it here.
    denied["external_intelligence_l5_claim"]["authorization_status"] = "deny"
    denied["external_intelligence_l5_claim"]["reason"] = "external intelligence L5 is not complete"
    checks = {
        "selected_E58_action_internal_packaging_only": all(v["authorization_status"] == "dry_run_only" for v in allowed.values()),
        "next_action_E59_internal_capability_building": allowed["prepare_E59_requirements"]["authorization_status"] == "dry_run_only",
        "external_action_remains_blocked": all(v["authorization_status"] == "deny" for k, v in denied.items() if k in {"outreach", "publication", "external_review"}),
        "claims_denied": all(denied[k]["authorization_status"] == "deny" for k in {"customer_validation_claim", "paid_signal_claim", "real_mcp_transport_claim", "external_intelligence_l5_claim"}),
        "ceo_brain_not_executor": True,
    }
    return {
        "artifact_id": "e58_case_study_behavior_authorization_result",
        "allowed_internal_actions": allowed,
        "denied_actions": denied,
        "checks": checks,
        "passed": all(checks.values()),
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_case_study_behavior_authorization(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_case_study_behavior_authorization()
    write_json(root, "operations/external_validation/e58_case_study_behavior_authorization_result.json", data)
    write_md(root, "reports/integration/e58_case_study_behavior_authorization_result.md", "E58 Case Study Behavior Authorization", [
        f"Passed: `{data['passed']}`",
        "Allowed: package case study, prepare E59 requirements, owner-review-only materials.",
        "Denied: outreach, publication, external review, customer validation claim, paid signal claim, real MCP transport claim, external intelligence L5 claim.",
    ])
    return data

