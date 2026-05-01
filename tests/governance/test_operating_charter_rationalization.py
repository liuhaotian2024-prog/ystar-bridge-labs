from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def test_active_operating_charter_exists_and_keeps_m_triangle():
    text = _read("governance/ACTIVE_OPERATING_CHARTER.md")
    assert "M-1 Survivability" in text
    assert "M-2 Governability" in text
    assert "M-3 Value Production" in text
    assert "External side effects require owner approval" in text


def test_active_charter_archives_admin_cadences_by_default():
    text = _read("governance/ACTIVE_OPERATING_CHARTER.md")
    assert "Daily, weekly, and nightly reports are not active by default" in text
    assert "Old content calendars are historical" in text
    assert "Old enterprise sales plans are historical" in text


def test_agents_points_to_active_charter_and_new_iron_rule_zero():
    text = _read("AGENTS.md")
    assert "governance/ACTIVE_OPERATING_CHARTER.md" in text
    assert "NO UNANALYZED CHOICE DUMPING" in text
    assert "approve / reject / request_revision / hold" in text
    assert "Administrative reporting obligations are active only" in text


def test_operations_marks_legacy_schedules_as_historical():
    text = _read("OPERATIONS.md")
    assert "Current Operations Policy — 2026 Active Runtime" in text
    assert "Historical Daily Schedule" in text
    assert "Historical Weekly Cycle" in text
    assert "Historical LinkedIn Content Strategy" in text
