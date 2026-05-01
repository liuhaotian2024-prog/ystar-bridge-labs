import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _retriage():
    return json.loads((REPO_ROOT / "directive_retriage.json").read_text(encoding="utf-8"))["items"]


def test_directive_retriage_json_has_required_fields():
    item = _retriage()[0]
    for field in (
        "directive_id",
        "task_id",
        "old_status",
        "new_status",
        "reason",
        "recommended_action",
        "m_triangle_alignment",
        "owner_decision_needed",
    ):
        assert field in item


def test_old_content_and_social_cadences_are_archived():
    items = {item["task_id"]: item for item in _retriage()}
    assert items["linkedin_hn_posting_schedules"]["new_status"] == "ARCHIVE_LEGACY"
    assert items["article_series_and_content_calendar"]["new_status"] == "ARCHIVE_LEGACY"


def test_three_repo_integration_is_superseded_by_runtime():
    items = {item["task_id"]: item for item in _retriage()}
    assert items["original_three_repo_backflow"]["new_status"] == "SUPERSEDED_BY_RUNTIME"


def test_directive_tracker_exposes_retriage_layer():
    text = (REPO_ROOT / "DIRECTIVE_TRACKER.md").read_text(encoding="utf-8")
    assert "Directive Re-Triage Status" in text
    assert "ARCHIVE_LEGACY" in text
    assert "OWNER_DECISION_REQUIRED" in text
