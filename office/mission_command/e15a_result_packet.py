from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15A_NEXT_ROUTES = [
    "E15A_send_now_owner_operated",
    "E15B_offer_revision_before_send",
    "E15C_expand_target_discovery",
    "E15D_gov_mcp_controlled_execution_pilot",
    "E15E_suppression_and_batch_replacement",
]


def build_e15a_result_packet(
    *,
    console: Mapping[str, Any],
    ledger_state: Mapping[str, Any],
    feedback_form: Mapping[str, Any],
    signal_fixture: Mapping[str, Any],
    replacement_plan: Mapping[str, Any],
) -> Dict[str, Any]:
    primary_routes = {row.get("route") for row in replacement_plan.get("primary_routes", [])}
    if primary_routes == {"keep_primary"} and console.get("primary_action_count") == 3:
        next_route = "E15A_send_now_owner_operated"
        reason = "The three primary actions are owner-handoff ready and no replacement/suppression is required."
    elif "suppress_target" in primary_routes:
        next_route = "E15E_suppression_and_batch_replacement"
        reason = "At least one primary target is suppressed and should be replaced before sending."
    elif "require_more_research" in primary_routes:
        next_route = "E15C_expand_target_discovery"
        reason = "At least one target/message lacks enough information for safe owner send."
    else:
        next_route = "E15B_offer_revision_before_send"
        reason = "Target/message fit requires revision before owner-operated sending."
    return {
        "packet_id": "e15a_result_packet",
        "current_execution_status": "awaiting_owner_send",
        "ready_for_owner_send_actions": [action["action_id"] for action in console.get("primary_actions", [])],
        "actions_requiring_replacement_or_suppression": [
            row["action_id"]
            for row in replacement_plan.get("primary_routes", [])
            if row.get("route") != "keep_primary"
        ],
        "expected_feedback_wait_state": "waiting_feedback_after_owner_sent_confirmation",
        "required_evidence_to_move_next": [
            "owner send confirmation fixture",
            "valid action ledger transition",
            "owner-entered feedback event or valid no-response after wait window",
        ],
        "next_route_recommendation": next_route,
        "recommendation_reason": reason,
        "routes": {
            "E15A_send_now_owner_operated": {
                "trigger": "primary actions are ready and owner chooses to manually send",
                "allowed_actions": ["owner manually sends selected copy/paste blocks", "owner records ledger rows", "owner records feedback"],
                "blocked_actions": ["Aiden autonomous send", "agent publication", "payment", "login", "form submission"],
            },
            "E15B_offer_revision_before_send": {
                "trigger": "message or offer fit is weak before sending",
                "allowed_actions": ["revise draft", "rerun owner console generation"],
                "blocked_actions": ["send weak draft"],
            },
            "E15C_expand_target_discovery": {
                "trigger": "target information is incomplete or target fit weak",
                "allowed_actions": ["public read-only target research", "replace target batch"],
                "blocked_actions": ["scrape private contact data"],
            },
            "E15D_gov_mcp_controlled_execution_pilot": {
                "trigger": "owner later activates a narrow gov-mcp execution envelope",
                "allowed_actions": ["prepare controlled execution pilot"],
                "blocked_actions": ["execute without owner constitutional envelope"],
            },
            "E15E_suppression_and_batch_replacement": {
                "trigger": "do-not-contact, suppression, or safety concern",
                "allowed_actions": ["suppress target", "replace with fallback", "record governance receipt"],
                "blocked_actions": ["follow up on suppressed target"],
            },
        },
        "feedback_capture_ready": bool(feedback_form.get("valid_actions")),
        "signal_fixture_ready": bool(signal_fixture.get("cases")),
        "ledger_waiting_owner_send_count": len(ledger_state.get("rows", [])),
        "external_action_executed_by_agent": False,
    }


def validate_e15a_result_packet(packet: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if packet.get("next_route_recommendation") not in E15A_NEXT_ROUTES:
        errors.append("invalid_next_route_recommendation")
    if packet.get("external_action_executed_by_agent") is not False:
        errors.append("result_packet_must_not_execute_agent_action")
    if len(packet.get("ready_for_owner_send_actions", [])) != 3:
        errors.append("result_packet_must_list_three_ready_actions")
    if packet.get("feedback_capture_ready") is not True:
        errors.append("feedback_capture_must_be_ready")
    if packet.get("signal_fixture_ready") is not True:
        errors.append("signal_fixture_must_be_ready")
    for route in E15A_NEXT_ROUTES:
        if route not in packet.get("routes", {}):
            errors.append(f"missing_next_route_{route}")
    return list(dict.fromkeys(errors))
