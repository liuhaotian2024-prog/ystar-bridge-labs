from pathlib import Path

from office.mission_command.e12_offer_learning_update import build_e12_offer_learning_update
from office.mission_command.e12_signal_evaluator import E12SignalEvaluation


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def test_positive_feedback_recommends_e13_only_when_signal_valid():
    update = build_e12_offer_learning_update(E12SignalEvaluation("strong_positive", 1, 0, 0, True, "asks_price"))
    assert update.recommended_next_step == "approve_E13_paid_signal_or_pilot_prep"
    assert update.learning_writeback_allowed is False


def test_negative_or_mixed_feedback_recommends_revision_or_second_batch():
    negative = build_e12_offer_learning_update(E12SignalEvaluation("negative", 0, 1, 0, False, "tools_solve_it"))
    mixed = build_e12_offer_learning_update(E12SignalEvaluation("mixed", 1, 1, 0, False, "mixed"))
    assert negative.recommended_next_step == "revise_offer_and_rerun_validation"
    assert mixed.recommended_next_step == "revise_offer_and_rerun_validation"


def test_no_feedback_keeps_full_mission_rt1_nonzero():
    text = (REPORTS / "e12_czl_closure_report.md").read_text(encoding="utf-8")
    assert "status: BLOCKED_BY_MISSING_E12_OWNER_APPROVAL" in text
    assert "E12 full_mission_rt1: 1" in text
    assert "validation_feedback_or_action_ledger_exists: False" in text


def test_e12_cannot_write_brain_memory_or_core_cieu_db():
    text = (REPORTS / "e12_czl_closure_report.md").read_text(encoding="utf-8")
    assert "core DB/brain/memory/CIEU writeback: false" in text


def test_e12_uses_e11_router_compatible_decisions():
    action_packet = (REPORTS / "e12_validation_action_packet.md").read_text(encoding="utf-8")
    target_preflight = (REPORTS / "e12_target_lifecycle_preflight.md").read_text(encoding="utf-8")
    assert "target_router_state" in action_packet
    assert "action_authorization_allowed" in action_packet
    assert "lifecycle_state: proposed_target_seed" in target_preflight

