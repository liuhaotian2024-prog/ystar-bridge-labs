from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_implementation_inspection_report_exists_and_mentions_actual_files():
    path = ROOT / "reports" / "integration" / "e5_implementation_inspection.md"
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "office/mission_command/tier1_public_research.py" in text
    assert "office/mission_command/e4_market_evidence_evaluator.py" in text
    assert "controlled_public_page_read_adapter/page_read_adapter.py" in text
    assert "post_push_quality_audit.md" in text
