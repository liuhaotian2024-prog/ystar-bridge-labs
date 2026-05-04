from __future__ import annotations

from typing import Any, Dict


def build_provider_promotion_gate(provider_sync: Dict[str, Any], reclassification: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    for row in reclassification["rows"]:
        promotion_allowed = bool(row["live_provider_enabled"] and not row["evidence_required"] and not row["owner_approval_required_by_risk_tier"])
        reason_codes = []
        if row["evidence_required"]:
            reason_codes.append("target_evidence_required")
        if not provider_sync["live_provider_enabled"]:
            reason_codes.append(provider_sync["live_execution_blocked_reason"])
        if row["owner_approval_required_by_risk_tier"]:
            reason_codes.append("owner_approval_required_by_risk_tier")
        rows.append({
            "action_id": row["action_id"],
            "target_name": row["target_name"],
            "promotion_allowed": promotion_allowed,
            "dry_run_required": True,
            "provider_live_ready_required": True,
            "provider_tests_required": True,
            "rate_limit_required": True,
            "idempotency_required": True,
            "suppression_clear_required": True,
            "audit_receipt_required": True,
            "owner_approval_only_if_required_by_risk_tier": True,
            "reason_codes": reason_codes or ["promotion_gate_passed"],
            "external_action_executed": False,
        })
    return {
        "artifact_id": "e21_provider_promotion_gate",
        "contract_id": "e21_dry_run_to_live_provider_promotion_gate",
        "promotion_allowed_count": sum(1 for row in rows if row["promotion_allowed"]),
        "promotion_blocked_count": sum(1 for row in rows if not row["promotion_allowed"]),
        "rows": rows,
        "live_execution_enabled_in_e21": False,
        "external_action_executed": False,
    }


def render_provider_promotion_gate(data: Dict[str, Any]) -> str:
    lines = [
        "# E21 Provider Promotion Gate",
        "",
        f"- promotion_allowed_count: {data['promotion_allowed_count']}",
        f"- promotion_blocked_count: {data['promotion_blocked_count']}",
        f"- live_execution_enabled_in_e21: {str(data['live_execution_enabled_in_e21']).lower()}",
        "- external_action_executed: false",
        "",
        "## Blockers",
    ]
    for row in data["rows"]:
        lines.append(f"- {row['target_name']}: {', '.join(row['reason_codes'])}")
    return "\n".join(lines).rstrip() + "\n"
