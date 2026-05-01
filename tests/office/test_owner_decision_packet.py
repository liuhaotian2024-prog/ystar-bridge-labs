from pathlib import Path

from office.mission_command.action_inventory import (
    build_action_inventory,
    preflight_action_inventory,
    summarize_action_preflight,
)
from office.mission_command.czl_mission_loop import build_czl_plan, compute_rt1, observe_y_t1
from office.mission_command.meta_development_method_kernel import build_meta_development_trace
from office.mission_command.mission_summary import build_mission_result, build_mission_summary
from office.mission_command.obligation_bridge import build_obligation_draft_from_mission, build_team_obligation_drafts
from office.mission_command.owner_decision_packet import build_owner_decision_packet
from office.mission_command.residual_learning_bridge import build_residual_candidates_for_experiments


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = "制定未来 7 天最可能产生第一笔收入的行动方案"


def _packet():
    result = build_mission_result(MISSION, REPO_ROOT)
    trace = build_meta_development_trace(MISSION, REPO_ROOT)
    drafts = [build_obligation_draft_from_mission(result)] + build_team_obligation_drafts(result.team_tasks, result.mission.mission_id)
    residuals = build_residual_candidates_for_experiments(trace["experiments"], trace["counterfactual_cases"], result.mission.mission_id)
    actions = build_action_inventory(result, trace, drafts, residuals)
    mission_dict = {
        "mission_id": result.mission.mission_id,
        "owner_goal": result.mission.goal,
        "allowed_permission_tier": result.mission.allowed_permission_tier,
        "research_budget": result.mission.research_budget,
    }
    preflight = summarize_action_preflight(preflight_action_inventory(actions, mission_dict, REPO_ROOT))
    czl = compute_rt1(observe_y_t1(build_czl_plan(result, REPO_ROOT), {
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
    }))
    return build_owner_decision_packet(result.mission.mission_id, trace["evidence_status"], czl.to_dict(), trace["counterfactual_gate_result"], preflight)


def test_owner_decision_packet_requests_tier1_research_not_customer_contact():
    packet = _packet()
    assert packet["requested_owner_decision"] == "approve_or_revise_tier1_read_only_research"
    assert "does not approve customer contact" in packet["exact_boundary_of_approval"]


def test_owner_decision_packet_has_approve_reject_revision_hold():
    packet = _packet()
    assert packet["options"] == ["approve", "reject", "request_revision", "hold"]


def test_reports_contain_rt1():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Rt+1" in text
    assert "rt1_score" in text


def test_no_payment():
    assert _packet()["external_action_executed"] is False


def test_no_publication():
    assert "publication" in _packet()["exact_boundary_of_approval"]


def test_no_obligation_auto_registration():
    assert "obligation registration" in _packet()["exact_boundary_of_approval"]


def test_no_cieu_write():
    assert "core writeback" in _packet()["exact_boundary_of_approval"]


def test_no_coo_invented():
    assert "COO" not in str(_packet())
