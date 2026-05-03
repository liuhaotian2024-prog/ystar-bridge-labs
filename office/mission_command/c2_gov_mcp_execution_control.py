from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


EXECUTION_MODES = [
    "deny",
    "prepare_only",
    "owner_handoff",
    "dry_run_local",
    "pending_owner_approval",
    "mcp_execute_after_activation",
]

ACTUAL_MODES_IN_C2 = {"prepare_only", "dry_run_local", "owner_handoff", "pending_owner_approval", "deny"}


@dataclass(frozen=True)
class C2GovMCPExecutionControl:
    contract_id: str
    action_id: str
    execution_mode: str
    input_packet_schema: List[str]
    execution_preflight: List[str]
    execution_receipt_fields: List[str]
    ledger_write: str
    feedback_wait_state: str
    failure_codes: List[str] = field(default_factory=list)
    result_normalization: List[str] = field(default_factory=list)
    rollback_or_takedown: str = ""
    no_secret_printing: bool = True
    no_credential_disclosure: bool = True
    external_action_executed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def mode_for_ygov_decision(decision: Mapping[str, Any]) -> str:
    decision_value = str(decision.get("decision", ""))
    if decision_value in {"blocked_by_hard_gate", "blocked_by_scope_mismatch", "blocked_by_invalid_target", "blocked_by_missing_evidence"}:
        return "deny"
    if decision_value == "blocked_by_missing_constitutional_activation":
        return "pending_owner_approval"
    if decision_value == "owner_handoff_only":
        return "owner_handoff"
    if decision_value == "mcp_execute_allowed":
        return "mcp_execute_after_activation"
    return "prepare_only"


def build_c2_gov_mcp_execution_control(decision: Mapping[str, Any]) -> C2GovMCPExecutionControl:
    action_id = str(decision.get("action_id", "unknown_action"))
    mode = mode_for_ygov_decision(decision)
    if mode == "mcp_execute_after_activation":
        # C2 does not execute live actions; it only defines the future gov-mcp contract.
        actual_mode = "dry_run_local"
    else:
        actual_mode = mode
    digest = hashlib.sha1((action_id + "|" + actual_mode).encode("utf-8")).hexdigest()[:10]
    return C2GovMCPExecutionControl(
        contract_id=f"c2_gov_mcp_execution_control_{digest}",
        action_id=action_id,
        execution_mode=actual_mode,
        input_packet_schema=[
            "action_intent_packet",
            "ygov_decision_envelope",
            "mcp_execution_contract",
            "execution_preflight",
        ],
        execution_preflight=[
            "validate_ygov_decision_id",
            "validate_constitutional_activation",
            "validate_capability_domain",
            "validate_target_class",
            "validate_message_hash_or_capsule_ref",
            "validate_stop_conditions",
            "validate_no_secret_or_credential_disclosure",
        ],
        execution_receipt_fields=[
            "receipt_id",
            "action_id",
            "execution_mode",
            "executed",
            "result_status",
            "evidence_refs",
            "rollback_or_takedown_ref",
            "residual_candidate",
        ],
        ledger_write="required_after_execution_or_denial_receipt",
        feedback_wait_state="wait_for_owner_or_gov_mcp_feedback_event_after_valid_action",
        failure_codes=[
            "Y_GOV_DENIED",
            "OWNER_ACTIVATION_MISSING",
            "OUT_OF_ENVELOPE",
            "HARD_GATE_ESCALATION",
            "SECRET_OR_CREDENTIAL_DISCLOSURE_BLOCKED",
            "ROLLBACK_PLAN_MISSING",
            "LIVE_EXECUTION_NOT_PERMITTED_IN_C2",
        ],
        result_normalization=[
            "action_id",
            "target_id",
            "capability_domain",
            "execution_mode",
            "executed",
            "result_status",
            "residual_candidate",
        ],
        rollback_or_takedown="required_for_publication_or_account_actions; suppression required for opt-out",
        external_action_executed=False,
    )


def validate_c2_execution_control(control: Mapping[str, Any] | C2GovMCPExecutionControl) -> List[str]:
    data = control.to_dict() if isinstance(control, C2GovMCPExecutionControl) else dict(control)
    errors: List[str] = []
    if data.get("execution_mode") not in EXECUTION_MODES:
        errors.append("invalid_execution_mode")
    if data.get("execution_mode") not in ACTUAL_MODES_IN_C2:
        errors.append("c2_must_not_run_live_mcp_execute_mode")
    if data.get("external_action_executed") is not False:
        errors.append("c2_execution_control_must_not_execute_external_action")
    if data.get("no_secret_printing") is not True:
        errors.append("must_block_secret_printing")
    if data.get("no_credential_disclosure") is not True:
        errors.append("must_block_credential_disclosure")
    for key in ["action_intent_packet", "ygov_decision_envelope", "mcp_execution_contract"]:
        if key not in data.get("input_packet_schema", []):
            errors.append(f"missing_input_schema_{key}")
    return errors
