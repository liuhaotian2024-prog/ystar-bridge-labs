from __future__ import annotations

from typing import Any, Dict


def build_e21_route_decision(provider_sync: Dict[str, Any], reclassification: Dict[str, Any], promotion_gate: Dict[str, Any]) -> Dict[str, Any]:
    counts = reclassification["summary_counts"]
    if counts["dry_run_available"] and not provider_sync["live_provider_enabled"]:
        recommended = "E22_autonomous_dry_run_batch_execution"
    elif provider_sync["live_provider_enabled"]:
        recommended = "E22_live_provider_adapter_implementation"
    else:
        recommended = "E22_policy_to_provider_alignment_fix"
    return {
        "artifact_id": "e21_route_decision_packet",
        "recommended_route": recommended,
        "secondary_routes": [
            "E22_live_provider_adapter_implementation",
            "E22_evidence_tightening_before_live",
            "keep_live_send_blocked",
        ],
        "why": "gov-mcp now has a disabled-live provider scaffold and dry-run simulator; live send remains blocked until live_ready provider and promotion requirements pass.",
        "dry_run_available_count": counts["dry_run_available"],
        "live_scaffolded_but_disabled_count": counts["live_scaffolded_but_disabled"],
        "evidence_required_count": counts["evidence_required"],
        "promotion_allowed_count": promotion_gate["promotion_allowed_count"],
        "keep_live_send_blocked": True,
        "external_action_executed": False,
    }


def render_route_decision(route: Dict[str, Any]) -> str:
    return "\n".join([
        "# E21 Route Decision Packet",
        "",
        f"- recommended_route: {route['recommended_route']}",
        f"- dry_run_available_count: {route['dry_run_available_count']}",
        f"- live_scaffolded_but_disabled_count: {route['live_scaffolded_but_disabled_count']}",
        f"- evidence_required_count: {route['evidence_required_count']}",
        f"- promotion_allowed_count: {route['promotion_allowed_count']}",
        f"- keep_live_send_blocked: {str(route['keep_live_send_blocked']).lower()}",
        "- external_action_executed: false",
        "",
        route["why"],
    ]).rstrip() + "\n"
