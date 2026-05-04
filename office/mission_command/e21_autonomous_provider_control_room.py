from __future__ import annotations

from typing import Any, Dict


def build_autonomous_provider_control_room(provider_sync: Dict[str, Any], reclassification: Dict[str, Any], promotion_gate: Dict[str, Any], route: Dict[str, Any] | None = None) -> Dict[str, Any]:
    rows = reclassification["rows"]
    return {
        "artifact_id": "e21_autonomous_provider_control_room",
        "control_room_type": "governed_provider_foundation_surface",
        "default_model": "agent_autonomous_when_risk_policy_provider_and_guards_pass",
        "provider_capability_status": provider_sync["capability_status"],
        "dry_run_available_actions": [row for row in rows if row["dry_run_available"]],
        "live_scaffolded_but_disabled_actions": [row for row in rows if row["live_scaffolded_but_disabled"]],
        "live_ready_actions": [row for row in rows if row["live_provider_enabled"]],
        "evidence_required_actions": [row for row in rows if row["evidence_required"]],
        "owner_approval_required_by_risk_tier_actions": [row for row in rows if row["owner_approval_required_by_risk_tier"]],
        "live_promotion_allowed_actions": [row for row in promotion_gate["rows"] if row["promotion_allowed"]],
        "live_send_blocked_reason": provider_sync["live_execution_blocked_reason"],
        "next_route": route.get("recommended_route") if route else "E22_autonomous_dry_run_batch_execution",
        "owner_manual_send_is_default": False,
        "external_action_executed": False,
    }


def render_autonomous_provider_control_room(room: Dict[str, Any]) -> str:
    lines = [
        "# E21 Autonomous Provider Control Room",
        "",
        f"- default_model: {room['default_model']}",
        f"- provider_capability_status: {room['provider_capability_status']}",
        f"- live_send_blocked_reason: {room['live_send_blocked_reason']}",
        f"- owner_manual_send_is_default: {str(room['owner_manual_send_is_default']).lower()}",
        f"- next_route: {room['next_route']}",
        "- external_action_executed: false",
        "",
        "## Counts",
        f"- dry_run_available_actions: {len(room['dry_run_available_actions'])}",
        f"- live_scaffolded_but_disabled_actions: {len(room['live_scaffolded_but_disabled_actions'])}",
        f"- live_ready_actions: {len(room['live_ready_actions'])}",
        f"- evidence_required_actions: {len(room['evidence_required_actions'])}",
        f"- owner_approval_required_by_risk_tier_actions: {len(room['owner_approval_required_by_risk_tier_actions'])}",
    ]
    return "\n".join(lines).rstrip() + "\n"
