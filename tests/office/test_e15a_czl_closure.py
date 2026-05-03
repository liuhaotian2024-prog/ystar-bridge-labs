from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_czl_closure import build_e15a_czl_closure, validate_e15a_czl_closure
from office.mission_command.e15a_feedback_capture_pack import build_e15a_feedback_capture_form
from office.mission_command.e15a_feedback_signal_evaluator import build_e15a_feedback_signal_evaluation_fixture
from office.mission_command.e15a_ledger_transition_runtime import build_e15a_ledger_state_after_owner_handoff
from office.mission_command.e15a_owner_confirmation_packet import build_e15a_owner_send_confirmation_fixture
from office.mission_command.e15a_owner_execution_console import build_e15a_owner_execution_console
from office.mission_command.e15a_result_packet import build_e15a_result_packet
from office.mission_command.e15a_target_replacement_router import build_e15a_target_replacement_plan


ROOT = Path(__file__).resolve().parents[2]
BASE_HEAD = "518899d81c8f2612e1ec66c17dfead53dcd6e3e6"


def closure_payload() -> dict:
    console = build_e15a_owner_execution_console(ROOT)
    confirmation = build_e15a_owner_send_confirmation_fixture(console)
    ledger = build_e15a_ledger_state_after_owner_handoff(console, confirmation)
    feedback_form = build_e15a_feedback_capture_form(console)
    signal = build_e15a_feedback_signal_evaluation_fixture()
    replacement = build_e15a_target_replacement_plan(console, confirmation)
    result_packet = build_e15a_result_packet(
        console=console,
        ledger_state=ledger,
        feedback_form=feedback_form,
        signal_fixture=signal,
        replacement_plan=replacement,
    )
    return build_e15a_czl_closure(
        base_head=BASE_HEAD,
        console=console,
        confirmation_fixture=confirmation,
        ledger_state=ledger,
        feedback_form=feedback_form,
        signal_fixture=signal,
        replacement_plan=replacement,
        result_packet=result_packet,
    ).to_dict()


def test_e15a_czl_closure_reaches_zero_local_residual() -> None:
    closure = closure_payload()
    assert validate_e15a_czl_closure(closure) == []
    assert closure["r_t1"] == 0
    assert closure["y_t1"]["owner_execution_package_ready"] is True
    assert closure["y_t1"]["next_route_recommendation"] == "E15A_send_now_owner_operated"


def test_e15a_czl_does_not_fake_sent_feedback_or_external_action() -> None:
    closure = closure_payload()
    assert closure["y_t1"]["external_action_executed_by_agent"] is False
    assert closure["y_t1"]["owner_sent_confirmed"] is False
    assert closure["y_t1"]["feedback_captured"] is False
    assert all(value is False for value in closure["no_external_side_effects"].values())
