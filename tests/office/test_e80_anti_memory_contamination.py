import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def test_e80_anti_memory_contamination_report_separates_evidence_from_prompt_hints():
    report = _load("operations/external_validation/e80_anti_memory_contamination_report.json")

    assert report["findings_from_raw_file_inventory"]["bridge_labs_tracked_files"] > 10000
    assert report["findings_from_symbol_index"]["python_file_count"] > 1000
    assert report["findings_from_generated_artifact_metadata"]["artifact_count"] > 1000
    assert report["findings_from_tests"]["test_file_count"] > 100
    assert report["actual_capabilities_discovered_not_named_in_prompt_count"] > 0
    assert report["prompt_hinted_capabilities_not_verified_by_repository_evidence_count"] > 0
    assert any(item["concept"] == "production_CIEU_ledger" for item in report["prompt_hinted_capabilities_not_found_or_not_active"])


def test_e80_prior_assumptions_corrected_include_recent_memory_warning():
    report = _load("operations/external_validation/e80_anti_memory_contamination_report.json")

    joined = " ".join(report["prior_assumptions_corrected"])
    assert "does not begin from E65-E79 named memory" in joined
    assert "prompt mentioned it" in joined
