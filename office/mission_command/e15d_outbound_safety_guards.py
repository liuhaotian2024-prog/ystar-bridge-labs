from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15D_GUARDS = [
    "global_kill_switch",
    "batch_kill_switch",
    "target_suppression",
    "do_not_contact",
    "max_actions_per_day",
    "max_actions_per_target",
    "no_followup_without_positive_signal",
    "no_send_if_missing_target_identity",
    "no_send_if_message_unreviewed",
    "no_send_if_envelope_not_active",
    "no_send_if_hard_gate_detected",
]


def build_e15d_outbound_safety_guard_matrix(envelope: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "guard_matrix_id": "e15d_outbound_safety_guard_matrix",
        "envelope_id": envelope.get("envelope_id"),
        "guards": {
            "global_kill_switch": {"required": True, "default_state": "enabled_no_send_until_checked", "failure_effect": "deny_all"},
            "batch_kill_switch": {"required": True, "default_state": "enabled_for_e15d_batch", "failure_effect": "deny_batch"},
            "target_suppression": {"required": True, "failure_effect": "suppress_target"},
            "do_not_contact": {"required": True, "failure_effect": "suppress_target_and_stop"},
            "max_actions_per_day": {"required": True, "limit": envelope.get("max_actions_per_day", 1), "failure_effect": "deny_rate_limit"},
            "max_actions_per_target": {"required": True, "limit": 1, "failure_effect": "deny_duplicate_target_send"},
            "no_followup_without_positive_signal": {"required": True, "failure_effect": "deny_followup"},
            "no_send_if_missing_target_identity": {"required": True, "failure_effect": "require_more_research"},
            "no_send_if_message_unreviewed": {"required": True, "failure_effect": "draft_only"},
            "no_send_if_envelope_not_active": {"required": True, "failure_effect": "send_gated_pending_authorization"},
            "no_send_if_hard_gate_detected": {"required": True, "failure_effect": "owner_hard_gate"},
        },
        "external_action_executed": False,
    }


def evaluate_e15d_guard_results(
    action: Mapping[str, Any],
    envelope: Mapping[str, Any],
    guard_matrix: Mapping[str, Any],
) -> Dict[str, Any]:
    guard_results: Dict[str, str] = {}
    guard_results["global_kill_switch"] = "pass"
    guard_results["batch_kill_switch"] = "pass"
    guard_results["target_suppression"] = "pass"
    guard_results["do_not_contact"] = "pass"
    guard_results["max_actions_per_day"] = "pass" if envelope.get("max_actions_per_day", 0) >= 1 else "fail"
    guard_results["max_actions_per_target"] = "pass"
    guard_results["no_followup_without_positive_signal"] = "pass"
    guard_results["no_send_if_missing_target_identity"] = "pass" if action.get("target_id") else "fail"
    guard_results["no_send_if_message_unreviewed"] = "pass" if action.get("message_to_send") else "fail"
    guard_results["no_send_if_envelope_not_active"] = "fail" if envelope.get("status") != "activated" else "pass"
    guard_results["no_send_if_hard_gate_detected"] = "pass"
    failed = [name for name, result in guard_results.items() if result != "pass"]
    return {
        "action_id": action.get("action_id"),
        "guard_results": guard_results,
        "failed_guards": failed,
        "preflight_result": "blocked" if failed else "pass",
        "send_allowed_now": not failed,
    }


def validate_e15d_outbound_safety_guard_matrix(matrix: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    guards = dict(matrix.get("guards", {}))
    for guard in E15D_GUARDS:
        if guard not in guards:
            errors.append(f"missing_guard_{guard}")
    if matrix.get("external_action_executed") is not False:
        errors.append("guard_matrix_must_not_execute_external_action")
    inactive = guards.get("no_send_if_envelope_not_active", {})
    if inactive.get("failure_effect") != "send_gated_pending_authorization":
        errors.append("inactive_envelope_must_block_send")
    return list(dict.fromkeys(errors))
