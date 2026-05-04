from __future__ import annotations

from typing import Any, Dict

SUPPRESSION_REASONS=["do_not_contact","bounced_or_invalid","unsubscribe","negative_response","legal_hold","sensitive_target","duplicate_target","manual_owner_suppression","compliance_blocked","unknown_status"]
SCOPES=["target_only","domain","organization","channel","campaign"]


def build_suppression_registry_schema() -> Dict[str, Any]:
    return {"artifact_id":"e23_suppression_registry_schema","supported_reasons":SUPPRESSION_REASONS,"supported_scopes":SCOPES,"required_fields":["target_id","suppression_reason","source_evidence","generated_at","scope","expiry_or_permanence","override_policy"],"owner_override_required_only_when_risk_policy_requires_it":True,"external_action_executed":False}


def build_suppression_registry(dossiers: Dict[str, Any]) -> Dict[str, Any]:
    entries=[]
    for dossier in dossiers["dossiers"]:
        if dossier["updated_classification"] == "suppress_or_do_not_contact":
            entries.append({"target_id":dossier["action_id"],"target_name":dossier["target_name"],"suppression_reason":"manual_owner_suppression","source_evidence":"operations/external_validation/e18_revenue_validation_batch.json","generated_at":"2026-05-04T00:00:00Z","scope":"target_only","expiry_or_permanence":"until_owner_explicitly_reactivates_candidate","override_policy":"risk_policy_check_required_before_override","real_suppression_evidence_fabricated":False})
    return {"artifact_id":"e23_suppression_registry","entries":entries,"production_suppressed_target_count":len(entries),"schema_ref":"operations/external_validation/e23_suppression_registry_schema.json","template_examples_included":False,"external_action_executed":False}
