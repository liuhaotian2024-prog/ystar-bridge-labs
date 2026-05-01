from pathlib import Path

from office.aiden_meeting_room.directive_retriage_analyzer import (
    analyze_directive_tracker,
    grouped_directive_summary,
)
from office.aiden_meeting_room.operations_admin_analyzer import analyze_operations_admin


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_directive_retriage_detects_stale_and_revenue_relevant_tasks():
    findings = analyze_directive_tracker(REPO_ROOT)
    grouped = grouped_directive_summary(findings)
    assert "ARCHIVE_LEGACY" in grouped
    assert "REVENUE_RELEVANT_NOW" in grouped
    assert "OWNER_DECISION_REQUIRED" in grouped


def test_operations_content_calendar_is_admin_or_historical():
    findings = analyze_operations_admin(REPO_ROOT)
    calendar = [finding for finding in findings if "HN" in finding.title or "LinkedIn" in finding.title]
    assert calendar
    assert all(finding.classification in {"historical_or_stale_admin", "stale_admin"} for finding in calendar[:5])


def test_operations_enterprise_sales_needs_owner_decision():
    findings = analyze_operations_admin(REPO_ROOT)
    enterprise = [finding for finding in findings if "Enterprise" in finding.title or "enterprise" in finding.title]
    assert enterprise
    assert any(finding.classification == "owner_decision_required" for finding in enterprise)

