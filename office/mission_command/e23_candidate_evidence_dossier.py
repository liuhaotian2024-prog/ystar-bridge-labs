from __future__ import annotations

from typing import Any, Dict


def build_candidate_evidence_dossiers(evaluation: Dict[str, Any]) -> Dict[str, Any]:
    dossiers=[]
    for row in evaluation["rows"]:
        dossiers.append({
            "action_id": row["action_id"],
            "target_name": row["target_name"],
            "current_status": row["updated_classification"],
            "evidence_present": row["evidence_present"],
            "evidence_missing": row["evidence_missing"],
            "repo_paths_supporting_present_evidence": row["repo_paths_supporting_present_evidence"],
            "pain_hypothesis": "supported" if row["buyer_pain_hypothesis_supported"] else "missing_or_not_applicable",
            "target_fit": "supported" if row["target_identity_sufficiently_grounded"] else "not_grounded",
            "offer_fit": "supported" if row["offer_fit_supported"] else "not_supported",
            "message_readiness": "adequate" if row["message_specificity_adequate"] else "not_ready",
            "compliance_suppression_status": "suppressed" if row["updated_classification"] == "suppress_or_do_not_contact" else "blocked_missing_source" if row["updated_classification"] == "blocked_missing_source" else "pending",
            "updated_classification": row["updated_classification"],
            "external_action_executed": False,
        })
    return {"artifact_id":"e23_candidate_evidence_dossiers","dossiers":dossiers,"dossier_count":len(dossiers),"external_action_executed":False}
