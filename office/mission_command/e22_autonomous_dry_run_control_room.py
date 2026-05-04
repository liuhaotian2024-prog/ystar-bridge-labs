from __future__ import annotations

from typing import Any, Dict


def build_autonomous_dry_run_control_room(selection: Dict[str, Any], dry_run_results: Dict[str, Any], ledger: Dict[str, Any], kpi: Dict[str, Any], blockers: Dict[str, Any], route: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "artifact_id": "e22_autonomous_dry_run_control_room",
        "control_room_type": "autonomous_dry_run_batch_execution_surface",
        "dry_run_actions_selected": selection["selected_dry_run_actions"],
        "dry_run_actions_executed": [row for row in dry_run_results["dry_run_results"] if row.get("dry_run_executed")],
        "blocked_actions": [row for row in dry_run_results["dry_run_results"] if not row.get("dry_run_executed")],
        "excluded_evidence_required_actions": [row for row in selection["excluded_actions_with_reasons"] if "evidence_required" in row["reasons"]],
        "dry_run_receipt_ledger_summary": {"dry_run_receipt_count": ledger["dry_run_receipt_count"], "live_receipt_count": ledger["live_receipt_count"]},
        "live_blockers": blockers["rows"],
        "kpi_dry_run_delta": kpi,
        "next_route_recommendation": route.get("recommended_route") if route else "E23_live_provider_enablement_plan",
        "owner_manual_send_is_default": False,
        "external_action_executed": False,
    }


def render_autonomous_dry_run_control_room(room: Dict[str, Any]) -> str:
    lines=["# E22 Autonomous Dry-Run Control Room","",f"- selected: {len(room['dry_run_actions_selected'])}",f"- executed: {len(room['dry_run_actions_executed'])}",f"- blocked: {len(room['blocked_actions'])}",f"- evidence_required_excluded: {len(room['excluded_evidence_required_actions'])}",f"- live_receipt_count: {room['dry_run_receipt_ledger_summary']['live_receipt_count']}",f"- next_route_recommendation: {room['next_route_recommendation']}","- owner_manual_send_is_default: false","- external_action_executed: false"]
    return "\n".join(lines).rstrip()+"\n"
