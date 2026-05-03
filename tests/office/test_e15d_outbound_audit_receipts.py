from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_draft_only_execution_simulator import build_e15d_draft_only_execution_receipts
from office.mission_command.e15d_outbound_audit_receipts import build_e15d_outbound_audit_receipts, validate_e15d_outbound_audit_receipts
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_outbound_safety_guards import build_e15d_outbound_safety_guard_matrix
from office.mission_command.e15d_send_gated_pilot_queue import build_e15d_send_gated_pilot_queue
from office.mission_command.e15d_ygov_outbound_policy import build_e15d_ygov_outbound_policy


ROOT = Path(__file__).resolve().parents[2]


def audit_receipts() -> dict:
    console = load_e15a_console(ROOT)
    envelope = build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))
    policy = build_e15d_ygov_outbound_policy(console, envelope)
    draft = build_e15d_draft_only_execution_receipts(console, policy)
    guards = build_e15d_outbound_safety_guard_matrix(envelope)
    queue = build_e15d_send_gated_pilot_queue(console, envelope, policy, draft, guards)
    return build_e15d_outbound_audit_receipts(queue, envelope, guards)


def test_e15d_audit_receipts_block_pending_authorization() -> None:
    data = audit_receipts()
    assert validate_e15d_outbound_audit_receipts(data) == []
    assert len(data["receipts"]) == 3
    assert data["external_action_executed"] is False


def test_e15d_audit_receipts_have_czl_fields_and_reason_codes() -> None:
    for receipt in audit_receipts()["receipts"]:
        assert receipt["execution_status"] == "blocked_pending_authorization"
        assert "czl_fields" in receipt
        assert "envelope_not_active" in receipt["deterministic_reason_codes"]
