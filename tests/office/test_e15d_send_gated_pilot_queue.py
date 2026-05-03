from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_draft_only_execution_simulator import build_e15d_draft_only_execution_receipts
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_outbound_safety_guards import build_e15d_outbound_safety_guard_matrix
from office.mission_command.e15d_send_gated_pilot_queue import build_e15d_send_gated_pilot_queue, validate_e15d_send_gated_pilot_queue
from office.mission_command.e15d_ygov_outbound_policy import build_e15d_ygov_outbound_policy


ROOT = Path(__file__).resolve().parents[2]


def queue() -> dict:
    console = load_e15a_console(ROOT)
    envelope = build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))
    policy = build_e15d_ygov_outbound_policy(console, envelope)
    receipts = build_e15d_draft_only_execution_receipts(console, policy)
    guards = build_e15d_outbound_safety_guard_matrix(envelope)
    return build_e15d_send_gated_pilot_queue(console, envelope, policy, receipts, guards)


def test_e15d_send_gated_queue_is_blocked_until_authorized() -> None:
    data = queue()
    assert validate_e15d_send_gated_pilot_queue(data) == []
    assert data["blocked_until_authorized"] is True
    assert len(data["rows"]) == 3


def test_e15d_send_gated_queue_has_idempotency_and_feedback_wait_state() -> None:
    for row in queue()["rows"]:
        assert len(row["idempotency_key"]) == 64
        assert row["authorization_required"] is True
        assert row["feedback_wait_state"] == "pending_valid_send_receipt"
