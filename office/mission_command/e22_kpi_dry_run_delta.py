from __future__ import annotations

from typing import Any, Dict


def build_kpi_dry_run_delta(selection: Dict[str, Any], dry_run_results: Dict[str, Any], guard_results: Dict[str, Any], idempotency: Dict[str, Any], suppression: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artifact_id": "e22_kpi_dry_run_delta",
        "dry_run_selected_count": selection["selected_count"],
        "dry_run_executed_count": dry_run_results["dry_run_executed_count"],
        "dry_run_blocked_count": dry_run_results["dry_run_blocked_count"],
        "guard_pass_count": guard_results["guard_pass_count"],
        "guard_block_count": guard_results["guard_block_count"],
        "idempotency_block_count": 1 if idempotency["duplicate_detected"] else 0,
        "suppression_block_count": 1 if suppression["result"] == "blocked_by_suppression_guard" else 0,
        "evidence_block_count": selection["excluded_count"],
        "live_send_count": 0,
        "real_response_count": 0,
        "paid_signal_count": 0,
        "external_action_executed": False,
    }


def render_kpi_dry_run_delta(kpi: Dict[str, Any]) -> str:
    lines=["# E22 KPI Dry-Run Delta", ""]
    for key in ["dry_run_selected_count","dry_run_executed_count","dry_run_blocked_count","guard_pass_count","guard_block_count","idempotency_block_count","suppression_block_count","evidence_block_count","live_send_count","real_response_count","paid_signal_count"]:
        lines.append(f"- {key}: {kpi[key]}")
    lines.append("- external_action_executed: false")
    return "\n".join(lines).rstrip()+"\n"
