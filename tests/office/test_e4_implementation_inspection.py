from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_implementation_inspection_report_exists_and_mentions_actual_files():
    report = ROOT / "reports" / "integration" / "e4_implementation_inspection.md"
    text = report.read_text(encoding="utf-8")
    assert "9390c63638741cac766e0a2fde04b5bafc0a3a90" in text
    assert "office/mission_command/strict_czl.py" in text
    assert "office/mission_command/tier1_research_runtime.py" in text
    assert "reports/integration/post_push_quality_audit.md" in text
    assert "keep untracked" in text
