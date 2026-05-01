from pathlib import Path

from office.mission_command.governance_bridge import (
    preflight_admin_rule,
    preflight_mission_action,
    preflight_value_alignment,
    summarize_preflight_results,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
MISSION = {
    "mission_id": "mission_test",
    "owner_goal": "first revenue",
    "allowed_permission_tier": 1,
    "research_budget": {"max_search_queries": 10},
}


def test_governance_bridge_handles_missing_imports_gracefully():
    result = preflight_mission_action({"action": "read-only research"}, MISSION, REPO_ROOT, force_unavailable=True)
    assert result["available"] is False
    assert result["external_action_executed"] is False


def test_governance_bridge_preflights_external_action_as_approval_needed():
    result = preflight_mission_action({"action": "send email to selected customer"}, MISSION, REPO_ROOT)
    assert result["external_action_executed"] is False
    assert result["decision"] == "NEEDS_OWNER_APPROVAL"


def test_governance_bridge_preflights_read_only_as_allowed():
    result = preflight_mission_action({"action": "read-only research public page search"}, MISSION, REPO_ROOT)
    assert result["external_action_executed"] is False
    assert result["decision"] == "ALLOW_INTERNAL"


def test_governance_bridge_admin_and_value_summary():
    results = [
        preflight_admin_rule({"title": "old daily report"}, MISSION, REPO_ROOT),
        preflight_value_alignment({"title": "first paid customer interview"}, REPO_ROOT),
    ]
    summary = summarize_preflight_results(results)
    assert summary["external_action_executed"] is False
    assert summary["core_db_write"] is False
    assert summary["available_count"] >= 1


def test_no_customer_contact_executed():
    result = preflight_mission_action({"action": "contact customer"}, MISSION, REPO_ROOT)
    assert result["external_action_executed"] is False


def test_no_email_executed():
    result = preflight_mission_action({"action": "send email"}, MISSION, REPO_ROOT)
    assert result["external_action_executed"] is False


def test_no_payment_executed():
    result = preflight_mission_action({"action": "process payment"}, MISSION, REPO_ROOT)
    assert result["external_action_executed"] is False
    assert result["decision"] in {"BLOCKED", "REVIEW_GATED", "NEEDS_OWNER_APPROVAL"}


def test_no_publication_executed():
    result = preflight_mission_action({"action": "publish public post"}, MISSION, REPO_ROOT)
    assert result["external_action_executed"] is False
