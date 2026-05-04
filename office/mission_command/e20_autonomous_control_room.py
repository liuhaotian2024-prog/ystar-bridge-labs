from __future__ import annotations

from typing import Any, Dict


def build_autonomous_control_room(reclassification: Dict[str, Any], provider_capability: Dict[str, Any], route: Dict[str, Any] | None = None) -> Dict[str, Any]:
    rows = reclassification["rows"]
    return {
        "artifact_id": "e20_autonomous_control_room",
        "control_room_type": "risk_tiered_autonomous_outbound_surface",
        "default_model": "agent_autonomous_by_risk_tier_not_owner_manual_by_default",
        "actions_agent_can_do_autonomously_now": [row for row in rows if row["executor_decision"] in {"agent_autonomous_allowed", "agent_autonomous_allowed_with_limits"}],
        "actions_agent_could_do_after_provider_implementation": [row for row in rows if row["classification"] == "policy_allows_autonomous_but_provider_missing"],
        "actions_requiring_owner_approval": [row for row in rows if row["executor_decision"] == "owner_approval_required"],
        "actions_owner_may_do_manually_as_override": [row for row in rows if row["executor_decision"] == "provider_capability_missing"],
        "blocked_actions": [row for row in rows if row["executor_decision"] == "blocked_no_go"],
        "missing_evidence_actions": [row for row in rows if row["executor_decision"] == "evidence_required_before_execution"],
        "provider_blockers": [
            "live provider adapter missing",
            "live provider tests missing",
            "rollback/reversal path missing for live sends",
        ]
        if not provider_capability.get("live_provider_adapter_present")
        else [],
        "next_commercial_route": route.get("recommended_route") if route else "prepare_E21_autonomous_provider_adapter_plan",
        "provider_capability_status": provider_capability["provider_capability_status"],
        "external_action_executed": False,
    }


def render_autonomous_control_room(room: Dict[str, Any]) -> str:
    lines = [
        "# E20 Autonomous Outbound Control Room",
        "",
        f"- default_model: {room['default_model']}",
        f"- provider_capability_status: {room['provider_capability_status']}",
        f"- next_commercial_route: {room['next_commercial_route']}",
        "- external_action_executed: false",
        "",
        "## Counts",
        f"- autonomous_now: {len(room['actions_agent_can_do_autonomously_now'])}",
        f"- autonomous_after_provider: {len(room['actions_agent_could_do_after_provider_implementation'])}",
        f"- owner_approval_required: {len(room['actions_requiring_owner_approval'])}",
        f"- owner_manual_override_possible: {len(room['actions_owner_may_do_manually_as_override'])}",
        f"- blocked: {len(room['blocked_actions'])}",
        f"- evidence_required: {len(room['missing_evidence_actions'])}",
        "",
        "## Provider Blockers",
    ]
    lines.extend(f"- {item}" for item in room["provider_blockers"])
    lines.extend(["", "## Autonomous After Provider Implementation"])
    for row in room["actions_agent_could_do_after_provider_implementation"]:
        lines.append(f"- {row['target_name']}: {row['classification']}")
    return "\n".join(lines).rstrip() + "\n"
