from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class E15DCZLClosure:
    y_star: str
    x_t: Dict[str, Any]
    u: List[str]
    y_t1: Dict[str, Any]
    r_t1: int
    no_external_side_effects: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e15d_czl_closure(
    *,
    base_head: str,
    domain: Mapping[str, Any],
    envelope: Mapping[str, Any],
    policy: Mapping[str, Any],
    adapter: Mapping[str, Any],
    draft_receipts: Mapping[str, Any],
    queue: Mapping[str, Any],
    guard_matrix: Mapping[str, Any],
    audit_receipts: Mapping[str, Any],
    e16_packet: Mapping[str, Any],
) -> E15DCZLClosure:
    local_checks_pass = (
        domain.get("external_action_executed") is False
        and envelope.get("external_action_executed") is False
        and envelope.get("owner_authorization_present") is False
        and policy.get("external_action_executed") is False
        and adapter.get("executes_real_external_action_in_e15d") is False
        and draft_receipts.get("external_action_executed") is False
        and queue.get("external_action_executed") is False
        and queue.get("blocked_until_authorized") is True
        and guard_matrix.get("external_action_executed") is False
        and audit_receipts.get("external_action_executed") is False
        and e16_packet.get("external_action_executed") is False
        and e16_packet.get("recommended_route") in {"E16B_owner_manual_send_first", "E16D_expand_evidence_before_send"}
    )
    return E15DCZLClosure(
        y_star="E15D controlled outbound execution pilot architecture is ready for draft-only/send-gated governance without unauthorized outbound execution.",
        x_t={
            "e15a_remote_confirmed_base": base_head,
            "e15a_console_source": "operations/external_validation/e15a_owner_execution_console.json",
            "c3_batch_source": "operations/external_validation/c3_validation_batch.json",
            "governance_contract_sources": ["B2R capability domains", "C2/C3 decision and execution controls"],
            "owner_authorization_present": envelope.get("owner_authorization_present"),
        },
        u=[
            "controlled_outbound_domain",
            "narrow_authorization_envelope_request",
            "Y_gov_outbound_policy",
            "gov_mcp_outbound_adapter_contract",
            "draft_only_execution_receipts",
            "send_gated_pilot_queue",
            "kill_switch_rate_limit_suppression_guards",
            "outbound_audit_receipts",
            "E16_controlled_pilot_decision_packet",
        ],
        y_t1={
            "controlled_outbound_pilot_architecture_ready": local_checks_pass,
            "draft_only_path_ready": True,
            "send_gated_path_ready_but_blocked_until_authorized": queue.get("blocked_until_authorized"),
            "recommended_next_route": e16_packet.get("recommended_route"),
            "external_action_executed": False,
            "owner_authorization_faked": False,
        },
        r_t1=0 if local_checks_pass else 1,
        no_external_side_effects={
            "real_customer_contact": False,
            "real_email_or_message_sent": False,
            "publication": False,
            "payment": False,
            "account_creation": False,
            "form_submission": False,
            "login": False,
            "external_validation_submission": False,
            "customer_system_access": False,
            "legal_or_financial_commitment": False,
            "credential_disclosure": False,
            "core_brain_cieu_memory_writeback": False,
        },
    )


def validate_e15d_czl_closure(closure: Mapping[str, Any] | E15DCZLClosure) -> List[str]:
    data = closure.to_dict() if isinstance(closure, E15DCZLClosure) else dict(closure)
    errors: List[str] = []
    if data.get("r_t1") != 0:
        errors.append("e15d_residual_not_closed")
    if data.get("y_t1", {}).get("external_action_executed") is not False:
        errors.append("e15d_must_not_execute_external_action")
    if data.get("y_t1", {}).get("owner_authorization_faked") is not False:
        errors.append("e15d_must_not_fake_owner_authorization")
    if any(data.get("no_external_side_effects", {}).values()):
        errors.append("external_side_effect_detected")
    return errors
