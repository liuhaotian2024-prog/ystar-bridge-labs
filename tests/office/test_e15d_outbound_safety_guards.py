from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_outbound_safety_guards import (
    build_e15d_outbound_safety_guard_matrix,
    evaluate_e15d_guard_results,
    validate_e15d_outbound_safety_guard_matrix,
)


ROOT = Path(__file__).resolve().parents[2]


def setup() -> tuple[dict, dict, dict]:
    console = load_e15a_console(ROOT)
    envelope = build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))
    matrix = build_e15d_outbound_safety_guard_matrix(envelope)
    return console, envelope, matrix


def test_e15d_guard_matrix_has_kill_rate_suppression_and_envelope_guards() -> None:
    _, _, matrix = setup()
    assert validate_e15d_outbound_safety_guard_matrix(matrix) == []
    for guard in ["global_kill_switch", "target_suppression", "max_actions_per_day", "no_send_if_envelope_not_active"]:
        assert guard in matrix["guards"]


def test_e15d_guard_results_block_inactive_envelope_send() -> None:
    console, envelope, matrix = setup()
    result = evaluate_e15d_guard_results(console["primary_actions"][0], envelope, matrix)
    assert result["preflight_result"] == "blocked"
    assert "no_send_if_envelope_not_active" in result["failed_guards"]
    assert result["send_allowed_now"] is False
