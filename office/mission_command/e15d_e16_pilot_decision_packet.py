from __future__ import annotations

from typing import Any, Dict, List, Mapping


E16_ROUTES = [
    "E16A_owner_approves_draft_only_pilot",
    "E16B_owner_manual_send_first",
    "E16C_one_action_send_gated_pilot_after_authorization",
    "E16D_expand_evidence_before_send",
    "E16E_suppress_current_batch_and_rebuild",
]


def build_e15d_e16_pilot_decision_packet(
    *,
    console: Mapping[str, Any],
    queue: Mapping[str, Any],
    audit_receipts: Mapping[str, Any],
) -> Dict[str, Any]:
    target_fit_ready = console.get("primary_action_count") == 3 and not queue.get("external_action_executed")
    if target_fit_ready:
        recommended = "E16B_owner_manual_send_first"
        reason = "E15A/C3 targets and messages are ready; safest next proof is owner manual send before activating gov-mcp send."
    else:
        recommended = "E16D_expand_evidence_before_send"
        reason = "Target/message fit is not sufficient for send-gated pilot."
    return {
        "packet_id": "e15d_e16_controlled_pilot_decision_packet",
        "recommended_route": recommended,
        "recommendation_reason": reason,
        "target_message_fit_ready": target_fit_ready,
        "send_gated_queue_ready_but_blocked": queue.get("blocked_until_authorized") is True,
        "audit_receipts_ready": len(audit_receipts.get("receipts", [])) == 3,
        "routes": {
            "E16A_owner_approves_draft_only_pilot": {
                "trigger": "owner wants gov-mcp to prepare drafts only",
                "allowed_actions": ["draft_only_generation", "draft_receipts", "no_send"],
                "blocked_actions": ["real_send", "publication", "payment"],
                "owner_involvement": "approve draft-only envelope",
            },
            "E16B_owner_manual_send_first": {
                "trigger": "target/message fit ready but owner wants lowest-risk validation first",
                "allowed_actions": ["owner manually sends E15A primary actions", "owner records ledger and feedback"],
                "blocked_actions": ["agent autonomous send", "gov-mcp live send without activated envelope"],
                "owner_involvement": "manual send and feedback capture",
            },
            "E16C_one_action_send_gated_pilot_after_authorization": {
                "trigger": "owner explicitly activates narrow one-action send-gated envelope",
                "allowed_actions": ["one gov-mcp controlled send", "receipt", "feedback wait state"],
                "blocked_actions": ["more than one send", "follow-up without positive signal", "out-of-envelope send"],
                "owner_involvement": "constitutional envelope approval only",
            },
            "E16D_expand_evidence_before_send": {
                "trigger": "target/message fit weak or required evidence missing",
                "allowed_actions": ["public read-only target/evidence improvement", "message revision"],
                "blocked_actions": ["send before evidence improves"],
                "owner_involvement": "review improved batch",
            },
            "E16E_suppress_current_batch_and_rebuild": {
                "trigger": "suppression/risk/do-not-contact emerges",
                "allowed_actions": ["suppress targets", "replace batch", "record audit receipt"],
                "blocked_actions": ["contact suppressed target"],
                "owner_involvement": "review suppression if ambiguous",
            },
        },
        "external_action_executed": False,
    }


def validate_e15d_e16_pilot_decision_packet(packet: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if packet.get("recommended_route") not in E16_ROUTES:
        errors.append("invalid_e16_route")
    for route in E16_ROUTES:
        if route not in packet.get("routes", {}):
            errors.append(f"missing_e16_route_{route}")
    if packet.get("external_action_executed") is not False:
        errors.append("e16_packet_must_not_execute_external_action")
    if packet.get("recommended_route") == "E16C_one_action_send_gated_pilot_after_authorization":
        errors.append("default_must_not_skip_to_send_gated_execution")
    return list(dict.fromkeys(errors))
