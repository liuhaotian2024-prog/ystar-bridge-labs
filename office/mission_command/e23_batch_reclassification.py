from __future__ import annotations

from typing import Any, Dict


def build_batch_reclassification(e21_reclassification: Dict[str, Any], evaluation: Dict[str, Any], suppression: Dict[str, Any], compliance: Dict[str, Any], promotion_gate: Dict[str, Any], e22_kpi: Dict[str, Any]) -> Dict[str, Any]:
    eval_by_id={row["action_id"]: row for row in evaluation["rows"]}
    suppressed={entry["target_id"] for entry in suppression["entries"]}
    rows=[]
    for row in e21_reclassification["rows"]:
        action_id=row["action_id"]
        eval_row=eval_by_id.get(action_id)
        if eval_row:
            classification=eval_row["updated_classification"]
        elif row.get("dry_run_available"):
            classification="dry_run_available"
        else:
            classification=row.get("classification","evidence_required")
        rows.append({"action_id":action_id,"target_name":row["target_name"],"classification":classification,"dry_run_available":classification=="dry_run_available","dry_run_executed_previously":action_id not in eval_by_id and row.get("dry_run_available",False),"newly_promoted_to_dry_run_available":bool(eval_row and eval_row["can_promote_to_dry_run_available"]),"still_evidence_required":classification in {"evidence_required","blocked_missing_source"},"suppressed":action_id in suppressed or classification=="suppress_or_do_not_contact","compliance_blocked":False,"live_ready":False,"live_blocked_provider_disabled":True,"owner_approval_required_by_risk":row.get("owner_approval_required_by_risk_tier",False),"blocked_no_go":classification in {"blocked_missing_source","weak_fit_reject"},"external_action_executed":False})
    counts={"dry_run_available":sum(1 for r in rows if r["dry_run_available"]),"dry_run_executed_previously":e22_kpi["dry_run_executed_count"],"newly_promoted_to_dry_run_available":sum(1 for r in rows if r["newly_promoted_to_dry_run_available"]),"still_evidence_required":sum(1 for r in rows if r["still_evidence_required"]),"suppressed":sum(1 for r in rows if r["suppressed"]),"compliance_blocked":compliance["compliance_blocked_count"],"live_ready":0,"live_blocked_provider_disabled":len(rows),"owner_approval_required_by_risk":sum(1 for r in rows if r["owner_approval_required_by_risk"]),"blocked_no_go":sum(1 for r in rows if r["blocked_no_go"])}
    return {"artifact_id":"e23_batch_reclassification","rows":rows,"counts":counts,"external_action_executed":False}


def render_batch_reclassification(data: Dict[str, Any]) -> str:
    lines=["# E23 Batch Reclassification", ""]
    lines.extend(f"- {k}: {v}" for k,v in data["counts"].items())
    lines.append("- external_action_executed: false")
    return "\n".join(lines).rstrip()+"\n"
