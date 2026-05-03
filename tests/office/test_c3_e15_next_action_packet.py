from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_decision_replay import replay_c3_decisions
from office.mission_command.c3_e15_next_action_packet import build_c3_e15_next_action_packet, validate_c3_e15_next_action_packet
from office.mission_command.c3_feedback_intake_runtime import build_c3_feedback_signal_fixture
from office.mission_command.c3_narrow_constitutional_envelope import build_c3_narrow_envelope
from office.mission_command.c3_owner_handoff_execution_batch import build_c3_owner_handoff_batch
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]


def packet() -> dict:
    batch = build_c3_validation_batch(ROOT)
    replay = replay_c3_decisions(batch, build_c3_narrow_envelope(ROOT).to_dict())
    handoff = build_c3_owner_handoff_batch(batch)
    return build_c3_e15_next_action_packet(batch=batch, replay_report=replay, handoff_batch=handoff, feedback_fixture=build_c3_feedback_signal_fixture())


def test_c3_e15_packet_recommends_route_and_lists_all_options() -> None:
    data = packet()
    assert validate_c3_e15_next_action_packet(data) == []
    assert data["recommended_route"] == "E15A"
    assert set(data["routes"]) == {"E15A", "E15B", "E15C", "E15D", "E15E"}


def test_c3_e15_packet_blocks_unapproved_actions() -> None:
    route = packet()["routes"]["E15A"]
    assert "Aiden autonomous send" in route["blocked_actions"]
    assert "payment" in route["blocked_actions"]
    assert route["expected_next_repository_milestone"] == "E15A_owner_handoff_validation_execution"
