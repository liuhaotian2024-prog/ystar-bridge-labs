from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class GovMCPExecutionContract:
    contract_id: str
    tool_gateway_owner: str
    decision_modes: List[str]
    requires_y_gov_validation_ref: bool
    requires_action_ledger: bool
    requires_result_receipt: bool
    executes_live_action_in_b2r: bool
    denied_hard_gate_actions: List[str]
    normalization_fields: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_gov_mcp_execution_contract() -> GovMCPExecutionContract:
    return GovMCPExecutionContract(
        contract_id="b2r_gov_mcp_execute_or_deny_contract",
        tool_gateway_owner="gov-mcp",
        decision_modes=["execute_within_envelope", "deny", "escalate_owner_hard_gate", "dry_run_only"],
        requires_y_gov_validation_ref=True,
        requires_action_ledger=True,
        requires_result_receipt=True,
        executes_live_action_in_b2r=False,
        denied_hard_gate_actions=[
            "payment",
            "contract",
            "legal_obligation",
            "financial_commitment",
            "customer_system_access",
            "regulated_form",
            "credential_disclosure",
            "core_writeback",
        ],
        normalization_fields=[
            "action_id",
            "domain_id",
            "decision",
            "reason_codes",
            "executed",
            "receipt_hash",
            "rollback_or_takedown_ref",
            "cieu_residual_ref",
        ],
    )


def validate_gov_mcp_execution_contract(contract: Mapping[str, Any] | GovMCPExecutionContract) -> List[str]:
    data = contract.to_dict() if isinstance(contract, GovMCPExecutionContract) else dict(contract)
    errors: List[str] = []
    if data.get("tool_gateway_owner") != "gov-mcp":
        errors.append("gov_mcp_must_own_execution_gateway")
    if data.get("requires_y_gov_validation_ref") is not True:
        errors.append("missing_y_gov_validation_requirement")
    if data.get("requires_action_ledger") is not True:
        errors.append("missing_action_ledger_requirement")
    if data.get("executes_live_action_in_b2r") is not False:
        errors.append("b2r_must_not_execute_live_action")
    if "execute_within_envelope" not in data.get("decision_modes", []):
        errors.append("missing_execute_within_envelope_mode")
    return errors
