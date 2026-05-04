from __future__ import annotations

from typing import Any, Dict, List


def select_dry_run_actions(e21_reclassification: Dict[str, Any], provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    selected: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    dry_run_capable = bool(provider_sync.get("dry_run_available"))
    for row in e21_reclassification.get("rows", []):
        reasons: list[str] = []
        if not row.get("dry_run_available"):
            reasons.append("not_classified_dry_run_available")
        if row.get("evidence_required"):
            reasons.append("evidence_required")
        if row.get("classification") in {"blocked_no_go", "suppress_or_do_not_contact"}:
            reasons.append("blocked_or_no_go")
        if row.get("suppression_status") == "suppress":
            reasons.append("suppression_active")
        if not dry_run_capable:
            reasons.append("dry_run_provider_capability_missing")
        if row.get("live_provider_enabled"):
            reasons.append("live_provider_not_required_for_dry_run")
        if reasons:
            excluded.append({"action_id": row["action_id"], "target_name": row["target_name"], "reasons": reasons})
        else:
            selected.append({**row, "selection_reason": "dry_run_available_with_evidence_and_provider_dry_run_capability"})
    return {
        "artifact_id": "e22_dry_run_batch_selection",
        "batch_id": e21_reclassification["batch_id"],
        "selected_dry_run_actions": selected,
        "excluded_actions_with_reasons": excluded,
        "selected_count": len(selected),
        "excluded_count": len(excluded),
        "external_action_executed": False,
    }


def render_dry_run_batch_selection(selection: Dict[str, Any]) -> str:
    lines=["# E22 Dry-Run Batch Selection","",f"- selected_count: {selection['selected_count']}",f"- excluded_count: {selection['excluded_count']}","- external_action_executed: false","","## Selected"]
    lines.extend(f"- {row['target_name']}: {row['selection_reason']}" for row in selection["selected_dry_run_actions"])
    lines.extend(["","## Excluded"])
    lines.extend(f"- {row['target_name']}: {', '.join(row['reasons'])}" for row in selection["excluded_actions_with_reasons"])
    return "\n".join(lines).rstrip()+"\n"
