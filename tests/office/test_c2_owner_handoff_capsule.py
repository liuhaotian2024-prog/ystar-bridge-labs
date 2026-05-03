from __future__ import annotations

from pathlib import Path

from office.mission_command.c2_action_queue import build_c2_action_queue
from office.mission_command.c2_constitutional_activation import build_c2_activation_packet
from office.mission_command.c2_owner_handoff_capsule import (
    build_c2_owner_handoff_capsule,
    render_c2_owner_handoff_capsule,
    validate_c2_owner_handoff_capsule,
)


ROOT = Path(__file__).resolve().parents[2]


def capsule() -> dict:
    queue = build_c2_action_queue(ROOT, build_c2_activation_packet(ROOT).to_dict())
    return build_c2_owner_handoff_capsule(queue).to_dict()


def test_c2_owner_handoff_capsule_has_three_bound_actions() -> None:
    data = capsule()
    assert validate_c2_owner_handoff_capsule(data) == []
    assert len(data["action_capsules"]) == 3
    assert all(item["action_id"] for item in data["action_capsules"])
    assert all(item["decision_id"] for item in data["action_capsules"])
    assert all(item["ledger_id"] for item in data["action_capsules"])
    assert all(item["feedback_event_id"] for item in data["action_capsules"])


def test_c2_owner_handoff_capsule_minimizes_owner_operations() -> None:
    data = capsule()
    assert any("Review and activate" in item for item in data["owner_minimal_operations"])
    assert "Owner is not the operating executor" in data["long_term_direction"]


def test_c2_owner_handoff_capsule_renders_message_and_bound_ids() -> None:
    rendered = render_c2_owner_handoff_capsule(capsule())
    assert "decision_id" in rendered
    assert "ledger_id" in rendered
    assert "feedback_event_id" in rendered
    assert "I am Aiden" in rendered


def test_c2_owner_handoff_capsule_does_not_authorize_external_actions() -> None:
    data = capsule()
    assert data["external_action_executed"] is False
    rendered = render_c2_owner_handoff_capsule(data)
    assert "email/message sending" in rendered
    assert "payment" in rendered
    assert "login" in rendered
