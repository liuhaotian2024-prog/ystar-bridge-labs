from __future__ import annotations

from pathlib import Path

from office.mission_command.c2_action_queue import C2_OFFER_THESIS, build_c2_action_queue, load_e14_selected_targets, validate_c2_action_queue
from office.mission_command.c2_constitutional_activation import build_c2_activation_packet


ROOT = Path(__file__).resolve().parents[2]


def queue() -> dict:
    return build_c2_action_queue(ROOT, build_c2_activation_packet(ROOT).to_dict())


def test_c2_reads_e14_selected_targets() -> None:
    targets = load_e14_selected_targets(ROOT)
    assert len(targets) >= 3
    assert {target["target_id"] for target in targets[:3]} >= {
        "cand_alicelabs_alicelabs",
        "cand_botsquash_botsquash",
        "cand_wotai_wotai",
    }


def test_c2_action_queue_has_primary_and_fallback_candidates() -> None:
    data = queue()
    assert data["primary_candidate_count"] == 3
    assert data["fallback_candidate_count"] == 3
    assert validate_c2_action_queue(data) == []


def test_c2_action_queue_binds_offer_and_decisions() -> None:
    for candidate in queue()["candidates"]:
        assert candidate["offer_thesis"] == C2_OFFER_THESIS
        assert candidate["ygov_decision"]["decision"] == "owner_handoff_only"
        assert candidate["gov_mcp_execution_mode"] == "owner_handoff"
        assert candidate["external_action_executed"] is False


def test_c2_action_queue_has_ledger_and_feedback_paths() -> None:
    candidate = queue()["candidates"][0]
    assert candidate["ledger_placeholder"]["action_id"] == candidate["action_id"]
    assert candidate["feedback_wait_condition"]
    assert "positive" in candidate["next_if_positive_response"]
    assert "negative" in candidate["next_if_negative_response"]


def test_c2_action_queue_message_capsule_is_not_sent() -> None:
    capsule = queue()["candidates"][0]["action_copy_or_message_capsule"]
    assert capsule["ai_transparency_required"] is True
    assert capsule["opt_out_required"] is True
    assert capsule["send_now"] is False
