from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_decision_replay import replay_c3_decisions
from office.mission_command.c3_dry_run_execution_receipts import build_c3_dry_run_receipts, validate_c3_dry_run_receipts
from office.mission_command.c3_narrow_constitutional_envelope import build_c3_narrow_envelope
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]


def receipts() -> dict:
    batch = build_c3_validation_batch(ROOT)
    replay = replay_c3_decisions(batch, build_c3_narrow_envelope(ROOT).to_dict())
    return build_c3_dry_run_receipts(batch, replay)


def test_c3_dry_run_receipts_cover_non_excluded_actions() -> None:
    data = receipts()
    assert validate_c3_dry_run_receipts(data) == []
    assert len(data["receipts"]) == 6


def test_c3_dry_run_receipts_do_not_execute_external_action() -> None:
    for receipt in receipts()["receipts"]:
        assert receipt["external_action_executed"] is False
        assert "email_message_sent" in receipt["prohibited_external_outputs"]
        assert receipt["dry_run_status"] == "completed_control_plane_only"
