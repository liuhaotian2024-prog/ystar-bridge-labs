from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Mapping


@dataclass(frozen=True)
class E15ACZLClosure:
    y_star: str
    x_t: Dict[str, Any]
    u: List[str]
    y_t1: Dict[str, Any]
    r_t1: int
    no_external_side_effects: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_e15a_czl_closure(
    *,
    base_head: str,
    console: Mapping[str, Any],
    confirmation_fixture: Mapping[str, Any],
    ledger_state: Mapping[str, Any],
    feedback_form: Mapping[str, Any],
    signal_fixture: Mapping[str, Any],
    replacement_plan: Mapping[str, Any],
    result_packet: Mapping[str, Any],
) -> E15ACZLClosure:
    local_checks_pass = (
        console.get("external_action_executed_by_agent") is False
        and confirmation_fixture.get("external_action_executed_by_agent") is False
        and confirmation_fixture.get("sent_confirmed_by_owner") is False
        and ledger_state.get("external_action_executed_by_agent") is False
        and ledger_state.get("sent_confirmed_by_owner") is False
        and feedback_form.get("external_action_executed_by_agent") is False
        and replacement_plan.get("external_action_executed_by_agent") is False
        and result_packet.get("external_action_executed_by_agent") is False
        and result_packet.get("next_route_recommendation") == "E15A_send_now_owner_operated"
    )
    return E15ACZLClosure(
        y_star="E15A owner-operated first validation execution and feedback capture loop is ready without agent external execution or fake sent/feedback state.",
        x_t={
            "c3_remote_confirmed_base": base_head,
            "c3_owner_handoff_batch_source": "operations/external_validation/c3_owner_handoff_validation_batch.json",
            "c3_validation_batch_source": "operations/external_validation/c3_validation_batch.json",
            "owner_sent_confirmation_present": confirmation_fixture.get("sent_confirmed_by_owner"),
            "feedback_received": False,
        },
        u=[
            "owner_execution_console_generation",
            "owner_confirmation_packet_generation",
            "ledger_transition_to_waiting_owner_send",
            "feedback_capture_form_generation",
            "feedback_signal_fixture_generation",
            "target_replacement_router_generation",
            "E15A_result_packet_generation",
        ],
        y_t1={
            "owner_execution_package_ready": local_checks_pass,
            "feedback_loop_ready": bool(feedback_form.get("valid_actions")),
            "next_route_recommendation": result_packet.get("next_route_recommendation"),
            "external_action_executed_by_agent": False,
            "owner_sent_confirmed": False,
            "feedback_captured": False,
        },
        r_t1=0 if local_checks_pass else 1,
        no_external_side_effects={
            "customer_contact_by_agent": False,
            "email_or_message_sent_by_agent": False,
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


def validate_e15a_czl_closure(closure: Mapping[str, Any] | E15ACZLClosure) -> List[str]:
    data = closure.to_dict() if isinstance(closure, E15ACZLClosure) else dict(closure)
    errors: List[str] = []
    if data.get("r_t1") != 0:
        errors.append("e15a_residual_not_closed")
    if data.get("y_t1", {}).get("external_action_executed_by_agent") is not False:
        errors.append("e15a_must_not_execute_agent_external_action")
    if data.get("y_t1", {}).get("owner_sent_confirmed") is not False:
        errors.append("e15a_must_not_fake_owner_sent")
    if data.get("y_t1", {}).get("feedback_captured") is not False:
        errors.append("e15a_must_not_fake_feedback")
    if any(data.get("no_external_side_effects", {}).values()):
        errors.append("external_side_effect_detected")
    return errors
