from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15D_EXECUTION_MODES = [
    "deny",
    "draft_only",
    "owner_handoff",
    "send_gated_pending_authorization",
    "send_gated_dry_run",
    "gov_mcp_execute_after_activation",
]

E15D_CURRENTLY_EXECUTABLE_MODES = ["draft_only", "owner_handoff", "send_gated_dry_run"]


def build_e15d_gov_mcp_outbound_adapter_contract() -> Dict[str, Any]:
    return {
        "contract_id": "e15d_gov_mcp_outbound_execution_adapter_contract",
        "gateway_owner": "gov-mcp",
        "execution_modes": E15D_EXECUTION_MODES,
        "currently_executable_modes_in_e15d": E15D_CURRENTLY_EXECUTABLE_MODES,
        "prohibited_live_actions_in_e15d": [
            "real_email_send",
            "real_message_send",
            "publication",
            "account_creation",
            "login",
            "form_submission",
            "external_validation_submission",
            "payment",
            "contract",
            "core_writeback",
        ],
        "input_schema": {
            "action_intent_packet": "REQUIRED",
            "ygov_decision_envelope": "REQUIRED",
            "authorization_envelope_ref": "REQUIRED",
            "idempotency_key": "REQUIRED",
        },
        "preflight_schema": {
            "kill_switch_guard": "required_pass",
            "rate_limit_guard": "required_pass",
            "suppression_guard": "required_pass",
            "envelope_active_guard": "required_for_live_send",
            "message_hash_guard": "required_pass",
        },
        "execution_request_schema": {
            "execution_mode": "|".join(E15D_EXECUTION_MODES),
            "target_id": "REQUIRED",
            "channel": "REQUIRED",
            "message_hash": "REQUIRED",
            "send_allowed_now": False,
        },
        "execution_receipt_schema": {
            "receipt_id": "REQUIRED",
            "action_id": "REQUIRED",
            "execution_mode": "REQUIRED",
            "external_action_executed": False,
            "ledger_transition": "REQUIRED",
            "feedback_wait_state": "REQUIRED",
        },
        "failure_receipt_schema": {
            "failure_code": "deny|guard_failed|authorization_missing|rate_limit|suppressed|kill_switch|adapter_unavailable",
            "reason_codes": [],
        },
        "idempotency_key": "sha256(action_id + message_hash + envelope_id)",
        "rate_limit_guard": {"max_actions_per_day": 1, "max_actions_per_batch": 3},
        "suppression_guard": "must deny suppressed/do-not-contact targets",
        "kill_switch_guard": "global and batch kill switches must be checked before any send",
        "audit_ledger_hook": "write action ledger receipt before feedback can be counted",
        "feedback_wait_state_hook": "set waiting_feedback only after valid sent receipt",
        "executes_real_external_action_in_e15d": False,
    }


def mode_for_e15d_policy_decision(decision: Mapping[str, Any]) -> str:
    if decision.get("decision") == "gov_mcp_execute_allowed_after_activation":
        return "gov_mcp_execute_after_activation"
    if decision.get("decision") == "send_gated_requires_owner_authorization":
        return "send_gated_pending_authorization"
    if decision.get("decision") == "suppress_target":
        return "deny"
    if decision.get("decision") in {"require_more_research", "require_offer_revision", "require_owner_review"}:
        return "deny"
    if decision.get("decision") == "draft_only":
        return "draft_only"
    return "send_gated_dry_run"


def validate_e15d_gov_mcp_outbound_adapter_contract(contract: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if contract.get("gateway_owner") != "gov-mcp":
        errors.append("gov_mcp_must_own_adapter")
    for mode in E15D_EXECUTION_MODES:
        if mode not in contract.get("execution_modes", []):
            errors.append(f"missing_execution_mode_{mode}")
    for mode in ["draft_only", "owner_handoff", "send_gated_dry_run"]:
        if mode not in contract.get("currently_executable_modes_in_e15d", []):
            errors.append(f"missing_e15d_current_mode_{mode}")
    if contract.get("executes_real_external_action_in_e15d") is not False:
        errors.append("adapter_contract_must_not_execute_real_action")
    if "real_email_send" not in contract.get("prohibited_live_actions_in_e15d", []):
        errors.append("real_email_send_must_be_prohibited")
    return list(dict.fromkeys(errors))
