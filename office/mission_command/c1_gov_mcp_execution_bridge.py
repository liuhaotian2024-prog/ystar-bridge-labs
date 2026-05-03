from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


FAILURE_CODES = [
    "PACKET_INVALID",
    "Y_GOV_DENIED",
    "Y_GOV_ESCALATED",
    "OUT_OF_ENVELOPE",
    "SECRET_OR_CREDENTIAL_DISCLOSURE_BLOCKED",
    "ROLLBACK_PLAN_MISSING",
    "EXECUTION_NOT_APPROVED_IN_C1",
]


@dataclass(frozen=True)
class C1GovMCPExecutionContract:
    contract_id: str = "c1_gov_mcp_execute_or_deny_contract"
    input_packet: str = "C1ActionIntentPacket + Y*gov decision + constitutional envelope"
    decision_modes: List[str] = field(default_factory=lambda: ["allow", "deny", "escalate"])
    execution_receipt_fields: List[str] = field(default_factory=lambda: ["receipt_id", "action_id", "decision", "executed", "result", "evidence_refs", "rollback_or_takedown_ref"])
    failure_codes: List[str] = field(default_factory=lambda: list(FAILURE_CODES))
    result_normalization: List[str] = field(default_factory=lambda: ["action_id", "domain", "target_class", "channel", "executed", "result_status", "residual_candidate"])
    evidence_capture: str = "Capture only receipt refs, hashes, timestamps, and non-secret evidence refs."
    rollback_or_takedown_required_where_relevant: bool = True
    no_secret_printing: bool = True
    no_credential_disclosure: bool = True
    executes_action_in_this_milestone: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c1_gov_mcp_execution_contract() -> C1GovMCPExecutionContract:
    return C1GovMCPExecutionContract()


def validate_c1_gov_mcp_execution_contract(contract: C1GovMCPExecutionContract | Dict[str, Any]) -> List[str]:
    data = contract.to_dict() if isinstance(contract, C1GovMCPExecutionContract) else dict(contract)
    errors: List[str] = []
    for mode in ["allow", "deny", "escalate"]:
        if mode not in data.get("decision_modes", []):
            errors.append(f"missing_decision_mode_{mode}")
    if data.get("no_secret_printing") is not True:
        errors.append("must_block_secret_printing")
    if data.get("no_credential_disclosure") is not True:
        errors.append("must_block_credential_disclosure")
    if data.get("executes_action_in_this_milestone") is not False:
        errors.append("c1_contract_must_not_execute_action")
    return errors
