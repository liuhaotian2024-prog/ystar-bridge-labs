from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_outbound_authorization_envelope import (
    build_e15d_outbound_authorization_envelope_request,
    validate_e15d_outbound_authorization_envelope_request,
)


ROOT = Path(__file__).resolve().parents[2]


def envelope() -> dict:
    console = load_e15a_console(ROOT)
    return build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))


def test_e15d_envelope_is_request_not_fake_approval() -> None:
    data = envelope()
    assert validate_e15d_outbound_authorization_envelope_request(data) == []
    assert data["status"] == "owner_review_required"
    assert data["owner_authorization_present"] is False
    assert data["send_allowed_now"] is False


def test_e15d_envelope_limits_batch_channels_and_followups() -> None:
    data = envelope()
    assert data["max_actions_per_batch"] == 3
    assert data["max_actions_per_day"] == 1
    assert data["no_follow_up_unless_positive"] is True
    assert "scraped personal contacts" in data["prohibited_target_categories"]
