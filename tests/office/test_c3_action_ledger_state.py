from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_action_ledger_state import (
    C3_AUTO_STATES,
    build_c3_action_ledger_state_fixture,
    build_c3_action_ledger_state_template,
    validate_c3_action_ledger_state_fixture,
)
from office.mission_command.c3_decision_replay import replay_c3_decisions
from office.mission_command.c3_dry_run_execution_receipts import build_c3_dry_run_receipts
from office.mission_command.c3_narrow_constitutional_envelope import build_c3_narrow_envelope
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]


def fixture() -> dict:
    batch = build_c3_validation_batch(ROOT)
    receipts = build_c3_dry_run_receipts(batch, replay_c3_decisions(batch, build_c3_narrow_envelope(ROOT).to_dict()))
    return build_c3_action_ledger_state_fixture(batch, receipts)


def test_c3_ledger_state_template_has_owner_confirmation_gates() -> None:
    template = build_c3_action_ledger_state_template()
    assert "sent_confirmed_by_owner" in template["owner_confirmation_required_for"]
    assert template["no_fake_sent"] is True


def test_c3_ledger_fixture_only_uses_auto_states() -> None:
    data = fixture()
    assert validate_c3_action_ledger_state_fixture(data) == []
    assert all(row["state"] in C3_AUTO_STATES for row in data["rows"])
    assert all(row["sent_confirmed_by_owner"] is False for row in data["rows"])
