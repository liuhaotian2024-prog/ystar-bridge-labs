from __future__ import annotations

from pathlib import Path

from office.mission_command.c2_action_queue import build_c2_action_queue
from office.mission_command.c2_constitutional_activation import build_c2_activation_packet
from office.mission_command.c2_ygov_action_decision import evaluate_c2_ygov_action, validate_c2_ygov_decision


ROOT = Path(__file__).resolve().parents[2]


def first_action_packet() -> dict:
    activation = build_c2_activation_packet(ROOT).to_dict()
    queue = build_c2_action_queue(ROOT, activation)
    item = queue["candidates"][0]
    return {
        "action_id": item["action_id"],
        "capability_domain": item["action_domain"],
        "risk_tier": item["risk_tier"],
        "target_class": "ai_consultant_agency",
        "channel": "owner_handoff_or_governed_messaging_adapter",
        "proposed_u": "Prepare one AI-transparent validation message.",
        "evidence_refs": ["e13r_ev_001"],
    }


def test_c2_ygov_blocks_without_activation() -> None:
    decision = evaluate_c2_ygov_action(first_action_packet(), None)
    assert decision.decision == "blocked_by_missing_constitutional_activation"
    assert "missing_constitutional_activation" in decision.reason_codes
    assert validate_c2_ygov_decision(decision) == []


def test_c2_ygov_owner_handoff_only_when_activation_pending() -> None:
    activation = build_c2_activation_packet(ROOT).to_dict()
    decision = evaluate_c2_ygov_action(first_action_packet(), activation)
    assert decision.decision == "owner_handoff_only"
    assert decision.permitted_next_step == "generate_owner_handoff_capsule"
    assert decision.external_action_executed is False


def test_c2_ygov_blocks_hard_gate() -> None:
    activation = build_c2_activation_packet(ROOT).to_dict()
    packet = first_action_packet()
    packet["proposed_u"] = "Make a payment and sign a contract."
    decision = evaluate_c2_ygov_action(packet, activation)
    assert decision.decision == "blocked_by_hard_gate"
    assert decision.permitted_next_step == "owner_escalation_required"


def test_c2_ygov_blocks_scope_mismatch() -> None:
    activation = build_c2_activation_packet(ROOT).to_dict()
    packet = first_action_packet()
    packet["capability_domain"] = "governed_publication"
    decision = evaluate_c2_ygov_action(packet, activation)
    assert decision.decision == "blocked_by_scope_mismatch"


def test_c2_ygov_blocks_missing_evidence() -> None:
    activation = build_c2_activation_packet(ROOT).to_dict()
    packet = first_action_packet()
    packet["evidence_refs"] = []
    decision = evaluate_c2_ygov_action(packet, activation)
    assert decision.decision == "blocked_by_missing_evidence"
