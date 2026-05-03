from __future__ import annotations

from pathlib import Path

from office.mission_command.e15a_feedback_capture_pack import build_e15a_feedback_capture_form
from office.mission_command.e15a_feedback_signal_evaluator import build_e15a_feedback_signal_evaluation_fixture
from office.mission_command.e15a_ledger_transition_runtime import build_e15a_ledger_state_after_owner_handoff
from office.mission_command.e15a_owner_confirmation_packet import build_e15a_owner_send_confirmation_fixture
from office.mission_command.e15a_owner_execution_console import build_e15a_owner_execution_console
from office.mission_command.e15a_result_packet import build_e15a_result_packet, validate_e15a_result_packet
from office.mission_command.e15a_target_replacement_router import build_e15a_target_replacement_plan


ROOT = Path(__file__).resolve().parents[2]


def result_packet() -> dict:
    console = build_e15a_owner_execution_console(ROOT)
    fixture = build_e15a_owner_send_confirmation_fixture(console)
    ledger = build_e15a_ledger_state_after_owner_handoff(console, fixture)
    form = build_e15a_feedback_capture_form(console)
    signal = build_e15a_feedback_signal_evaluation_fixture()
    replacement = build_e15a_target_replacement_plan(console, fixture)
    return build_e15a_result_packet(
        console=console,
        ledger_state=ledger,
        feedback_form=form,
        signal_fixture=signal,
        replacement_plan=replacement,
    )


def test_e15a_result_packet_defaults_to_owner_send_now() -> None:
    packet = result_packet()
    assert validate_e15a_result_packet(packet) == []
    assert packet["next_route_recommendation"] == "E15A_send_now_owner_operated"
    assert len(packet["ready_for_owner_send_actions"]) == 3


def test_e15a_result_packet_lists_all_next_routes_and_blocks_agent_send() -> None:
    packet = result_packet()
    assert set(packet["routes"]) == {
        "E15A_send_now_owner_operated",
        "E15B_offer_revision_before_send",
        "E15C_expand_target_discovery",
        "E15D_gov_mcp_controlled_execution_pilot",
        "E15E_suppression_and_batch_replacement",
    }
    assert "Aiden autonomous send" in packet["routes"]["E15A_send_now_owner_operated"]["blocked_actions"]
