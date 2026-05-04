from __future__ import annotations

from typing import Any, Dict, List

from .e20_autonomous_execution_eligibility import classify_autonomous_eligibility
from .e20_autonomous_outbound_envelope import build_autonomous_outbound_envelope


def _candidate_action_context(candidate: Dict[str, Any]) -> Dict[str, Any]:
    ready = candidate.get("status") == "ready_for_owner_review"
    return {
        "action_id": candidate.get("action_id"),
        "action_type": "external_validation_message",
        "capability_domain": candidate.get("capability_domain", "external_validation_message"),
        "risk_tier": "T2_low_medium_limited_outbound" if ready else "",
        "target_type": "commercial_validation_candidate",
        "public_private_surface": "external_target_message",
        "reversibility": "stop_future_sends_only",
        "volume": "low",
        "message_sensitivity": "low_transparent_validation",
        "legal_financial_implications": False,
        "payment_or_credential_or_account": False,
        "regulated_content": False,
        "brand_risk": "low",
        "prior_suppression": candidate.get("status") == "suppress_or_do_not_contact",
        "evidence_sufficient": bool(candidate.get("evidence_basis")) and ready,
        "suppression_clear": candidate.get("status") != "suppress_or_do_not_contact",
        "policy_compatible": candidate.get("capability_domain", "external_validation_message") == "external_validation_message",
    }


def build_batch_autonomous_reclassification(batch: Dict[str, Any], provider_capability: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    envelopes: List[Dict[str, Any]] = []
    for candidate in batch.get("candidates", []):
        context = _candidate_action_context(candidate)
        eligibility = classify_autonomous_eligibility(context, provider_capability)
        envelope = build_autonomous_outbound_envelope(candidate, eligibility, provider_capability)
        rows.append(
            {
                "action_id": candidate["action_id"],
                "target_name": candidate["target_name"],
                "candidate_status": candidate["status"],
                "agent_autonomous_send_allowed_in_principle": eligibility["policy_allows_autonomous_in_principle"],
                "current_provider_capability_permits_live": False if eligibility["executor_decision"] == "provider_capability_missing" else provider_capability.get("live_provider_adapter_present", False),
                "owner_approval_truly_required": eligibility["owner_approval_required"],
                "more_evidence_or_message_revision_required": eligibility["evidence_required"],
                "no_go_or_suppression_applies": eligibility["executor_decision"] == "blocked_no_go",
                "classification": (
                    "policy_allows_autonomous_but_provider_missing"
                    if eligibility["executor_decision"] == "provider_capability_missing" and eligibility["policy_allows_autonomous_in_principle"]
                    else "owner_required_due_to_high_risk"
                    if eligibility["owner_approval_required"]
                    else "blocked_due_to_no_go"
                    if eligibility["executor_decision"] == "blocked_no_go"
                    else "evidence_required"
                    if eligibility["evidence_required"]
                    else "autonomous_live_ready"
                    if eligibility["executor_decision"] in {"agent_autonomous_allowed", "agent_autonomous_allowed_with_limits"}
                    else eligibility["executor_decision"]
                ),
                "executor_decision": eligibility["executor_decision"],
                "risk_tier": eligibility["risk_tier"],
                "reason_codes": eligibility["reason_codes"],
                "envelope_id": envelope["envelope_id"],
                "external_action_executed": False,
            }
        )
        envelopes.append(envelope)
    counts = {decision: sum(1 for row in rows if row["executor_decision"] == decision) for decision in [
        "agent_autonomous_allowed",
        "agent_autonomous_allowed_with_limits",
        "owner_approval_required",
        "owner_manual_only",
        "blocked_no_go",
        "provider_capability_missing",
        "evidence_required_before_execution",
    ]}
    return {
        "artifact_id": "e20_batch_autonomous_reclassification",
        "batch_id": batch["batch_id"],
        "summary_counts": counts,
        "rows": rows,
        "autonomous_outbound_envelopes": envelopes,
        "external_action_executed": False,
    }


def render_batch_autonomous_reclassification(data: Dict[str, Any]) -> str:
    lines = [
        "# E20 Batch Autonomous Reclassification",
        "",
        f"- batch_id: {data['batch_id']}",
        "- external_action_executed: false",
        "",
        "## Summary Counts",
    ]
    lines.extend(f"- {key}: {value}" for key, value in data["summary_counts"].items())
    lines.extend(["", "| target | executor decision | classification |", "| --- | --- | --- |"])
    for row in data["rows"]:
        lines.append(f"| {row['target_name']} | {row['executor_decision']} | {row['classification']} |")
    return "\n".join(lines).rstrip() + "\n"
