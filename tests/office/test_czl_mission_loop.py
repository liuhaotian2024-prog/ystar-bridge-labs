from pathlib import Path

from office.mission_command.czl_mission_loop import (
    E1_5_Y_STAR,
    build_czl_plan,
    compute_rt1,
    is_czl_complete,
    observe_y_t1,
    record_u_action,
    render_czl_markdown,
)
from office.mission_command.mission_summary import build_mission_result


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = "制定未来 7 天最可能产生第一笔收入的行动方案"


def _complete_evidence():
    return {
        "czl_tuple_present": True,
        "counterfactual_gate_present": True,
        "counterfactual_gate_can_change_or_confirm": True,
        "action_wide_preflight_complete": True,
        "dynamic_obligation_ids_dry_run": True,
        "residual_update_review_gated": True,
        "owner_decision_packet_present": True,
        "plan_u_yt1_rt1_distinguished": True,
        "no_external_side_effects": True,
        "tests_and_unseen_smoke_passed": True,
        "external_research_executed": False,
    }


def test_czl_plan_defines_y_star_xt_u_expected_y_t1():
    result = build_mission_result(MISSION, REPO_ROOT)
    state = build_czl_plan(result, REPO_ROOT)
    assert state.y_star == E1_5_Y_STAR
    assert state.xt_snapshot["repo_root"] == str(REPO_ROOT)
    assert state.u_actions == []
    assert state.rt1_score == len(E1_5_Y_STAR)


def test_czl_rt1_nonzero_when_preflight_missing():
    result = build_mission_result(MISSION, REPO_ROOT)
    state = build_czl_plan(result, REPO_ROOT)
    evidence = _complete_evidence()
    evidence["action_wide_preflight_complete"] = False
    state = compute_rt1(observe_y_t1(state, evidence))
    assert state.rt1_score > 0
    assert any("preflight" in residual.lower() for residual in state.rt1_residuals)


def test_czl_rt1_zero_when_all_y_star_criteria_met():
    result = build_mission_result(MISSION, REPO_ROOT)
    state = build_czl_plan(result, REPO_ROOT)
    state = record_u_action(state, {"action_id": "u_test", "description": "test action"})
    state = compute_rt1(observe_y_t1(state, _complete_evidence()))
    assert state.rt1_score == 0
    assert is_czl_complete(state)


def test_czl_completion_requires_no_residuals():
    result = build_mission_result(MISSION, REPO_ROOT)
    state = compute_rt1(build_czl_plan(result, REPO_ROOT))
    assert not is_czl_complete(state)


def test_reports_contain_czl_tuple():
    result = build_mission_result(MISSION, REPO_ROOT)
    state = build_czl_plan(result, REPO_ROOT)
    text = render_czl_markdown(state)
    assert "Y*" in text
    assert "Xt" in text
    assert "U" in text
    assert "Yt+1" in text
    assert "Rt+1" in text
