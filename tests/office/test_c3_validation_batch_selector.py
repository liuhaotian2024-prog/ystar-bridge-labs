from __future__ import annotations

from pathlib import Path

from office.mission_command.c3_validation_batch_selector import C3_OFFER, build_c3_validation_batch, validate_c3_validation_batch


ROOT = Path(__file__).resolve().parents[2]


def test_c3_batch_selects_required_roles_from_c2_queue() -> None:
    batch = build_c3_validation_batch(ROOT)
    assert validate_c3_validation_batch(batch) == []
    assert batch["primary_count"] == 3
    assert batch["fallback_count"] == 2
    assert batch["suppression_candidate_count"] == 1
    assert batch["excluded_count"] == 1


def test_c3_batch_binds_offer_and_ids() -> None:
    batch = build_c3_validation_batch(ROOT)
    for action in batch["actions"]:
        assert action["offer_thesis"] == C3_OFFER
        assert action["action_id"]
        assert action["ledger_id"]
        assert action["feedback_event_id"]
        assert action["external_action_executed"] is False


def test_c3_batch_excludes_direct_agent_execution() -> None:
    excluded = [item for item in build_c3_validation_batch(ROOT)["actions"] if item["role"] == "excluded"][0]
    assert excluded["gov_mcp_execution_mode"] == "deny"
    assert "direct agent" in excluded["exclusion_or_suppression_reason"].lower()
