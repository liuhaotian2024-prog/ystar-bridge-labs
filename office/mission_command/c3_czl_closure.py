from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class C3CZLClosure:
    y_star: str
    x_t: Dict[str, Any]
    u: List[str]
    y_t1: Dict[str, Any]
    r_t1: int
    no_external_side_effects: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c3_czl_closure(
    *,
    base_head: str,
    envelope: Mapping[str, Any],
    batch: Mapping[str, Any],
    replay_report: Mapping[str, Any],
    dry_run_receipts: Mapping[str, Any],
    ledger_fixture: Mapping[str, Any],
    e15_packet: Mapping[str, Any],
) -> C3CZLClosure:
    local_checks_pass = (
        envelope.get("external_action_executed") is False
        and batch.get("external_action_executed") is False
        and replay_report.get("all_consistent") is True
        and dry_run_receipts.get("external_action_executed") is False
        and ledger_fixture.get("external_action_executed") is False
        and e15_packet.get("recommended_route") in {"E15A", "E15B", "E15C", "E15D", "E15E"}
    )
    return C3CZLClosure(
        y_star="C3 narrow constitutional activation plus first governed validation batch control loop reaches owner-handoff readiness without unauthorized external execution.",
        x_t={
            "c2_remote_confirmed_base": base_head,
            "c2_queue_source": "operations/external_validation/c2_governed_action_queue.json",
            "c2_envelope_source": "operations/external_validation/c2_constitutional_activation_packet.json",
            "e14_targets_source": "operations/external_validation/e14_target_batch.proposed.json",
            "owner_approval_evidence_present": envelope.get("owner_approval_evidence_present"),
        },
        u=[
            "narrow_envelope_generation",
            "first_validation_batch_selection",
            "Y_gov_decision_replay",
            "gov_mcp_owner_handoff_execution_package",
            "local_dry_run_execution_receipts",
            "action_ledger_state_machine",
            "feedback_intake_runtime",
            "E15_next_action_decision_packet",
        ],
        y_t1={
            "first_governed_validation_batch_owner_handoff_ready": local_checks_pass,
            "primary_actions": batch.get("primary_count"),
            "fallback_actions": batch.get("fallback_count"),
            "recommended_next_route": e15_packet.get("recommended_route"),
            "external_action_executed": False,
        },
        r_t1=0 if local_checks_pass else 1,
        no_external_side_effects={
            "customer_contact": False,
            "email_or_message_sent": False,
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


def validate_c3_czl_closure(closure: Mapping[str, Any] | C3CZLClosure) -> List[str]:
    data = closure.to_dict() if isinstance(closure, C3CZLClosure) else dict(closure)
    errors: List[str] = []
    if data.get("r_t1") != 0:
        errors.append("c3_residual_not_closed")
    if data.get("y_t1", {}).get("external_action_executed") is not False:
        errors.append("c3_must_not_execute_external_action")
    if any(data.get("no_external_side_effects", {}).values()):
        errors.append("external_side_effect_detected")
    if not data.get("y_star"):
        errors.append("missing_y_star")
    return errors
