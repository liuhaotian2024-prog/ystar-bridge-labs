from __future__ import annotations

from typing import Any, Dict


def build_e20_route_decision(reclassification: Dict[str, Any], provider_capability: Dict[str, Any]) -> Dict[str, Any]:
    counts = reclassification["summary_counts"]
    if counts.get("provider_capability_missing", 0) > 0:
        recommended = "prepare_E21_autonomous_provider_adapter_plan"
        reason = "Low-risk autonomous execution is policy-eligible for several candidates, but live provider capability is missing."
    elif counts.get("evidence_required_before_execution", 0) > 0:
        recommended = "expand_target_evidence_before_autonomous_send"
        reason = "Some candidates lack sufficient evidence."
    elif counts.get("owner_approval_required", 0) > 0:
        recommended = "owner_approval_required_for_high_risk_only"
        reason = "Only high-risk actions should route to owner."
    else:
        recommended = "run_autonomous_dry_run_batch_first"
        reason = "Provider and evidence conditions allow a dry-run batch."
    return {
        "artifact_id": "e20_route_decision_packet",
        "recommended_route": recommended,
        "reason": reason,
        "route_options": {
            "build_real_provider_adapter_for_low_risk_autonomous_send": "Future gov-mcp milestone if owner wants live autonomous sends.",
            "run_autonomous_dry_run_batch_first": "Allowed locally with no provider call.",
            "revise_messages_before_autonomous_send": "Use if message variants are weak.",
            "expand_target_evidence_before_autonomous_send": "Use for evidence_required candidates.",
            "owner_approval_required_for_high_risk_only": "Owner gates exceptional risk, not normal low-risk send.",
            "keep_high_risk_actions_blocked": "T4/T5 remain gated or blocked.",
            "resolve_gov_mcp_provider_gap": "Implement live provider adapter and tests in gov-mcp.",
            "prepare_E21_autonomous_provider_adapter_plan": "Recommended next step.",
        },
        "summary_counts": counts,
        "real_external_action_executed": False,
    }


def render_route_decision(packet: Dict[str, Any]) -> str:
    lines = [
        "# E20 Route Decision Packet",
        "",
        f"- recommended_route: {packet['recommended_route']}",
        f"- reason: {packet['reason']}",
        "- real_external_action_executed: false",
        "",
        "## Summary Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in packet["summary_counts"].items())
    lines.extend(["", "## Route Options"])
    lines.extend(f"- {key}: {value}" for key, value in packet["route_options"].items())
    return "\n".join(lines).rstrip() + "\n"
