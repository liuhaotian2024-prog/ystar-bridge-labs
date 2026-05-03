from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Mapping


E15D_YGOV_DECISIONS = [
    "deny",
    "draft_only",
    "owner_handoff",
    "send_gated_requires_owner_authorization",
    "gov_mcp_execute_allowed_after_activation",
    "suppress_target",
    "require_more_research",
    "require_offer_revision",
    "require_owner_review",
]


def _decision_id(action_id: str) -> str:
    digest = hashlib.sha256(f"e15d:{action_id}".encode("utf-8")).hexdigest()[:10]
    return f"e15d_ygov_decision_{digest}"


def evaluate_e15d_ygov_outbound_action(
    action: Mapping[str, Any],
    envelope: Mapping[str, Any],
    *,
    suppressed: bool = False,
) -> Dict[str, Any]:
    reason_codes: List[str] = []
    if suppressed:
        decision = "suppress_target"
        reason_codes.append("target_suppressed_or_do_not_contact")
    elif not action.get("target_id") or not action.get("message_to_send"):
        decision = "require_more_research"
        reason_codes.append("missing_target_or_message")
    elif envelope.get("status") != "activated":
        decision = "send_gated_requires_owner_authorization"
        reason_codes.append("owner_authorization_envelope_not_active")
    else:
        decision = "gov_mcp_execute_allowed_after_activation"
        reason_codes.append("active_envelope_present")
    reason_codes.extend(
        [
            "low_risk_validation_messaging_domain",
            "ai_transparent_message_required",
            "opt_out_language_required",
            "action_ledger_required",
            "feedback_wait_state_required",
        ]
    )
    send_allowed = decision == "gov_mcp_execute_allowed_after_activation"
    return {
        "action_id": action.get("action_id"),
        "policy_id": "e15d_ygov_outbound_validation_messaging_policy",
        "decision_id": _decision_id(str(action.get("action_id", ""))),
        "decision": decision,
        "capability_domain": "external_validation_message",
        "risk_tier": "Tier 5 controlled low-volume outbound validation pilot",
        "envelope_status": envelope.get("status"),
        "target_status": "suppressed" if suppressed else "valid_owner_handoff_target",
        "message_status": "present" if action.get("message_to_send") else "missing",
        "suppression_status": "suppressed" if suppressed else "clear",
        "allowed_next_steps": ["draft_only_receipt", "owner_handoff", "send_gated_dry_run"]
        + (["gov_mcp_execute_after_activation"] if send_allowed else []),
        "prohibited_next_steps": [
            "real_email_or_message_send_now",
            "publication",
            "payment",
            "account_creation",
            "form_submission",
            "login",
            "external_validation_submission",
            "core_writeback",
        ],
        "deterministic_reason_codes": reason_codes,
        "real_send_allowed_now": send_allowed,
        "external_action_executed": False,
    }


def build_e15d_ygov_outbound_policy(console: Mapping[str, Any], envelope: Mapping[str, Any]) -> Dict[str, Any]:
    decisions = [evaluate_e15d_ygov_outbound_action(action, envelope) for action in console.get("primary_actions", [])]
    return {
        "policy_id": "e15d_ygov_outbound_validation_messaging_policy",
        "decision_values": E15D_YGOV_DECISIONS,
        "source_console_id": console.get("console_id"),
        "envelope_id": envelope.get("envelope_id"),
        "decisions": decisions,
        "real_send_allowed_now": any(decision.get("real_send_allowed_now") for decision in decisions),
        "external_action_executed": False,
    }


def validate_e15d_ygov_outbound_policy(policy: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    decisions = list(policy.get("decisions", []))
    if len(decisions) != 3:
        errors.append("policy_must_cover_three_primary_actions")
    if policy.get("real_send_allowed_now") is not False:
        errors.append("policy_must_not_allow_real_send_now")
    if policy.get("external_action_executed") is not False:
        errors.append("policy_must_not_execute_external_action")
    for decision in decisions:
        if decision.get("decision") not in E15D_YGOV_DECISIONS:
            errors.append(f"{decision.get('action_id')}:invalid_decision")
        if "owner_authorization_envelope_not_active" not in decision.get("deterministic_reason_codes", []):
            errors.append(f"{decision.get('action_id')}:missing_owner_authorization_reason")
        if "real_email_or_message_send_now" not in decision.get("prohibited_next_steps", []):
            errors.append(f"{decision.get('action_id')}:must_prohibit_real_send_now")
        if decision.get("external_action_executed") is not False:
            errors.append(f"{decision.get('action_id')}:external_action_executed")
    return list(dict.fromkeys(errors))
