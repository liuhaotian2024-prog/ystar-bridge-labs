from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class C2CZLClosure:
    y_star: str
    x_t: Dict[str, Any]
    u: List[str]
    y_t1: Dict[str, Any]
    r_t1: int
    no_external_side_effects: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_c2_czl_closure(
    *,
    base_head: str,
    activation_packet: Mapping[str, Any],
    action_queue: Mapping[str, Any],
    handoff_capsule: Mapping[str, Any],
    feedback_template_valid: bool,
) -> C2CZLClosure:
    local_checks_pass = (
        bool(activation_packet)
        and len(action_queue.get("candidates", [])) >= 6
        and len(handoff_capsule.get("action_capsules", [])) >= 3
        and feedback_template_valid
        and action_queue.get("external_action_executed") is False
        and handoff_capsule.get("external_action_executed") is False
    )
    return C2CZLClosure(
        y_star="C2 governed first action activation loop produces activation packet, deterministic Y*gov decisions, gov-mcp execution controls, action queue, owner-handoff capsule, local ledger/feedback schema, signal loop, and no unauthorized external side effects.",
        x_t={
            "ab3_c1_base_head": base_head,
            "activation_state": activation_packet.get("activation_state"),
            "selected_targets_source": "operations/external_validation/e14_target_batch.proposed.json",
            "owner_approval_present": activation_packet.get("owner_approval_present"),
            "live_external_execution_approved": activation_packet.get("live_external_execution_approved"),
        },
        u=[
            "activation_packet_generation",
            "Y_gov_decision_envelope_generation",
            "gov_mcp_execution_control_generation",
            "governed_action_queue_generation",
            "owner_handoff_capsule_generation",
            "feedback_ingestion_template_generation",
            "signal_loop_fixture_generation",
        ],
        y_t1={
            "readiness_to_activation_loop_created": local_checks_pass,
            "action_candidate_count": len(action_queue.get("candidates", [])),
            "owner_handoff_action_count": len(handoff_capsule.get("action_capsules", [])),
            "external_action_executed": False,
            "next_stage": "C3 owner activates narrow constitutional envelope, then first governed owner-handoff validation round or gov-mcp controlled action pilot.",
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


def validate_c2_czl_closure(closure: Mapping[str, Any] | C2CZLClosure) -> List[str]:
    data = closure.to_dict() if isinstance(closure, C2CZLClosure) else dict(closure)
    errors: List[str] = []
    if not data.get("y_star"):
        errors.append("missing_y_star")
    if data.get("r_t1") != 0:
        errors.append("c2_local_residual_not_closed")
    if any(data.get("no_external_side_effects", {}).values()):
        errors.append("external_side_effect_detected")
    if data.get("y_t1", {}).get("external_action_executed") is not False:
        errors.append("c2_must_not_execute_external_action")
    return errors
