from __future__ import annotations

from typing import Any, Dict, List, Mapping


E15A_TARGET_ROUTES = [
    "keep_primary",
    "replace_with_fallback",
    "suppress_target",
    "require_more_research",
    "require_owner_review",
    "revise_message_before_send",
]


def route_e15a_target(action: Mapping[str, Any], confirmation: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    confirmation = confirmation or {}
    send_status = str(confirmation.get("send_status", "not_sent"))
    missing_message = not str(action.get("message_to_send", "")).strip()
    if send_status == "suppressed_by_owner":
        route = "suppress_target"
        reason = "owner_suppressed_target"
    elif send_status == "replaced_by_fallback":
        route = "replace_with_fallback"
        reason = "owner_replaced_primary"
    elif send_status == "blocked_by_missing_target_info" or missing_message:
        route = "require_more_research"
        reason = "target_or_message_missing_required_fields"
    elif send_status == "skipped_by_owner":
        route = "replace_with_fallback"
        reason = "owner_skipped_primary"
    elif send_status == "not_sent":
        route = "keep_primary"
        reason = "primary_ready_but_awaiting_owner_send"
    elif send_status == "sent_confirmed_by_owner":
        route = "keep_primary"
        reason = "valid_owner_sent_confirmation_can_wait_for_feedback"
    else:
        route = "require_owner_review"
        reason = "unknown_send_status"
    return {
        "action_id": action.get("action_id"),
        "target_id": action.get("target_id"),
        "target_name": action.get("target_name"),
        "send_status": send_status,
        "route": route,
        "reason": reason,
        "fallback_allowed": route in {"replace_with_fallback", "require_more_research"},
        "owner_review_required": route == "require_owner_review",
        "suppression_required": route == "suppress_target",
    }


def build_e15a_target_replacement_plan(console: Mapping[str, Any], confirmation_fixture: Mapping[str, Any]) -> Dict[str, Any]:
    confirmation_by_action = {row["action_id"]: row for row in confirmation_fixture.get("rows", [])}
    primary_routes = [
        route_e15a_target(action, confirmation_by_action.get(action["action_id"]))
        for action in console.get("primary_actions", [])
    ]
    fallback_pool = [
        {
            "action_id": action["action_id"],
            "target_id": action["target_id"],
            "target_name": action["target_name"],
            "use_condition": "Use only when a primary is skipped, suppressed, or blocked by missing target info.",
        }
        for action in console.get("fallback_actions", [])
    ]
    return {
        "plan_id": "e15a_target_replacement_plan",
        "routes_supported": E15A_TARGET_ROUTES,
        "primary_routes": primary_routes,
        "fallback_pool": fallback_pool,
        "default_route": "keep_primary",
        "external_action_executed_by_agent": False,
    }


def validate_e15a_target_replacement_plan(plan: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if plan.get("external_action_executed_by_agent") is not False:
        errors.append("replacement_plan_must_not_execute_agent_action")
    if len(plan.get("primary_routes", [])) != 3:
        errors.append("replacement_plan_must_cover_three_primary_actions")
    if len(plan.get("fallback_pool", [])) != 2:
        errors.append("replacement_plan_must_include_two_fallback_actions")
    routes_supported = set(plan.get("routes_supported", []))
    for route in E15A_TARGET_ROUTES:
        if route not in routes_supported:
            errors.append(f"missing_route_{route}")
    for row in plan.get("primary_routes", []):
        if row.get("route") not in E15A_TARGET_ROUTES:
            errors.append(f"{row.get('action_id')}:invalid_route")
    return list(dict.fromkeys(errors))
