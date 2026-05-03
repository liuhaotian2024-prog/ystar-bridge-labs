from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping

from office.mission_command.b2r_capability_domains import HARD_OWNER_GATE_DOMAINS, evaluate_capability_action
from office.mission_command.b2r_gov_mcp_execution_contract import build_gov_mcp_execution_contract, validate_gov_mcp_execution_contract
from office.mission_command.b2r_y_gov_action_packet import build_action_packet, validate_action_packet


@dataclass(frozen=True)
class C1EntryDecision:
    ready: bool
    readiness_only: bool
    domain_id: str
    decision: str
    blocked_reason: str
    no_live_action_executed: bool
    action_packet_valid: bool
    gov_mcp_contract_valid: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def evaluate_c1_entry(domain_id: str, envelope: Mapping[str, Any] | None = None) -> C1EntryDecision:
    if envelope is None:
        return C1EntryDecision(False, True, domain_id, "blocked", "missing_valid_envelope", True, False, False)
    if domain_id in HARD_OWNER_GATE_DOMAINS:
        return C1EntryDecision(False, True, domain_id, "blocked", "owner_hard_gate_domain", True, False, False)
    capability = evaluate_capability_action(domain_id, envelope)
    packet = build_action_packet(domain_id)
    contract = build_gov_mcp_execution_contract()
    packet_valid = validate_action_packet(packet) == []
    contract_valid = validate_gov_mcp_execution_contract(contract) == []
    ready = capability.allowed and packet_valid and contract_valid
    blocked_reason = "" if ready else ",".join(capability.reason_codes) or "invalid_contract"
    return C1EntryDecision(
        ready=ready,
        readiness_only=True,
        domain_id=domain_id,
        decision="ready_for_governed_action_cycle" if ready else "blocked",
        blocked_reason=blocked_reason,
        no_live_action_executed=True,
        action_packet_valid=packet_valid,
        gov_mcp_contract_valid=contract_valid,
    )


def build_c1_entry_gate() -> Dict[str, Any]:
    return {
        "gate_id": "b2r_c1_governed_action_entry_gate",
        "status": "readiness_only_no_live_action",
        "supported_readiness_paths": [
            "1-3 AI-transparent validation messages under envelope",
            "low-risk contact form submission under envelope",
            "approved-channel governed publication under envelope",
            "authenticated draft-only action under envelope",
        ],
        "hard_blocks": [
            "payment",
            "contract",
            "legal obligation",
            "financial commitment",
            "customer system access",
            "regulated/government/tax/immigration/identity forms",
            "credential disclosure",
            "core writeback",
            "out-of-envelope action",
        ],
        "action_packet_example": build_action_packet("external_validation_message").to_dict(),
        "gov_mcp_execute_or_deny_contract": build_gov_mcp_execution_contract().to_dict(),
        "action_ledger_schema": {
            "action_id": "required",
            "domain_id": "required",
            "envelope_id": "required",
            "y_gov_validation_ref": "required",
            "gov_mcp_receipt_ref": "required",
            "executed_at": "required_if_executed",
            "result_status": "required",
        },
        "feedback_event_schema": {
            "feedback_event_id": "required",
            "action_id": "required",
            "feedback_source": "owner_or_governed_gateway_recorded",
            "classification": "strong_positive|weak_positive|neutral|negative|invalid_feedback",
        },
        "cieu_residual_semantics": "C1 residual compares expected governed action result with actual action receipt and feedback event; no public evidence becomes validation feedback.",
    }
