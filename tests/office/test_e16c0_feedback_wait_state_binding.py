from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def feedback() -> dict:
    return json.loads((ROOT / "operations/external_validation/e16c0_feedback_wait_state_binding.json").read_text())


def test_feedback_wait_state_binds_action_ledger_and_feedback_ids() -> None:
    data = feedback()
    assert data["action_id"] == "c2_action_primary_001_cand_alicelabs_alicelabs"
    assert data["ledger_id"] == "ledger_c2_action_primary_001_cand_alicelabs_alicelabs"
    assert data["feedback_event_id"] == "feedback_c2_action_primary_001_cand_alicelabs_alicelabs"
    assert data["feedback_wait_state"] == "pending_valid_send_receipt"


def test_feedback_is_not_fabricated_and_cieu_writeback_remains_blocked() -> None:
    data = feedback()
    assert data["feedback_received"] is False
    assert data["public_evidence_is_not_validation_feedback"] is True
    assert data["owner_reported_feedback_is_provisional_until_provenance_recorded"] is True
    assert data["cieu_core_writeback_allowed"] is False
    assert data["external_action_executed"] is False
