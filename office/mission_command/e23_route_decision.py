from __future__ import annotations

from typing import Any, Dict


def build_e23_route_decision(kpi: Dict[str, Any], promotion: Dict[str, Any], provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    if not provider_sync.get("live_provider_enabled"):
        route="E24_live_provider_sandbox_enablement"
    elif kpi["still_evidence_required"]:
        route="E24_evidence_expansion_before_live"
    else:
        route="E24_one_action_live_canary_plan"
    return {"artifact_id":"e23_route_decision_packet","recommended_route":route,"secondary_routes":["E24_suppression_compliance_hardening","E24_provider_policy_alignment_fix","E24_autonomous_dry_run_iteration_2","keep_live_send_blocked"],"why":"Evidence/compliance gates are defined, but live provider remains disabled and live tests/config/persistence are missing.","live_ready_count":promotion["counts"]["live_ready"],"live_blocked_provider_disabled":promotion["counts"]["live_blocked_provider_disabled"],"keep_live_send_blocked":True,"external_action_executed":False}

def render_route_decision(route: Dict[str, Any]) -> str:
    return "\n".join(["# E23 Route Decision Packet","",f"- recommended_route: {route['recommended_route']}",f"- live_ready_count: {route['live_ready_count']}",f"- live_blocked_provider_disabled: {route['live_blocked_provider_disabled']}",f"- keep_live_send_blocked: {str(route['keep_live_send_blocked']).lower()}","- external_action_executed: false", "", route["why"]]).rstrip()+"\n"
