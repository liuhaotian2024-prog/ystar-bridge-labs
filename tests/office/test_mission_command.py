from pathlib import Path

from office.mission_command.mission_from_owner_message import build_mission_from_owner_message
from office.mission_command.mission_summary import build_mission_result, build_mission_summary
from office.mission_command.team_task_builder import build_team_tasks


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = "Aiden，带团队制定未来 7 天最可能产生第一笔收入的行动方案"


def test_mission_from_owner_message_sets_m3_priority_and_evidence():
    mission = build_mission_from_owner_message(MISSION, REPO_ROOT)
    assert mission.default_priority.startswith("M-3 Value Production")
    assert mission.allowed_permission_tier == 1
    assert mission.evidence_basis
    assert "Founder AI Workflow Audit" in mission.recommended_path


def test_team_task_builder_uses_existing_team_only():
    mission = build_mission_from_owner_message(MISSION, REPO_ROOT)
    tasks = build_team_tasks(mission)
    names = " ".join(task.agent for task in tasks)
    assert "Aiden Liu" in names
    assert "Sofia Blake" in names
    assert "Marco Rivera" in names
    assert "Zara Johnson" in names
    assert "Ethan Wright" in names
    assert "Jinjin / K9 Scout" in names
    assert "COO" not in names


def test_mission_result_contains_policy_and_mcp_preflight():
    result = build_mission_result(MISSION, REPO_ROOT)
    assert result.m_triangle_alignment["primary"] == "M-3 Value Production"
    assert result.ystar_gov_preflight["external_action_executed"] is False
    assert result.gov_mcp_preflight["external_action_executed"] is False
    assert result.gov_mcp_preflight["external_contact"]["decision"] == "NEEDS_OWNER_APPROVAL"
    assert result.gov_mcp_preflight["internal_research"]["decision"] == "ALLOW_INTERNAL"


def test_mission_summary_is_owner_readable_and_safe():
    text = build_mission_summary(MISSION, REPO_ROOT)
    assert "Mission goal:" in text
    assert "Team Task Split" in text
    assert "Approval-Needed Actions" in text
    assert "Y-star-gov Preflight" in text
    assert "gov-mcp Preflight" in text
    assert "no external sending" in text
    assert "COO" not in text

