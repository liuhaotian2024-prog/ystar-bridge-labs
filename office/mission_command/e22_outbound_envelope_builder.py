from __future__ import annotations

import hashlib
from typing import Any, Dict, List

CANONICAL_RISK_TIER = "TIER_2_TRANSPARENT_LOW_RISK_EXTERNAL_VALIDATION"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_outbound_envelopes(selection: Dict[str, Any], e20_reclassification: Dict[str, Any]) -> Dict[str, Any]:
    e20_envelopes = {env["action_id"]: env for env in e20_reclassification.get("autonomous_outbound_envelopes", [])}
    envelopes: List[Dict[str, Any]] = []
    for row in selection["selected_dry_run_actions"]:
        prior = e20_envelopes.get(row["action_id"], {})
        message_ref = prior.get("message_content_ref", "E18/E19 approved message variant; not executed")
        message_hash = _hash(f"{row['action_id']}:{message_ref}")[:32]
        idem = "idem_" + _hash(f"{row['action_id']}:{message_hash}:e22_dry_run")[:32]
        envelopes.append({
            "envelope_id": "e22_dry_run_envelope_" + _hash(row["action_id"])[:16],
            "action_id": row["action_id"],
            "target_id": prior.get("target", row["target_name"]).lower().replace(" ", "_").replace("/", "_"),
            "target_name": row["target_name"],
            "channel": "gov_mcp_dry_run_validation_message",
            "message_content_ref": message_ref,
            "message_hash": message_hash,
            "risk_tier": CANONICAL_RISK_TIER,
            "executor_decision": "agent_autonomous_dry_run",
            "provider_mode": "dry_run",
            "capability_domain": "external_validation_message",
            "evidence_references": prior.get("evidence_references", []),
            "guard_requirements": ["risk_tier", "policy_compatibility", "provider_capability", "dry_run_mode", "rate_limit", "idempotency", "suppression", "evidence", "message_safety", "owner_approval_if_required_by_risk_tier"],
            "idempotency_key": idem,
            "suppression_status": prior.get("suppression_status", "clear"),
            "rate_limit_bucket": {"bucket_id": "e22_autonomous_dry_run_batch", "max_actions": 5, "window": "local_batch"},
            "audit_czl_reference": "operations/external_validation/e22_czl_closure.json",
            "live_execution_disabled": True,
            "owner_approval_required_by_risk_tier": row.get("owner_approval_required_by_risk_tier", False),
            "external_action_executed": False,
        })
    return {"artifact_id": "e22_outbound_envelopes", "envelopes": envelopes, "envelope_count": len(envelopes), "external_action_executed": False}
