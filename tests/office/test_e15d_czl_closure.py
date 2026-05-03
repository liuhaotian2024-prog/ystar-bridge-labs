from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_czl_closure import build_e15d_czl_closure, validate_e15d_czl_closure
from office.mission_command.e15d_draft_only_execution_simulator import build_e15d_draft_only_execution_receipts
from office.mission_command.e15d_e16_pilot_decision_packet import build_e15d_e16_pilot_decision_packet
from office.mission_command.e15d_gov_mcp_outbound_adapter import build_e15d_gov_mcp_outbound_adapter_contract
from office.mission_command.e15d_outbound_audit_receipts import build_e15d_outbound_audit_receipts
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_outbound_safety_guards import build_e15d_outbound_safety_guard_matrix
from office.mission_command.e15d_send_gated_pilot_queue import build_e15d_send_gated_pilot_queue
from office.mission_command.e15d_ygov_outbound_policy import build_e15d_ygov_outbound_policy


ROOT = Path(__file__).resolve().parents[2]
BASE_HEAD = "663925811432d7667efa291c1f73a9e49b2ac909"


def closure_payload() -> dict:
    console = load_e15a_console(ROOT)
    domain = build_e15d_controlled_outbound_domain(console)
    envelope = build_e15d_outbound_authorization_envelope_request(console, domain)
    policy = build_e15d_ygov_outbound_policy(console, envelope)
    adapter = build_e15d_gov_mcp_outbound_adapter_contract()
    draft = build_e15d_draft_only_execution_receipts(console, policy)
    guards = build_e15d_outbound_safety_guard_matrix(envelope)
    queue = build_e15d_send_gated_pilot_queue(console, envelope, policy, draft, guards)
    audit = build_e15d_outbound_audit_receipts(queue, envelope, guards)
    e16 = build_e15d_e16_pilot_decision_packet(console=console, queue=queue, audit_receipts=audit)
    return build_e15d_czl_closure(
        base_head=BASE_HEAD,
        domain=domain,
        envelope=envelope,
        policy=policy,
        adapter=adapter,
        draft_receipts=draft,
        queue=queue,
        guard_matrix=guards,
        audit_receipts=audit,
        e16_packet=e16,
    ).to_dict()


def test_e15d_czl_closure_reaches_zero_local_residual() -> None:
    closure = closure_payload()
    assert validate_e15d_czl_closure(closure) == []
    assert closure["r_t1"] == 0
    assert closure["y_t1"]["controlled_outbound_pilot_architecture_ready"] is True


def test_e15d_czl_does_not_fake_authorization_or_outbound_action() -> None:
    closure = closure_payload()
    assert closure["x_t"]["owner_authorization_present"] is False
    assert closure["y_t1"]["external_action_executed"] is False
    assert closure["y_t1"]["owner_authorization_faked"] is False
    assert all(value is False for value in closure["no_external_side_effects"].values())
