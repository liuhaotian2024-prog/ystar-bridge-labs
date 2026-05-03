from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_draft_only_execution_simulator import build_e15d_draft_only_execution_receipts
from office.mission_command.e15d_e16_pilot_decision_packet import build_e15d_e16_pilot_decision_packet, validate_e15d_e16_pilot_decision_packet
from office.mission_command.e15d_outbound_audit_receipts import build_e15d_outbound_audit_receipts
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_outbound_safety_guards import build_e15d_outbound_safety_guard_matrix
from office.mission_command.e15d_send_gated_pilot_queue import build_e15d_send_gated_pilot_queue
from office.mission_command.e15d_ygov_outbound_policy import build_e15d_ygov_outbound_policy


ROOT = Path(__file__).resolve().parents[2]


def packet() -> dict:
    console = load_e15a_console(ROOT)
    envelope = build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))
    policy = build_e15d_ygov_outbound_policy(console, envelope)
    draft = build_e15d_draft_only_execution_receipts(console, policy)
    guards = build_e15d_outbound_safety_guard_matrix(envelope)
    queue = build_e15d_send_gated_pilot_queue(console, envelope, policy, draft, guards)
    audit = build_e15d_outbound_audit_receipts(queue, envelope, guards)
    return build_e15d_e16_pilot_decision_packet(console=console, queue=queue, audit_receipts=audit)


def test_e15d_e16_packet_recommends_owner_manual_send_first_by_default() -> None:
    data = packet()
    assert validate_e15d_e16_pilot_decision_packet(data) == []
    assert data["recommended_route"] == "E16B_owner_manual_send_first"
    assert data["send_gated_queue_ready_but_blocked"] is True


def test_e15d_e16_packet_lists_send_gated_pilot_but_does_not_default_to_it() -> None:
    data = packet()
    assert "E16C_one_action_send_gated_pilot_after_authorization" in data["routes"]
    assert data["recommended_route"] != "E16C_one_action_send_gated_pilot_after_authorization"
    assert "owner explicitly activates" in data["routes"]["E16C_one_action_send_gated_pilot_after_authorization"]["trigger"]
