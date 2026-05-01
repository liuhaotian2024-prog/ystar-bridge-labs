from pathlib import Path

from office.mission_command.counterfactual_reasoning import (
    build_counterfactual_case,
    build_counterfactual_matrix,
    rank_counterfactual_risks,
)
from office.mission_command.meta_development_method_kernel import build_meta_development_trace


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_counterfactual_case_has_all_required_dimensions():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    case = build_counterfactual_case(trace["top_opportunities"][0], trace["top_opportunities"], trace)
    for field in [
        "do_nothing",
        "wrong_path",
        "alternative_path",
        "capability_failure",
        "buyer_nonexistence",
        "governance_drag",
        "m_triangle_failure",
        "owner_burden_failure",
        "highest_risk_assumption",
        "fastest_disconfirming_test",
        "recommended_adjustment",
    ]:
        assert case[field]


def test_counterfactual_matrix_covers_all_top_opportunities():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    matrix = build_counterfactual_matrix(trace["top_opportunities"], trace)
    assert len(matrix) == len(trace["top_opportunities"])


def test_counterfactual_identifies_buyer_nonexistence_risk():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    matrix = build_counterfactual_matrix(trace["top_opportunities"], trace)
    assert any("buyer" in case["buyer_nonexistence"].lower() for case in matrix)


def test_fastest_disconfirming_test_present():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    matrix = build_counterfactual_matrix(trace["top_opportunities"], trace)
    assert all("48h" in case["fastest_disconfirming_test"] for case in matrix)


def test_counterfactual_can_change_or_confirm_default():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert "default_changed_after_counterfactual" in trace
    assert "why_default_still_wins_or_changed" in trace
    assert trace["default_recommendation"]["title"]


def test_rank_counterfactual_risks_returns_scores():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    ranked = rank_counterfactual_risks(trace["counterfactual_cases"])
    assert ranked[0]["risk_score"] >= ranked[-1]["risk_score"]


def test_no_coo_invented():
    trace = build_meta_development_trace("制定未来 7 天最可能产生第一笔收入的行动方案", REPO_ROOT)
    assert "COO" not in str(trace["counterfactual_cases"])
