from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_narrow_constitutional_envelope import (
    C3_EXCLUDED_SCOPE,
    build_c3_narrow_envelope,
    validate_c3_narrow_envelope,
)


ROOT = Path(__file__).resolve().parents[2]


def test_c3_narrow_envelope_is_owner_handoff_only_not_approval() -> None:
    envelope = build_c3_narrow_envelope(ROOT)
    assert envelope.status == "locally_activated_for_owner_handoff_only"
    assert envelope.owner_approval_evidence_present is False
    assert envelope.agent_direct_execution_allowed is False
    assert envelope.external_action_executed is False
    assert validate_c3_narrow_envelope(envelope) == []


def test_c3_narrow_envelope_covers_only_validation_handoff_scope() -> None:
    envelope = build_c3_narrow_envelope(ROOT).to_dict()
    assert envelope["scope"]["approved_capability_domains"] == ["external_validation_message"]
    assert set(envelope["allowed_execution_modes"]) == {"owner_handoff", "dry_run_local"}
    for item in C3_EXCLUDED_SCOPE:
        assert item in envelope["excluded_scope"]


def test_c3_narrow_envelope_does_not_permanently_hard_block_proposals() -> None:
    envelope = build_c3_narrow_envelope(ROOT)
    assert "low_risk_validation_messaging" in envelope.allowed_scope
    assert "feedback_intake" in envelope.allowed_scope
    assert "signal_evaluation" in envelope.allowed_scope
