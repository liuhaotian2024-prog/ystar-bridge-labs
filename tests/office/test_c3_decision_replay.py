from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_decision_replay import replay_c3_decisions, validate_c3_decision_replay_report
from office.mission_command.c3_narrow_constitutional_envelope import build_c3_narrow_envelope
from office.mission_command.c3_validation_batch_selector import build_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]


def test_c3_decision_replay_covers_full_batch() -> None:
    report = replay_c3_decisions(build_c3_validation_batch(ROOT), build_c3_narrow_envelope(ROOT).to_dict())
    assert validate_c3_decision_replay_report(report) == []
    assert len(report["records"]) == 7
    assert report["all_consistent"] is True


def test_c3_decision_replay_keeps_owner_handoff_only_modes() -> None:
    report = replay_c3_decisions(build_c3_validation_batch(ROOT), build_c3_narrow_envelope(ROOT).to_dict())
    for record in report["records"]:
        assert record["owner_handoff_only"] is True
        assert record["gov_mcp_execution_mode"] in {"owner_handoff", "dry_run_local", "prepare_only", "deny"}
        assert record["external_action_executed"] is False


def test_c3_decision_replay_has_deterministic_reason_codes() -> None:
    report = replay_c3_decisions(build_c3_validation_batch(ROOT), build_c3_narrow_envelope(ROOT).to_dict())
    assert all(record["deterministic_reason_codes"] for record in report["records"])
