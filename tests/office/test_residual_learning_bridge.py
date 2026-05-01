from pathlib import Path

from office.mission_command.meta_development_method_kernel import build_meta_development_trace
from office.mission_command.mission_summary import build_mission_summary
from office.mission_command.residual_learning_bridge import build_residual_candidates_for_experiments


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = "制定未来 7 天最可能产生第一笔收入的行动方案"


def test_residual_candidates_are_review_gated():
    trace = build_meta_development_trace(MISSION, REPO_ROOT)
    candidates = build_residual_candidates_for_experiments(trace["experiments"], trace["counterfactual_cases"])
    assert candidates
    assert all(item["review_required"] is True for item in candidates)


def test_residual_candidates_do_not_write_core_db():
    trace = build_meta_development_trace(MISSION, REPO_ROOT)
    candidates = build_residual_candidates_for_experiments(trace["experiments"], trace["counterfactual_cases"])
    assert all(item["writeback_allowed"] is False for item in candidates)


def test_report_contains_counterfactual_stress_test():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Counterfactual Stress Test" in text
    assert "Highest Risk Assumptions" in text


def test_report_contains_obligation_drafts():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Obligation Drafts" in text
    assert "registration_allowed=False" in text


def test_report_contains_residual_candidates():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Residual Learning Candidates" in text
    assert "writeback_allowed=False" in text


def test_no_external_side_effects():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "no external sending" in text


def test_no_core_db_writeback():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "core DB writeback executed" in text


def test_no_coo_invented():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "COO" not in text
