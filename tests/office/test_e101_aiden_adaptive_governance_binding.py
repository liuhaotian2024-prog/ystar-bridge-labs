from pathlib import Path

from office.aiden_meeting_room.aiden_response_engine import (
    answer_owner,
    build_aiden_adaptive_governance_result,
    build_aiden_answer_owner_action_context,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_fastest_cash_answer_is_adaptive_governance_gated(tmp_path):
    text = answer_owner(
        "Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？",
        repo_root=REPO_ROOT,
        memory_path=tmp_path / "memory.json",
    )

    assert "Adaptive Governance Gate: REQUIRE_REVISION" in text
    assert "six_d_brain_review" in text
    assert "pricing_hypothesis_source_audit" in text
    assert "right_to_win_analysis" in text
    assert "Correct path" in text
    assert "Founder AI Workflow Audit" in text


def test_status_answer_still_gets_adaptive_discovery_without_full_strategy_lock(tmp_path):
    text = answer_owner(
        "Aiden，你现在自己是一个什么状态？",
        repo_root=REPO_ROOT,
        memory_path=tmp_path / "memory.json",
    )

    assert "Adaptive Governance Gate:" in text
    assert "repo-grounded CEO meeting layer" in text
    assert "不是完全自治 CEO" in text


def test_aiden_action_context_marks_strategy_questions_as_major():
    context = build_aiden_answer_owner_action_context("最快拿到第一笔钱", "fastest_cash")

    assert context["market_strategy_required"] is True
    assert context["external_observation_required"] is True
    assert context["major_action"] is True


def test_aiden_adaptive_result_returns_navigation_for_missing_capabilities():
    result = build_aiden_adaptive_governance_result("最快拿到第一笔钱", "fastest_cash", "依据: repo evidence")

    missing = set(result["obligation_invocation_proof"]["missing_obligations"])
    assert "six_d_brain_review" in missing
    assert "pricing_hypothesis_source_audit" in missing
    assert result["correct_path_navigator"]["missing_obligation_count"] >= 2
