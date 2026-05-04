from __future__ import annotations

from typing import Any, Dict


def build_promotion_readiness_gate(e21_reclassification: Dict[str, Any], suppression: Dict[str, Any], compliance: Dict[str, Any], provider_sync: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    suppressed_ids={entry["target_id"] for entry in suppression["entries"]}
    eval_by_id={row["action_id"]: row for row in evaluation["rows"]}
    rows=[]
    for row in e21_reclassification["rows"]:
        action_id=row["action_id"]
        eval_row=eval_by_id.get(action_id,{})
        statuses=[]
        if not provider_sync.get("live_provider_enabled"):
            statuses.append("live_blocked_provider_disabled")
        if row.get("evidence_required") or eval_row.get("updated_classification") == "blocked_missing_source":
            statuses.append("live_blocked_evidence_required")
        if action_id in suppressed_ids or eval_row.get("updated_classification") == "suppress_or_do_not_contact":
            statuses.append("live_blocked_suppression")
        if compliance["compliance_blocked_count"]:
            statuses.append("live_blocked_compliance")
        statuses.extend(["live_blocked_missing_live_tests","live_blocked_idempotency"])
        if row.get("owner_approval_required_by_risk_tier"):
            statuses.append("live_blocked_owner_approval_required_by_risk")
        statuses=list(dict.fromkeys(statuses))
        rows.append({"action_id":action_id,"target_name":row["target_name"],"live_ready":False,"statuses":statuses,"primary_status":statuses[0] if statuses else "live_ready","external_action_executed":False})
    counts={"live_ready":0,"live_blocked_provider_disabled":sum(1 for r in rows if "live_blocked_provider_disabled" in r["statuses"]),"live_blocked_evidence_required":sum(1 for r in rows if "live_blocked_evidence_required" in r["statuses"]),"live_blocked_suppression":sum(1 for r in rows if "live_blocked_suppression" in r["statuses"]),"live_blocked_compliance":sum(1 for r in rows if "live_blocked_compliance" in r["statuses"]),"live_blocked_missing_live_tests":sum(1 for r in rows if "live_blocked_missing_live_tests" in r["statuses"]),"live_blocked_owner_approval_required_by_risk":sum(1 for r in rows if "live_blocked_owner_approval_required_by_risk" in r["statuses"]),"live_blocked_no_go":0}
    return {"artifact_id":"e23_promotion_readiness_gate","counts":counts,"rows":rows,"external_action_executed":False}


def render_promotion_readiness_gate(gate: Dict[str, Any]) -> str:
    lines=["# E23 Promotion Readiness Gate", ""]
    lines.extend(f"- {k}: {v}" for k,v in gate["counts"].items())
    lines.append("- external_action_executed: false")
    lines.extend(["","## Per Action"])
    lines.extend(f"- {row['target_name']}: {', '.join(row['statuses'])}" for row in gate["rows"])
    return "\n".join(lines).rstrip()+"\n"
