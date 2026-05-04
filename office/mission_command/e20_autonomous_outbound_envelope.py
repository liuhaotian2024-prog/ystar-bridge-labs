from __future__ import annotations

import hashlib
from typing import Any, Dict


def build_autonomous_outbound_envelope(candidate: Dict[str, Any], eligibility: Dict[str, Any], provider_capability: Dict[str, Any]) -> Dict[str, Any]:
    action_id = str(candidate.get("action_id", "unknown_action"))
    message_seed = f"{action_id}|{candidate.get('target_name')}|{candidate.get('offer')}"
    message_hash = hashlib.sha256(message_seed.encode("utf-8")).hexdigest()
    idempotency_key = hashlib.sha256(f"{action_id}|{message_hash}|e20-autonomous-envelope".encode("utf-8")).hexdigest()
    return {
        "envelope_id": f"e20_autonomous_envelope_{message_hash[:16]}",
        "action_id": action_id,
        "target": candidate.get("target_name"),
        "channel": "future_provider_supported_validation_message",
        "message_content_ref": "E18/E19 approved message variant; not executed in E20",
        "risk_tier": eligibility["risk_tier"],
        "executor_decision": eligibility["executor_decision"],
        "policy_checks": ["Y*gov/gov-mcp compatibility", "AI transparency", "opt-out", "template hash"],
        "evidence_references": list(candidate.get("evidence_basis", [])),
        "guard_checks": ["rate_limit", "idempotency", "suppression", "kill_switch", "audit_receipt"],
        "rate_limit": {"max_actions_per_day": 3, "max_actions_per_target": 1},
        "idempotency_key": idempotency_key,
        "suppression_status": "clear" if "suppression_not_clear" not in eligibility.get("reason_codes", []) else "blocked",
        "provider_capability_status": provider_capability["provider_capability_status"],
        "dry_run_receipt": {
            "receipt_type": "local_no_send_planning_receipt",
            "external_action_executed": False,
            "provider_called": False,
            "real_message_sent": False,
        },
        "live_execution_readiness": "not_live_ready_provider_capability_missing" if eligibility["executor_decision"] == "provider_capability_missing" else "not_executed_in_e20",
        "required_owner_approval_only_if_applicable": eligibility["owner_approval_required"],
        "audit_czl_linkage": "operations/external_validation/e20_czl_closure.json",
        "external_action_executed": False,
    }


def build_autonomous_outbound_envelope_schema() -> Dict[str, Any]:
    return {
        "artifact_id": "e20_autonomous_outbound_envelope_schema",
        "required_fields": [
            "action_id",
            "target",
            "channel",
            "message_content_ref",
            "risk_tier",
            "executor_decision",
            "policy_checks",
            "evidence_references",
            "guard_checks",
            "rate_limit",
            "idempotency_key",
            "suppression_status",
            "provider_capability_status",
            "dry_run_receipt",
            "live_execution_readiness",
            "audit_czl_linkage",
        ],
        "live_execution_forbidden_in_e20": True,
        "external_action_executed": False,
    }
