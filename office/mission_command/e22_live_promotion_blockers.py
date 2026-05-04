from __future__ import annotations

from typing import Any, Dict, List


def build_live_promotion_blockers(reclassification: Dict[str, Any], provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for row in reclassification["rows"]:
        blockers = ["live_provider_enablement", "provider_credentials_config", "live_provider_tests", "live_audit_receipt_readiness"]
        if row.get("evidence_required"):
            blockers.append("final_evidence_sufficiency")
        if row.get("owner_approval_required_by_risk_tier"):
            blockers.append("owner_approval_required_by_risk_tier")
        rows.append({"action_id": row["action_id"], "target_name": row["target_name"], "live_execution_allowed_now": False, "blockers": blockers, "live_blocked_reason": row.get("live_execution_blocked_reason", provider_sync["live_execution_blocked_reason"]), "external_action_executed": False})
    return {"artifact_id": "e22_live_promotion_blockers", "rows": rows, "live_ready_count": 0, "live_blocked_count": len(rows), "external_action_executed": False}


def render_live_promotion_blockers(data: Dict[str, Any]) -> str:
    lines=["# E22 Live Promotion Blockers","",f"- live_ready_count: {data['live_ready_count']}",f"- live_blocked_count: {data['live_blocked_count']}","- external_action_executed: false","","## Per Action"]
    for row in data["rows"]:
        lines.append(f"- {row['target_name']}: {', '.join(row['blockers'])}")
    return "\n".join(lines).rstrip()+"\n"
