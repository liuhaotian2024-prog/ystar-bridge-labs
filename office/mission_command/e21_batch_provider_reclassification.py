from __future__ import annotations

from typing import Any, Dict, List


def build_batch_provider_reclassification(e20_reclassification: Dict[str, Any], provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for row in e20_reclassification.get("rows", []):
        evidence_required = row.get("executor_decision") == "evidence_required_before_execution"
        owner_required = bool(row.get("owner_approval_truly_required"))
        dry_run_available = bool(provider_sync.get("dry_run_available")) and not evidence_required
        live_scaffolded_disabled = bool(provider_sync.get("live_scaffold_available")) and not provider_sync.get("live_provider_enabled") and not evidence_required
        if evidence_required:
            classification = "evidence_required_before_execution"
        elif live_scaffolded_disabled:
            classification = "dry_run_available_live_scaffolded_but_disabled"
        elif provider_sync.get("live_provider_enabled"):
            classification = "autonomous_live_ready"
        else:
            classification = "live_provider_missing"
        rows.append(
            {
                "action_id": row["action_id"],
                "target_name": row["target_name"],
                "previous_e20_classification": row["classification"],
                "risk_tier": row["risk_tier"],
                "dry_run_available": dry_run_available,
                "live_scaffolded_but_disabled": live_scaffolded_disabled,
                "live_provider_enabled": bool(provider_sync.get("live_provider_enabled")) and not evidence_required,
                "provider_capability_missing": not provider_sync.get("live_scaffold_available") and not evidence_required,
                "evidence_required": evidence_required,
                "owner_approval_required_by_risk_tier": owner_required,
                "owner_manual_required_due_to_provider_gap": False,
                "classification": classification,
                "live_execution_allowed_now": False,
                "live_execution_blocked_reason": "evidence_required_before_execution" if evidence_required else provider_sync.get("live_execution_blocked_reason"),
                "external_action_executed": False,
            }
        )
    counts = {
        "dry_run_available": sum(1 for row in rows if row["dry_run_available"]),
        "live_scaffolded_but_disabled": sum(1 for row in rows if row["live_scaffolded_but_disabled"]),
        "live_ready": sum(1 for row in rows if row["live_provider_enabled"]),
        "provider_capability_missing": sum(1 for row in rows if row["provider_capability_missing"]),
        "evidence_required": sum(1 for row in rows if row["evidence_required"]),
        "owner_approval_required_by_risk_tier": sum(1 for row in rows if row["owner_approval_required_by_risk_tier"]),
    }
    return {
        "artifact_id": "e21_batch_provider_reclassification",
        "batch_id": e20_reclassification["batch_id"],
        "provider_capability_status": provider_sync["capability_status"],
        "summary_counts": counts,
        "rows": rows,
        "external_action_executed": False,
    }


def render_batch_provider_reclassification(data: Dict[str, Any]) -> str:
    lines = [
        "# E21 Batch Provider Reclassification",
        "",
        f"- batch_id: {data['batch_id']}",
        f"- provider_capability_status: {data['provider_capability_status']}",
        "- external_action_executed: false",
        "",
        "## Summary Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in data["summary_counts"].items())
    lines.extend(["", "| target | classification | live blocked reason |", "| --- | --- | --- |"])
    for row in data["rows"]:
        lines.append(f"| {row['target_name']} | {row['classification']} | {row['live_execution_blocked_reason']} |")
    return "\n".join(lines).rstrip() + "\n"
