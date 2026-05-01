from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e6_czl_complete_requires_market_backed_offer_thesis():
    text = (ROOT / "reports" / "integration" / "e6_czl_closure_report.md").read_text(encoding="utf-8")
    assert "status: complete" in text
    assert "full_mission_rt1: 0" in text
    assert "market_backed_offer_thesis_if_claiming_completion: True" in text


def test_e6_czl_blocked_full_rt1_nonzero_when_evidence_insufficient():
    text = (ROOT / "reports" / "integration" / "e6_research_runtime_blocker.md").read_text(encoding="utf-8") if (ROOT / "reports" / "integration" / "e6_research_runtime_blocker.md").exists() else ""
    if text:
        assert "full_mission_rt1: 0" not in text


def test_e6_evidence_bundle_requires_receipt_sources_and_summary_paths():
    text = (ROOT / "reports" / "integration" / "e6_evidence_provenance_report.md").read_text(encoding="utf-8")
    assert "validated_live: True" in text
    assert "market_backing_eligible: True" in text
    assert "Source Summary Paths" in text
    assert "Sources" in text


def test_e6_research_writes_receipt_and_source_summaries_when_sources_exist():
    assert (ROOT / "reports" / "integration" / "e6_tier1_research_budget_receipt.md").exists()
    assert (ROOT / "reports" / "integration" / "e6_external_source_summaries.md").exists()


def test_no_core_db_writeback_obligation_registration_cieu_or_coo():
    text = (ROOT / "reports" / "integration" / "e6_czl_closure_report.md").read_text(encoding="utf-8")
    assert "core DB/brain/memory/CIEU writeback: false" in text
    assert "obligation auto-registration: false" in text
    assert "COO invented: false" in text
