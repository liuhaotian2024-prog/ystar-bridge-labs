from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_ygov_outbound_policy import build_e15d_ygov_outbound_policy, validate_e15d_ygov_outbound_policy


ROOT = Path(__file__).resolve().parents[2]


def policy() -> dict:
    console = load_e15a_console(ROOT)
    envelope = build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))
    return build_e15d_ygov_outbound_policy(console, envelope)


def test_e15d_policy_replays_three_e15a_actions_without_send() -> None:
    data = policy()
    assert validate_e15d_ygov_outbound_policy(data) == []
    assert len(data["decisions"]) == 3
    assert data["real_send_allowed_now"] is False


def test_e15d_policy_uses_deterministic_reason_codes() -> None:
    decisions = policy()["decisions"]
    for decision in decisions:
        assert decision["decision"] == "send_gated_requires_owner_authorization"
        assert "owner_authorization_envelope_not_active" in decision["deterministic_reason_codes"]
        assert "real_email_or_message_send_now" in decision["prohibited_next_steps"]
