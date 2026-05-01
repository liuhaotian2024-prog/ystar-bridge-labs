from pathlib import Path

from office.aiden_meeting_room.company_context_loader import load_company_context
from office.aiden_meeting_room.repo_evidence_index import build_repo_evidence_index


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_active_operating_charter_exists_and_sets_m3_default():
    charter = REPO_ROOT / "governance" / "ACTIVE_OPERATING_CHARTER.md"
    text = charter.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "M-3 Value Production unless M-1 or M-2 is actively broken" in text
    assert "old daily, weekly, and nightly reports are not active by default" in lowered
    assert "hn and linkedin calendars are historical" in lowered
    assert "never invent a COO" in text


def test_aiden_context_loads_active_operating_charter():
    ctx = load_company_context(REPO_ROOT)
    assert "governance/ACTIVE_OPERATING_CHARTER.md" in ctx.source_texts


def test_evidence_index_includes_active_operating_charter():
    index = build_repo_evidence_index(REPO_ROOT)
    labels = {item.label for item in index.items}
    assert "Active charter default priority" in labels
    assert "Active runtime Mission Command" in labels
    assert "Administrative rationalization" in labels
