from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping

from office.mission_command.c1_constitutional_envelope import HARD_GATES


DECISIONS = {
    "allow",
    "deny",
    "owner_escalation_required",
    "mcp_execute_allowed",
    "mcp_prepare_only",
    "owner_handoff_only",
    "blocked_by_missing_constitutional_activation",
    "blocked_by_hard_gate",
    "blocked_by_scope_mismatch",
    "blocked_by_missing_evidence",
    "blocked_by_invalid_target",
    "blocked_by_unapproved_external_action",
}


@dataclass(frozen=True)
class C2YGovDecisionEnvelope:
    decision_id: str
    action_id: str
    decision: str
    capability_domain: str
    risk_tier: str
    evidence_basis: List[str]
    owner_boundary_basis: str
    ystar_contract_basis: str
    gov_mcp_contract_basis: str
    permitted_next_step: str
    prohibited_next_steps: List[str]
    reason_codes: List[str] = field(default_factory=list)
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _decision_id(action_id: str, reason_codes: List[str]) -> str:
    digest = hashlib.sha1((action_id + "|" + ",".join(reason_codes)).encode("utf-8")).hexdigest()[:10]
    return f"c2_ygov_decision_{digest}"


def evaluate_c2_ygov_action(
    action_packet: Mapping[str, Any],
    activation_packet: Mapping[str, Any] | None,
) -> C2YGovDecisionEnvelope:
    action_id = str(action_packet.get("action_id") or action_packet.get("intent_id") or "unknown_action")
    capability_domain = str(action_packet.get("capability_domain", ""))
    risk_tier = str(action_packet.get("risk_tier", "unknown"))
    evidence_basis = [str(item) for item in action_packet.get("evidence_refs", []) if item]
    prohibited = [
        "execute_external_action_without_activation",
        "payment",
        "contract",
        "legal_or_financial_commitment",
        "customer_system_access",
        "credential_disclosure",
        "core_brain_cieu_memory_writeback",
    ]

    if activation_packet is None:
        reasons = ["missing_constitutional_activation"]
        return C2YGovDecisionEnvelope(
            _decision_id(action_id, reasons),
            action_id,
            "blocked_by_missing_constitutional_activation",
            capability_domain,
            risk_tier,
            evidence_basis,
            "none",
            "Y-star-gov must validate activation before execution.",
            "gov-mcp must deny execution without activation.",
            "create_owner_handoff_capsule",
            prohibited,
            reasons,
        )

    text = " ".join(str(action_packet.get(key, "")).lower() for key in ["proposed_u", "capability_domain", "channel", "risk_tier"])
    if any(gate in text or gate.replace("_", " ") in text for gate in HARD_GATES):
        reasons = ["owner_hard_gate_detected"]
        return C2YGovDecisionEnvelope(
            _decision_id(action_id, reasons),
            action_id,
            "blocked_by_hard_gate",
            capability_domain,
            risk_tier,
            evidence_basis,
            str(activation_packet.get("source_envelope_id", "unknown")),
            "Y-star-gov escalates payment/legal/customer-system/core-writeback hard gates.",
            "gov-mcp deny/escalate only.",
            "owner_escalation_required",
            prohibited,
            reasons,
        )

    scope = dict(activation_packet.get("scope", {}))
    if capability_domain not in set(scope.get("approved_capability_domains", [])):
        reasons = ["capability_domain_out_of_scope"]
        return C2YGovDecisionEnvelope(
            _decision_id(action_id, reasons),
            action_id,
            "blocked_by_scope_mismatch",
            capability_domain,
            risk_tier,
            evidence_basis,
            str(activation_packet.get("source_envelope_id", "unknown")),
            "Y-star-gov validates domain against constitutional scope.",
            "gov-mcp must deny out-of-scope domain.",
            "revise_action_domain_or_request_envelope_update",
            prohibited,
            reasons,
        )

    target_class = str(action_packet.get("target_class", ""))
    if capability_domain != "publication_draft" and target_class not in set(scope.get("approved_target_classes", [])):
        reasons = ["target_class_out_of_scope"]
        return C2YGovDecisionEnvelope(
            _decision_id(action_id, reasons),
            action_id,
            "blocked_by_invalid_target",
            capability_domain,
            risk_tier,
            evidence_basis,
            str(activation_packet.get("source_envelope_id", "unknown")),
            "Y-star-gov validates target class against constitutional scope.",
            "gov-mcp must deny invalid target class.",
            "revise_target_or_request_target_class_update",
            prohibited,
            reasons,
        )

    if not evidence_basis:
        reasons = ["missing_evidence_basis"]
        return C2YGovDecisionEnvelope(
            _decision_id(action_id, reasons),
            action_id,
            "blocked_by_missing_evidence",
            capability_domain,
            risk_tier,
            evidence_basis,
            str(activation_packet.get("source_envelope_id", "unknown")),
            "Y-star-gov requires evidence refs before external action preparation.",
            "gov-mcp prepare-only until evidence exists.",
            "attach_evidence_refs_before_queueing",
            prohibited,
            reasons,
        )

    if activation_packet.get("owner_approval_present") is not True:
        reasons = ["constitutional_activation_pending", "external_execution_not_approved"]
        return C2YGovDecisionEnvelope(
            _decision_id(action_id, reasons),
            action_id,
            "owner_handoff_only",
            capability_domain,
            risk_tier,
            evidence_basis,
            str(activation_packet.get("source_envelope_id", "unknown")),
            "Y-star-gov can simulate decision but cannot authorize execution before activation.",
            "gov-mcp prepare_only / owner_handoff only.",
            "generate_owner_handoff_capsule",
            prohibited,
            reasons,
        )

    reasons = ["activation_present", "scope_valid", "evidence_basis_present"]
    return C2YGovDecisionEnvelope(
        _decision_id(action_id, reasons),
        action_id,
        "mcp_execute_allowed",
        capability_domain,
        risk_tier,
        evidence_basis,
        str(activation_packet.get("source_envelope_id", "unknown")),
        "Y-star-gov allows execution within activated envelope.",
        "gov-mcp may execute or deny after preflight.",
        "gov_mcp_execution_preflight",
        prohibited,
        reasons,
    )


def validate_c2_ygov_decision(decision: Mapping[str, Any] | C2YGovDecisionEnvelope) -> List[str]:
    data = decision.to_dict() if isinstance(decision, C2YGovDecisionEnvelope) else dict(decision)
    errors: List[str] = []
    if data.get("decision") not in DECISIONS:
        errors.append("invalid_decision")
    for key in ["decision_id", "action_id", "capability_domain", "risk_tier", "ystar_contract_basis", "gov_mcp_contract_basis", "permitted_next_step"]:
        if not data.get(key):
            errors.append(f"missing_{key}")
    if data.get("external_action_executed") is not False:
        errors.append("c2_decision_must_not_execute_external_action")
    if not data.get("reason_codes"):
        errors.append("reason_codes_required")
    return errors
