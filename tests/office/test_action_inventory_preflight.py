from pathlib import Path

from office.mission_command.action_inventory import (
    build_action_inventory,
    preflight_action_inventory,
    summarize_action_preflight,
)
from office.mission_command.meta_development_method_kernel import build_meta_development_trace
from office.mission_command.mission_summary import build_mission_result
from office.mission_command.obligation_bridge import build_obligation_draft_from_mission, build_team_obligation_drafts
from office.mission_command.residual_learning_bridge import build_residual_candidates_for_experiments


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = "制定未来 7 天最可能产生第一笔收入的行动方案"


def _rows():
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
    return preflight_action_inventory(actions, mission_dict, REPO_ROOT)


def test_all_proposed_actions_receive_preflight():
    rows = _rows()
    summary = summarize_action_preflight(rows)
    assert rows
    assert summary["all_actions_preflighted"] is True
    assert all(row["preflight_decision"] for row in rows)


def test_external_actions_need_owner_approval():
    rows = _rows()
    external = [row for row in rows if row["structured_action"]["external_side_effect"]]
    assert external
    assert any(row["preflight_decision"] == "NEEDS_OWNER_APPROVAL" for row in external)


def test_core_writeback_review_gated():
    rows = _rows()
    core = [row for row in rows if row["action_class"] == "core_writeback_review_gated"]
    assert core
    assert all(row["preflight_decision"] in {"BLOCKED", "REVIEW_GATED", "NEEDS_OWNER_APPROVAL"} for row in core)


def test_no_external_side_effects():
    assert all(row["external_action_executed"] is False for row in _rows())


def test_no_customer_contact():
    rows = _rows()
    customer = [row for row in rows if "customer" in row["action_title"].lower()]
    assert customer
    assert all(row["external_action_executed"] is False for row in customer)


def test_no_email():
    rows = _rows()
    email = [row for row in rows if "email" in row["action_title"].lower()]
    assert email
    assert all(row["external_action_executed"] is False for row in email)


def test_approval_packet_creation_is_internal_not_external_false_positive():
    rows = _rows()
    matches = [row for row in rows if row["action_title"].startswith("Create approval packet")]
    assert matches
    assert matches[0]["preflight_decision"] == "ALLOW_INTERNAL"
    assert matches[0]["structured_action"]["external_side_effect"] is False


def test_aiden_external_gate_coordination_is_internal():
    rows = _rows()
    matches = [row for row in rows if "keep all external actions approval-gated" in row["action_title"]]
    assert matches
    assert matches[0]["preflight_decision"] == "ALLOW_INTERNAL"


def test_external_pain_residual_candidate_is_review_gated():
    rows = _rows()
    matches = [row for row in rows if "opp_external_pain_agent_bottleneck" in row["action_title"]]
    assert matches
    assert matches[0]["preflight_decision"] == "REVIEW_GATED"
    assert matches[0]["structured_action"]["external_side_effect"] is False
