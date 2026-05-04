from __future__ import annotations

from typing import Any, Dict, List

SUPPORTING_PATHS = [
    "operations/external_validation/e18_revenue_validation_batch.json",
    "operations/external_validation/e18_commercial_fit_scores.json",
    "operations/external_validation/e22_dry_run_batch_selection.json",
]


def evaluate_evidence_tightening(e22_selection: Dict[str, Any], e18_batch: Dict[str, Any]) -> Dict[str, Any]:
    candidates = {item["action_id"]: item for item in e18_batch.get("candidates", [])}
    rows: List[Dict[str, Any]] = []
    for excluded in e22_selection.get("excluded_actions_with_reasons", []):
        candidate = candidates.get(excluded["action_id"], {})
        evidence_basis = list(candidate.get("evidence_basis", []))
        missing = list(candidate.get("missing_fields", []))
        suppression_reason = candidate.get("suppression_reason", "")
        if candidate.get("status") == "suppress_or_do_not_contact":
            updated = "suppress_or_do_not_contact"
            missing_evidence = []
            can_promote = False
            reason = "candidate has repo evidence but is reserved/suppressed by existing batch policy"
        elif not evidence_basis or "real_target_not_applicable" in missing:
            updated = "blocked_missing_source"
            missing_evidence = ["real target identity", "repo-grounded source evidence", "buyer pain evidence", "message-specific target fit"]
            can_promote = False
            reason = "not a real customer target and no repo evidence exists"
        else:
            updated = "evidence_required"
            missing_evidence = missing or ["evidence sufficiency not proven"]
            can_promote = False
            reason = "evidence remains insufficient"
        rows.append({
            "action_id": excluded["action_id"],
            "target_name": excluded["target_name"],
            "prior_reasons": excluded["reasons"],
            "evidence_present": evidence_basis,
            "repo_paths_supporting_present_evidence": SUPPORTING_PATHS if evidence_basis else [],
            "evidence_missing": missing_evidence,
            "target_identity_sufficiently_grounded": bool(evidence_basis) and candidate.get("target_id") != "not_applicable_agent_direct_execution",
            "buyer_pain_hypothesis_supported": bool(evidence_basis) and candidate.get("buyer_pain_hypothesis") not in {"", "not_applicable"},
            "message_specificity_adequate": bool(evidence_basis) and updated != "blocked_missing_source",
            "offer_fit_supported": bool(evidence_basis) and candidate.get("offer") == "48h AI Agent Implementation Readiness Review",
            "suppression_or_compliance_can_be_resolved": updated not in {"suppress_or_do_not_contact", "blocked_missing_source"},
            "can_promote_to_dry_run_available": can_promote,
            "updated_classification": updated,
            "decision_reason": reason,
            "suppression_reason": suppression_reason,
            "external_action_executed": False,
        })
    return {
        "artifact_id": "e23_evidence_tightening_evaluation",
        "evidence_required_before": len(e22_selection.get("excluded_actions_with_reasons", [])),
        "promoted_to_dry_run_available": sum(1 for row in rows if row["can_promote_to_dry_run_available"]),
        "still_evidence_required": sum(1 for row in rows if row["updated_classification"] in {"evidence_required", "blocked_missing_source"}),
        "suppressed_or_rejected": sum(1 for row in rows if row["updated_classification"] in {"suppress_or_do_not_contact", "weak_fit_reject", "blocked_missing_source"}),
        "rows": rows,
        "external_action_executed": False,
    }


def render_evidence_tightening(data: Dict[str, Any]) -> str:
    lines=["# E23 Evidence Tightening", "", f"- evidence_required_before: {data['evidence_required_before']}", f"- promoted_to_dry_run_available: {data['promoted_to_dry_run_available']}", f"- still_evidence_required: {data['still_evidence_required']}", f"- suppressed_or_rejected: {data['suppressed_or_rejected']}", "- external_action_executed: false", "", "## Candidate Outcomes"]
    lines.extend(f"- {row['target_name']}: {row['updated_classification']} - {row['decision_reason']}" for row in data["rows"])
    return "\n".join(lines).rstrip()+"\n"
