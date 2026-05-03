from __future__ import annotations

from pathlib import Path

from office.mission_command.c2_constitutional_activation import (
    HARD_GATES,
    build_c2_activation_packet,
    validate_c2_activation_packet,
)


ROOT = Path(__file__).resolve().parents[2]


def test_c2_builds_pending_activation_from_c1_request() -> None:
    packet = build_c2_activation_packet(ROOT)
    assert packet.status == "owner_review_required"
    assert packet.activation_state == "pending_owner_activation"
    assert packet.owner_approval_present is False
    assert packet.live_external_execution_approved is False
    assert validate_c2_activation_packet(packet) == []


def test_c2_activation_keeps_owner_hard_gates() -> None:
    gates = set(build_c2_activation_packet(ROOT).owner_hard_gates)
    for gate in HARD_GATES:
        assert gate in gates


def test_c2_activation_allows_local_preparation_without_execution() -> None:
    packet = build_c2_activation_packet(ROOT)
    assert "decision_simulation" in packet.allowed_without_activation
    assert "owner_handoff_capsule_generation" in packet.allowed_without_activation
    assert packet.external_action_executed is False


def test_c2_activation_models_progressive_domains_not_global_hard_block() -> None:
    domains = set(build_c2_activation_packet(ROOT).progressive_action_domains)
    assert "login_proposal" in domains
    assert "form_preparation_proposal" in domains
    assert "low_risk_publication_draft_preparation" in domains
    assert "account_creation_proposal" in domains
