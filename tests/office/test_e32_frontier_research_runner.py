import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def test_frontier_research_receipts_are_public_readonly():
    run = json.loads((ROOT / "operations/external_validation/e32_frontier_research_run.json").read_text())
    receipts = json.loads((ROOT / "operations/external_validation/e32_frontier_research_receipts.json").read_text())
    assert run["research_status"] == "executed"
    assert receipts["receipt_count"] == run["source_count"]
    assert all(r["evidence_boundary"] == "observed_public_evidence" for r in receipts["receipts"])
    assert all(r["no_external_effect_proof"] is True for r in receipts["receipts"])
