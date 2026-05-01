from pathlib import Path

from office.mission_command.mission_summary import build_mission_result
from office.mission_command.obligation_bridge import (
    build_obligation_draft_from_mission,
    build_team_obligation_drafts,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = "制定未来 7 天最可能产生第一笔收入的行动方案"


def test_obligation_draft_matches_gov_order_schema():
    result = build_mission_result(MISSION, REPO_ROOT)
    draft = build_obligation_draft_from_mission(result)
    for field in [
        "owner",
        "entity_id",
        "rule_id",
        "rule_name",
        "description",
        "due_secs",
        "severity",
        "required_event",
    ]:
        assert draft[field]
    assert draft["owner"] in {"ceo", "cto", "cmo", "cso", "cfo", "secretary"}
    assert draft["entity_id"].startswith("BOARD-2026-05-01-")
    assert draft["rule_id"].isascii()
    assert draft["required_event"] in {
        "acknowledgement_event",
        "completion_event",
        "result_publication_event",
        "status_update_event",
    }


def test_obligation_draft_does_not_register_automatically():
    result = build_mission_result(MISSION, REPO_ROOT)
    draft = build_obligation_draft_from_mission(result)
    assert draft["owner_review_required"] is True
    assert draft["registration_allowed"] is False
    assert "--dry-run" in draft["registration_command_preview"]


def test_team_obligation_drafts_created_for_team_tasks():
    result = build_mission_result(MISSION, REPO_ROOT)
    drafts = build_team_obligation_drafts(result.team_tasks, result.mission.mission_id)
    assert len(drafts) == len(result.team_tasks)
    assert all(draft["registration_allowed"] is False for draft in drafts)


def test_no_core_db_writeback():
    result = build_mission_result(MISSION, REPO_ROOT)
    drafts = build_team_obligation_drafts(result.team_tasks, result.mission.mission_id)
    assert all("register_obligation" not in draft["registration_command_preview"] for draft in drafts)
