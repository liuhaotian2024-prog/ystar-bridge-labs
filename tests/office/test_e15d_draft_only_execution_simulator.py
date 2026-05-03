from __future__ import annotations

from pathlib import Path

from office.mission_command.e15d_controlled_outbound_domain import build_e15d_controlled_outbound_domain, load_e15a_console
from office.mission_command.e15d_draft_only_execution_simulator import (
    build_e15d_draft_only_execution_receipts,
    validate_e15d_draft_only_execution_receipts,
)
from office.mission_command.e15d_outbound_authorization_envelope import build_e15d_outbound_authorization_envelope_request
from office.mission_command.e15d_ygov_outbound_policy import build_e15d_ygov_outbound_policy


ROOT = Path(__file__).resolve().parents[2]


def receipts() -> dict:
    console = load_e15a_console(ROOT)
    envelope = build_e15d_outbound_authorization_envelope_request(console, build_e15d_controlled_outbound_domain(console))
    policy = build_e15d_ygov_outbound_policy(console, envelope)
    return build_e15d_draft_only_execution_receipts(console, policy)


def test_e15d_draft_receipts_cover_primary_actions_without_send() -> None:
    data = receipts()
    assert validate_e15d_draft_only_execution_receipts(data) == []
    assert len(data["receipts"]) == 3
    assert data["external_action_executed"] is False


def test_e15d_draft_receipts_require_owner_authorization_before_send() -> None:
    for receipt in receipts()["receipts"]:
        assert receipt["draft_status"] == "draft_only_simulated"
        assert receipt["send_allowed_now"] is False
        assert receipt["owner_authorization_required"] is True
