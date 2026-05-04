from __future__ import annotations

from typing import Any, Dict, List

from .e20_human_intervention_boundary import requires_human_intervention
from .e20_provider_capability_detector import live_ready


E20_EXECUTOR_DECISIONS = [
    "agent_autonomous_allowed",
    "agent_autonomous_allowed_with_limits",
    "owner_approval_required",
    "owner_manual_only",
    "blocked_no_go",
    "provider_capability_missing",
    "evidence_required_before_execution",
]


NO_GO_ACTIONS = {
    "payment",
    "contract",
    "legal_commitment",
    "financial_commitment",
    "credential_disclosure",
    "account_creation",
    "login",
    "customer_private_data_access",
    "regulated_form_submission",
    "fake_feedback",
    "fake_target_evidence",
    "unapproved_provider_api_call",
}


def infer_risk_tier(action: Dict[str, Any]) -> str:
    action_type = str(action.get("action_type", action.get("capability_domain", "external_validation_message")))
    if action_type in NO_GO_ACTIONS or action.get("no_go") is True:
        return "T5_no_go_blocked"
    if requires_human_intervention(action):
        return "T4_high_risk_owner_approval_required"
    if action_type in {"internal_artifact", "dry_run", "feedback_classification"}:
        return "T0_internal_only_no_external_effect"
    if action_type in {"public_read_only", "draft_preview"}:
        return "T1_low_risk_reversible_external"
    if action_type in {"external_validation_message", "low_volume_publication"}:
        return "T2_low_medium_limited_outbound"
    return "T3_medium_risk_requires_strict_limits"


def classify_autonomous_eligibility(action: Dict[str, Any], provider_capability: Dict[str, Any]) -> Dict[str, Any]:
    tier = str(action.get("risk_tier") or infer_risk_tier(action))
    reason_codes: List[str] = []
    evidence_sufficient = bool(action.get("evidence_sufficient", False))
    suppression_clear = bool(action.get("suppression_clear", False))
    policy_compatible = bool(action.get("policy_compatible", True))
    provider_live_ready = live_ready(provider_capability)

    if tier == "T5_no_go_blocked":
        decision = "blocked_no_go"
        reason_codes.append("no_go_action_or_blocked_tier")
    elif not evidence_sufficient:
        decision = "evidence_required_before_execution"
        reason_codes.append("evidence_insufficient")
    elif not policy_compatible:
        decision = "owner_approval_required"
        reason_codes.append("policy_not_compatible_without_owner_gate")
    elif not suppression_clear:
        decision = "blocked_no_go"
        reason_codes.append("suppression_not_clear")
    elif tier == "T4_high_risk_owner_approval_required":
        decision = "owner_approval_required"
        reason_codes.append("high_risk_owner_gate")
    elif tier in {"T0_internal_only_no_external_effect", "T1_low_risk_reversible_external"}:
        decision = "agent_autonomous_allowed" if provider_live_ready or tier == "T0_internal_only_no_external_effect" else "provider_capability_missing"
        reason_codes.append("low_risk_autonomous_policy")
        if decision == "provider_capability_missing":
            reason_codes.append("live_provider_adapter_missing")
    elif tier in {"T2_low_medium_limited_outbound", "T3_medium_risk_requires_strict_limits"}:
        decision = "agent_autonomous_allowed_with_limits" if provider_live_ready else "provider_capability_missing"
        reason_codes.append("limited_outbound_autonomous_policy")
        if decision == "provider_capability_missing":
            reason_codes.append("policy_allows_autonomous_but_provider_missing")
    else:
        decision = "owner_approval_required"
        reason_codes.append("unknown_tier_defaults_to_owner_gate")

    return {
        "action_id": action.get("action_id", ""),
        "risk_tier": tier,
        "executor_decision": decision,
        "provider_capability_status": provider_capability.get("provider_capability_status"),
        "policy_allows_autonomous_in_principle": tier in {"T0_internal_only_no_external_effect", "T1_low_risk_reversible_external", "T2_low_medium_limited_outbound", "T3_medium_risk_requires_strict_limits"} and evidence_sufficient and suppression_clear and policy_compatible,
        "owner_approval_required": decision == "owner_approval_required",
        "owner_manual_only": decision == "owner_manual_only",
        "evidence_required": decision == "evidence_required_before_execution",
        "reason_codes": reason_codes,
        "external_action_executed": False,
    }


def build_autonomous_execution_eligibility_rules() -> Dict[str, Any]:
    return {
        "artifact_id": "e20_autonomous_execution_eligibility_rules",
        "decisions": E20_EXECUTOR_DECISIONS,
        "rule_order": [
            "no_go_blocks_first",
            "evidence_required_before_execution",
            "policy_compatibility_required",
            "suppression_clear_required",
            "human_intervention_boundary",
            "provider_live_readiness",
            "rate_limit_idempotency_audit_required",
        ],
        "manual_send_default": False,
        "provider_missing_is_not_owner_manual_required": True,
        "external_action_executed": False,
    }
